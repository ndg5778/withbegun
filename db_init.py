import psycopg2
import bcrypt
import binascii
import json, datetime

with open('./database.json', 'r', encoding='utf-8') as f:
    read_data = f.read()

db_data = json.loads(read_data)

user = db_data.get('user')
password = db_data.get('password')
host = db_data.get('host')
dbname = db_data.get('dbname')
port = db_data.get('port')

psql = None
pc = None

def auth_password_hashing(user_password):
    """
    User password encryption
    @return string(hex)
    """
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
    hex_hashed_password = hashed_password.hex()
    return hex_hashed_password

def password_checking(input_user_password, hex_hashed_password):
    """
    Checking user password
    @return Bool(True/False)
    """
    binary_password = binascii.unhexlify(hex_hashed_password)
    return bcrypt.checkpw(input_user_password.encode('utf-8'), binary_password)


def conn():
    global psql, pc
    try:
        psql = psycopg2.connect(f"""
                dbname={dbname}
                user={user}
                host={host}
                password={password}
                port={port}
        """)
        print("연결 성공")
    except:
        print("Error")
    pc = psql.cursor()

def db_close():
    global psql, pc
    psql.commit()
    pc.close()
    psql.close()
    pc = None
    psql = None

def create_user(user_code, user_password, user_name, user_email, user_grade=9, user_major_code=0):
    if not psql:
        conn()

    hasing_password = auth_password_hashing(user_password)

    pc.execute('''
        INSERT INTO Users(code, password, name, email, grade, major_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, code, name;
    ''', (user_code, hasing_password, user_name, user_email, user_grade, user_major_code))

    value = pc.fetchone()

    db_close()

def get_login_user(std_code, pwd):
    if not psql:
        conn()

    pc.execute(f"""
        SELECT password
        FROM Users
        WHERE code = '{std_code}';
    """)

    value = pc.fetchone()

    if value:
        user_salt_password = value[0]
        is_user = password_checking(pwd, user_salt_password)
        if is_user:
            return value
    return False

def get_simple_data_user(std_code):
    if not psql:
        conn()
    
    pc.execute(f"""
        SELECT id, name
        FROM Users
        WHERE code = '{std_code}';
    """)

    value = pc.fetchone()
    return value

def get_product_categories():
    if not psql:
        conn()

    pc.execute(f"""
        SELECT id, category
        FROM ProductCategories;
    """)

    values = pc.fetchall()
    return values

def get_products(category='0'):
    if not psql:
        conn()

    if category == '0':
        pc.execute(f"""
            SELECT  p.id, u.name, c.category, p.title, p.price, i.img_link1, p.created_at
            FROM Products as p
            LEFT OUTER JOIN ProductImages as i
            ON i.product_id = p.id
            INNER JOIN ProductCategories as c
            ON p.category_id = c.id
            INNER JOIN Users as u
            ON p.user_id = u.id
            WHERE p.status_id = 1
            ORDER BY p.created_at DESC;
        """)
    else:
        pc.execute(f"""
            SELECT  p.id, u.name, c.category, p.title, p.price, i.img_link1, p.created_at
            FROM Products as p
            LEFT OUTER JOIN ProductImages as i
            ON i.product_id = p.id
            INNER JOIN ProductCategories as c
            ON p.category_id = c.id
            INNER JOIN Users as u
            ON p.user_id = u.id
            WHERE p.category_id = '{category}' and p.status_id = 1
            ORDER BY p.created_at DESC;
        """)
    
    values = pc.fetchall()
    return values

def set_product(user_id, product_data, img_list):
    if not psql:
        conn()

    category_id = product_data.get('category')
    title = product_data.get('title')
    content = product_data.get('content')
    price = product_data.get('price')


    pc.execute(f"""
        INSERT INTO Products(category_id, user_id, title, content, price)
        VALUES ('{category_id}', '{user_id}', '{title}', '{content}', '{price}')
        RETURNING id;
    """)
    value = pc.fetchone()
    product_id = value[0]

    img_link_list = ['', '', '', '', '']
    img_hashdelete_list = ['', '', '', '', '']
    cnt = len(img_list)
    for idx in range(cnt):
        img_link_list[idx] = img_list[idx][0]
        img_hashdelete_list[idx] = img_list[idx][1]

    pc.execute(f"""
        INSERT INTO ProductImages(product_id, cnt, img_link1, img_hashdelete1, img_link2, img_hashdelete2, img_link3, img_hashdelete3, img_link4, img_hashdelete4, img_link5, img_hashdelete5)
        VALUES ('{product_id}', '{cnt}', '{img_link_list[0]}', '{img_hashdelete_list[0]}', '{img_link_list[1]}', '{img_hashdelete_list[1]}', '{img_link_list[2]}', '{img_hashdelete_list[2]}', '{img_link_list[3]}', '{img_hashdelete_list[3]}', '{img_link_list[4]}', '{img_hashdelete_list[4]}');
    """)

    db_close()

def get_product(product_id):
    if not psql:
        conn()
    
    pc.execute(f"""
        SELECT p.id, c.category, u.id, u.name, p.title, p.content, p.price, s.status,
            i.cnt, i.img_link1, i.img_link2, i.img_link3, i.img_link4, i.img_link5, p.created_at, count(v.user_id)
        FROM Products as p
        LEFT OUTER JOIN ProductImages as i
        ON p.id = i.product_id
        INNER JOIN ProductCategories as c
        ON p.category_id = c.id
        INNER JOIN Users as u
        ON p.user_id = u.id
        INNER JOIN ProductStatus as s
        ON p.status_id = s.id
        INNER JOIN ProductViews as v
        ON p.id = v.product_id
        WHERE p.id = '{product_id}'
        GROUP BY p.id, c.category, u.id, u.name, p.title, p.content, p.price, s.status,
            i.cnt, i.img_link1, i.img_link2, i.img_link3, i.img_link4, i.img_link5, p.created_at;
    """)

    value = pc.fetchone()
    return value

def set_product_view(product_id, user_id):
    if not psql:
        conn()
    
    pc.execute(f"""
        SELECT v.user_id
        FROM Products as p
        INNER JOIN ProductViews as v
        ON p.id = v.product_id
        WHERE v.user_id = '{user_id}' and v.product_id = '{product_id}';
    """)

    value = pc.fetchone()

    if value == None:
        pc.execute(f"""
            INSERT INTO ProductViews(product_id, user_id)
            VALUES ('{product_id}', '{user_id}');
        """)

    db_close()


def get_buses():
    if not psql:
        conn()
    
    pc.execute(f"""
        SELECT seat
        FROM Buses;
    """)

    values = pc.fetchall()
    return values

def set_bus_reservation(user_id, seat):
    if not psql:
        conn()

    pc.execute(f"""
        INSERT INTO Buses(user_id, seat)
        VALUES ('{user_id}', '{seat+1}');
    """)

    db_close()

def get_bus_reservation(user_id):
    if not psql:
        conn()

    pc.execute(f"""
        SELECT seat
        FROM Buses
        WHERE user_id = {user_id};
    """)

    value = pc.fetchone()
    return value

def delete_bus_reservation(user_id):
    if not psql:
        conn()

    pc.execute(f"""
        DELETE FROM Buses
        WHERE user_id = {user_id};
    """)

    db_close()

def get_places():
    if not psql:
        conn()
    
    pc.execute(f"""
        SELECT p.id, (SELECT category
                    FROM PlaceCategories as pc
                    WHERE p.category_id = pc.id),
            p.name, p.address, p.url, p.loc_x, p.loc_y, p.tel
        FROM Places as p;
    """)

    value = pc.fetchall()
    return value
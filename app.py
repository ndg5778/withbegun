from flask import Flask, request, render_template, session, redirect, url_for
import json, datetime, base64
import requests
import db_init

app = Flask(__name__)
app.secret_key = 'guide'

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_code = request.form.get('user-code')
        user_pwd = request.form.get('user-password')
        result = db_init.get_login_user(user_code, user_pwd)
        if result:
            session['user_code'] = user_code
            user_data = db_init.get_simple_data_user(user_code)
            session['user_id'] = user_data[0]
            session['user_name'] = user_data[1]
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
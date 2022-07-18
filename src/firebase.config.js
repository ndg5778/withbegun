import { getApp, getApps, initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyA2mwRLY2bfJOLT0NTH9z-LD_EHiEiMubc",
  authDomain: "restaurantapp-a7c97.firebaseapp.com",
  databaseURL: "https://restaurantapp-a7c97-default-rtdb.firebaseio.com",
  projectId: "restaurantapp-a7c97",
  storageBucket: "restaurantapp-a7c97.appspot.com",
  messagingSenderId: "188944903488",
  appId: "1:188944903488:web:422a8c016467f4333d9ea5"
};

const app = getApps.length > 0 ? getApp() : initializeApp(firebaseConfig);

const firestore = getFirestore(app);
const storage = getStorage(app);

export { app, firestore, storage };
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBPCmpqVsdwD98g4T9_SucRPDe1lo_Th6U",
    "authDomain": "classroomai-ed428.firebaseapp.com",
    "projectId": "classroomai-ed428",
    "storageBucket": "classroomai-ed428.appspot.com",
    "messagingSenderId": "478901054017",
    "appId": "1:478901054017:web:677a05263a54639ab234c0",
    "databaseURL": "https://classroomai-ed428-default-rtdb.firebaseio.com/"
}



firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()
db = firebase.database()
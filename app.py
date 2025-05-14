from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from chatbot_model import predict_intent
import firebase_admin
from firebase_admin import credentials, db
import json
import os

app = Flask(__name__)
app.secret_key = '1816'  # 🔒 Replace with a secure value in production

# ✅ Firebase initialization using environment variable
firebase_json = os.getenv("FIREBASE_CREDENTIALS")

if firebase_json:
    try:
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://collegechatbotdb-default-rtdb.firebaseio.com/'
        })
    except Exception as e:
        print(f"Firebase initialization error: {e}")
else:
    print("Firebase credentials not found in environment variables.")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['message']
    response = predict_intent(user_input)

    # ✅ Store conversation in Firebase if available
    try:
        ref = db.reference('chats')
        ref.push({"user": user_input, "bot": response})
    except Exception as e:
        print(f"Error storing chat in Firebase: {e}")

    return jsonify({'response': response})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 🔒 Replace with secure database or Firebase auth
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect('/admin')
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

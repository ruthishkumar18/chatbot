from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from chatbot_model import predict_intent
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)
app.secret_key = '1816'  # Change this to a secure key in production

# Try Firebase initialization
firebase_initialized = False
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://collegechatbotdb-default-rtdb.firebaseio.com/'
        })
        firebase_initialized = True
except Exception as e:
    print(f"[WARNING] Firebase not initialized: {e}")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['message']
    response = predict_intent(user_input)

    # Store conversation if Firebase is ready
    if firebase_initialized:
        try:
            ref = db.reference('chats')
            ref.push({"user": user_input, "bot": response})
        except Exception as e:
            print(f"[ERROR] Failed to store chat: {e}")

    return jsonify({'response': response})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect('/admin')
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    chats = []
    if firebase_initialized:
        try:
            ref = db.reference('chats')
            chats = ref.get()
        except Exception as e:
            print(f"[ERROR] Failed to fetch chats: {e}")

    return render_template('admin.html', chats=chats)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ✅ Route to collect user feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    name = request.form.get("name")
    message = request.form.get("message")

    if firebase_initialized:
        try:
            ref = db.reference('feedback')
            ref.push({"name": name, "message": message})
        except Exception as e:
            print(f"[ERROR] Feedback store failed: {e}")

    return redirect('/')

from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from chatbot_model import predict_intent
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = '1816'  # 🔒 Change this in production

# Firebase initialization (optional, for chat storage)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://collegechatbotdb-default-rtdb.firebaseio.com/'
})

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['message']
    response = predict_intent(user_input)

    # Optional: store conversation in Firebase
    ref = db.reference('chats')
    ref.push({"user": user_input, "bot": response})

    return jsonify({'response': response})

@app.route('/get_chats')
def get_chats():
    ref = db.reference('chats')
    chats = ref.get()
    return jsonify({'chats': chats})

# ✅ LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect('/admin')
        else:
            return "Invalid credentials"
    return render_template("login.html")

# ✅ ADMIN DASHBOARD
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    return render_template('admin.html')

# ✅ LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ✅ FEEDBACK ROUTE
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form['feedback']
    ref = db.reference('feedback')
    ref.push({"feedback": feedback})
    return 'Feedback submitted successfully!'

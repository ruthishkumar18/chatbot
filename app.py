import firebase_admin
from firebase_admin import credentials, db

from flask import Flask, render_template, request, jsonify
from chatbot_model import predict_intent

app = Flask(__name__)

# 🔑 Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://collegechatbotdb-default-rtdb.firebaseio.com'  # 🔁 Replace with your actual project ID
})

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.json['message']  # Use .json if sending JSON via JS/AJAX
    response = predict_intent(user_input)

    # 🔄 Save conversation to Firebase
    ref = db.reference('chats')
    ref.push({
        'user': user_input,
        'bot': response
    })

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

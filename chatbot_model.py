import json
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

with open("intents.json") as file:
    data = json.load(file)

vectorizer = CountVectorizer()
all_patterns = []
all_tags = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        all_patterns.append(pattern)
        all_tags.append(intent["tag"])

X = vectorizer.fit_transform(all_patterns)
model = LogisticRegression()
model.fit(X, all_tags)

def predict_intent(user_input):
    input_vector = vectorizer.transform([user_input])
    tag = model.predict(input_vector)[0]
    for intent in data["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

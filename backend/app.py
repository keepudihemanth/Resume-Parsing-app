from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import pickle
import numpy as np
from pdfminer.high_level import extract_text
import spacy
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Init
app = Flask(__name__)
CORS(app)

# Load resources
nlp = spacy.load("en_core_web_sm")
model = load_model("resume_model.h5")
with open("tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)
SKILL_SET = set(["python", "java", "c++", "javascript", "html", "css", "sql", "excel", "powerpoint", "communication", "teamwork", "leadership"])

# Utils
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "N/A"

def extract_email(text):
    matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return matches[0] if matches else "N/A"

def extract_phone(text):
    phone_pattern = r'(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    matches = re.findall(phone_pattern, text)
    return re.sub(r'[^\d+]', '', matches[0]) if matches else "N/A"

def extract_skills(text):
    words = set(re.findall(r'\b\w+\b', text.lower()))
    return list(SKILL_SET.intersection(words))

# API Route
@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = clean_text(extract_text(file.stream))
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=200)
    prediction = model.predict(padded)[0][0]
    result = "Accepted" if prediction >= 0.5 else "Rejected"

    return jsonify({
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "prediction": result
    })

if __name__ == '__main__':
    app.run(debug=True)

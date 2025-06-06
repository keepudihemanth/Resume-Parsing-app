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
SKILL_SET = set(['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit', 'react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy', 'ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode', 'ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience', 'aws', 'google cloud platform', 'microsoft azure', 'docker', 'kubernetes', 'jenkins', 'github actions', 'terraform', 'ci/cd', 'ansible', 'apache spark', 'apache kafka', 'hadoop', 'airflow', 'snowflake', 'etl', 'dbt', 'pandas', 'numpy', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'firebase', 'cassandra', 'elasticsearch', 'next.js', 'vue.js', 'svelte', 'tailwind css', 'bootstrap', 'rest api', 'graphql', 'websockets', 'typescript', 'go', 'rust', 'scala', 'ruby', 'bash', 'matlab', 'opencv', 'transformers', 'hugging face', 'nltk', 'spacy', 'scikit-learn', 'langchain', 'llm', 'generative ai', 'chatgpt', 'prompt engineering', 'owasp', 'penetration testing', 'burp suite', 'wireshark', 'ethical hacking', 'kali linux', 'selenium', 'junit', 'cypress', 'postman', 'testng', 'appium', 'jira', 'trello', 'asana', 'notion', 'confluence', 'slack', 'agile', 'scrum', 'blender', 'canva', 'sketch', 'invision'])
ROLE_SKILL_MAP = {
    "Data Scientist": {"pandas", "numpy", "scikit-learn", "tensorflow", "keras", "pytorch", "machine learning", "deep learning", "matplotlib"},
    "Backend Developer": {"django", "flask", "node js", "php", "laravel", "express", "mongodb", "mysql", "postgresql", "graphql"},
    "Frontend Developer": {"react", "react js", "angular js", "vue.js", "svelte", "html", "css", "javascript", "tailwind css", "bootstrap"},
    "DevOps Engineer": {"docker", "kubernetes", "jenkins", "github actions", "terraform", "aws", "azure", "gcp", "ci/cd", "ansible"},
    "Mobile Developer": {"flutter", "kotlin", "android", "ios", "swift", "xcode", "android development", "ios development"},
    "UI/UX Designer": {"figma", "adobe xd", "wireframes", "prototyping", "user experience", "sketch", "invision"},
    "Security Engineer": {"penetration testing", "owasp", "burp suite", "wireshark", "ethical hacking", "kali linux"},
    "Tester / QA Engineer": {"selenium", "junit", "cypress", "testng", "appium", "postman"}
}

# Utils
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            print(f"Detected name entity: {ent.text}, Start: {ent.start_char}, End: {ent.end_char}")
            return ent.text
    return "N/A"

def extract_email(text):
    matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return matches[0] if matches else "N/A"

def extract_phone(text):
    phone_pattern = re.compile(r'''
        (?:(?:\+|00)?\s*\d{1,3})?       # Optional country code with '+' or '00', followed by 1-3 digits
        [\s\-\.()]*
        (?:\d{2,4})                     # Area code or part of number (2 to 4 digits)
        [\s\-\.()]*
        (?:\d{2,4})                     # Mid part
        [\s\-\.()]*
        (?:\d{3,4})                     # Last part
    ''', re.VERBOSE)
    matches = re.findall(phone_pattern, text)
    return re.sub(r'[^\d+]', '', matches[0]) if matches else "N/A"

def extract_skills(text):
    words = set(re.findall(r'\b\w+\b', text.lower()))
    return list(SKILL_SET.intersection(words))

def predict_role(skills):
    role_scores = {}
    for role, required_skills in ROLE_SKILL_MAP.items():
        score = len(set(skills) & required_skills)
        if score > 0:
            role_scores[role] = score
    return max(role_scores, key=role_scores.get) if role_scores else "N/A"


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

    skills = extract_skills(text)
    role = predict_role(skills)

    return jsonify({
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": skills,
        "predicted_role": role,
        "prediction": result
    })

if __name__ == '__main__':
    app.run(debug=True)

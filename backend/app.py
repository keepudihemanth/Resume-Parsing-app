from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import pickle
import numpy as np
from pdfminer.high_level import extract_text
import spacy
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Setup fLask
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Load resources
nlp = spacy.load("en_core_web_sm")
model = load_model("resume_model_balanced.h5")
with open("tokenizer_balanced.pickle", "rb") as f:
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


def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_name(text):
    name_regex = re.search(r"(?:Name|Candidate)[:\-\s]*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", text[:300], re.IGNORECASE)
    if name_regex:
        name = name_regex.group(1).strip()
        if name.lower() not in ["email", "contact", "phone"]:
            logging.info(f"[Regex] Detected name: {name}")
            return name

    doc = nlp(text[:500])
    candidates = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    for name in candidates:
        if name.lower() not in ["email", "contact", "phone", "resume"]:
            logging.info(f"[NER] Detected name entity: {name}")
            return name

    return "N/A"

def extract_email(text):
    matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return matches[0] if matches else "N/A"

def extract_phone(text):
    matches = re.findall(r'(\+?\d[\d\s\-()]{7,}\d)', text)
    return re.sub(r'[^\d+]', '', matches[0]) if matches else "N/A"

def extract_skills(text):
    doc = nlp(text.lower())

    candidates = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        if phrase in SKILL_SET:
            candidates.add(phrase)

    for token in doc:
        if token.is_alpha and not token.is_stop:
            lemma = token.lemma_.lower()
            if lemma in SKILL_SET:
                candidates.add(lemma)

    logging.info(f"[SKILLS] Extracted: {sorted(candidates)}")
    return sorted(candidates)


def predict_role(skills):
    role_scores = {}

    for role, required_skills in ROLE_SKILL_MAP.items():
        match_count = len(set(skills) & required_skills)
        if match_count > 0:
            normalized_score = match_count / len(required_skills)
            role_scores[role] = normalized_score

    if role_scores:
        best_role = max(role_scores, key=role_scores.get)
        logging.info(f"[ROLE] Predicted: {best_role} (score: {role_scores[best_role]:.2f})")
        return best_role
    else:
        return "N/A"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200
@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
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
            "prediction": result,
            "confidence": float(prediction)
        })

    except Exception as e:
        logging.error(f"Error processing resume: {e}")
        return jsonify({"error": "Failed to process resume"}), 500

if __name__ == '__main__':
    app.run(debug=True)

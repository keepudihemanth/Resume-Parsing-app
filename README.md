# Resume-Parsing-app

A web application that extracts and classifies information from resumes such as name, email, phone number, and skills using machine learning and natural language processing.

---

## Features

- Upload resumes in PDF format
- Extract key personal details (Name, Email, Phone Number)
- Parse and extract skills and other relevant information
- Classify resumes based on extracted data
- User-friendly interface for easy resume submission and results viewing

---

## Technologies Used

- Python 3.x
- Flask (Backend API)
- React.js (Frontend UI)
- TensorFlow / spaCy (Machine Learning & NLP models)
- PyPDF2 / pdfminer (PDF parsing)
- REST API for communication between frontend and backend

---

## Project Structure

Resume-Parsing-app/
│
├── backend/ # Flask backend code
│ ├── app.py # Main Flask application
│ ├── model/ # ML models and parsing scripts
│ └── requirements.txt # Backend dependencies
│
├── resume-praser-app/ # React frontend application
│ ├── public/
│ ├── src/
│ ├── package.json
│ └── README.md
│
└── README.md # This file


---

## Installation and Setup

### Backend

1. Clone the repository:

   ```bash
   git clone https://github.com/keepudihemanth/Resume-Parsing-app.git
   cd Resume-Parsing-app/backend

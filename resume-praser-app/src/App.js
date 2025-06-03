import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activePage, setActivePage] = useState('home');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null); // Clear previous result on new file selection
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error('Upload error:', error);
      setResult({ error: 'Failed to upload or process resume.' });
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="app-container">
    <header className="navbar">
      <div className="nav-logo">Resume Parser</div>
      <div className="nav-links">
        <button
          className={`nav-button ${activePage === 'home' ? 'active' : ''}`}
          onClick={() => setActivePage('home')}
        >
          Home
        </button>
        <button
          className={`nav-button ${activePage === 'about' ? 'active' : ''}`}
          onClick={() => setActivePage('about')}
        >
          About
        </button>
      </div>
    </header>

    {activePage === 'home' && (
      <main className="container">
        <h1>Upload a Resume (PDF)</h1>
        <div className="upload-box">
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button onClick={handleUpload} disabled={loading || !file}>
            {loading ? 'Processing...' : 'Upload'}
          </button>
          {file && <div className="filename">{file.name}</div>}
        </div>

        {loading && <div className="loader">⏳ Processing resume...</div>}

        {result && (
          <div className="result-box">
            {result.error ? (
              <p className="error">{result.error}</p>
            ) : (
              <>
                <h2 className="prediction">Prediction: {result.prediction}</h2>
                <div className="result-field"><strong>Name:</strong> {result.name}</div>
                <div className="result-field"><strong>Email:</strong> {result.email}</div>
                <div className="result-field"><strong>Phone:</strong> {result.phone}</div>
                <div className="result-field"><strong>Skills:</strong> {result.skills.join(', ')}</div>
                <div className="result-field"><strong>Predicted Role:</strong> {result.predicted_role}</div>
              </>
            )}
          </div>
        )}
      </main>
    )}

    {activePage === 'about' && (
      <div className="about-page">
        <h1>About Resume Parser</h1>
        <p>
          <strong>Resume Parser</strong> is a smart web application that leverages machine learning and natural language processing (NLP) to automate the analysis of resumes. It is built to assist HR teams, recruiters, and job platforms in interpreting and categorizing resumes efficiently.
        </p>

        <h2>🚀 Key Features</h2>
        <ul>
          <li>PDF Upload & Parsing</li>
          <li>Candidate Information Extraction (Name, Email, Phone, Skills)</li>
          <li>Automatic Role Prediction using a trained ML model</li>
          <li>User-Friendly Interface with real-time results</li>
        </ul>

        <h2>🧠 How It Works</h2>
        <ol>
          <li>Upload a PDF resume via the Home page</li>
          <li>The backend extracts and processes the content</li>
          <li>NLP and ML models classify and extract key information</li>
          <li>Predicted role and extracted details are displayed</li>
        </ol>

        <h2>🛠️ Technologies Used</h2>
        <ul>
          <li><strong>Frontend:</strong> React (JavaScript, JSX)</li>
          <li><strong>Backend:</strong> Flask (Python)</li>
          <li><strong>PDF Parsing:</strong> PyMuPDF, pdfminer</li>
          <li><strong>ML/NLP:</strong> Scikit-learn, SpaCy/NLTK</li>
        </ul>

        <h2>📌 Use Cases</h2>
        <ul>
          <li>Resume shortlisting in recruitment systems</li>
          <li>Job portal resume classification</li>
          <li>Automated HR workflows</li>
          <li>Educational demos for ML/NLP applications</li>
        </ul>
      </div>
    )}

    <footer className="footer">
      &copy; {new Date().getFullYear()} Resume Parser App | All rights reserved
    </footer>
  </div>
);
}

export default App;

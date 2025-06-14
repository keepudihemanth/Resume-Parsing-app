import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activePage, setActivePage] = useState('home');
  const [backendStatus, setBackendStatus] = useState('Checking...');

 
  useEffect(() => {
    fetch('http://localhost:5000/health')
      .then(res => res.json())
      .then(data => setBackendStatus('✅ Running'))
      .catch(() => setBackendStatus('❌ Offline'));
  }, []);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type !== 'application/pdf') {
      setResult({ error: 'Only PDF files are supported.' });
      setFile(null);
    } else {
      setFile(selected);
      setResult(null);
    }
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
        <div className="status">Backend: {backendStatus}</div>
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
                  <div className="result-field"><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</div>
                  <div className="result-field"><strong>Name:</strong> {result.name}</div>
                  <div className="result-field"><strong>Email:</strong> {result.email}</div>
                  <div className="result-field"><strong>Phone:</strong> {result.phone}</div>
                  <div className="result-field"><strong>Skills:</strong> {result.skills?.join(', ') || 'None found'}</div>
                  <div className="result-field"><strong>Predicted Role:</strong> {result.predicted_role}</div>
                </>
              )}
            </div>
          )}
        </main>
      )}

      {activePage === 'about' && (
  <div className="about-container fade-in">
    <h1 className="slide-up">About Resume Parser</h1>
    <p className="fade-in delay-1">
      <strong>Resume Parser</strong> is a smart web application that leverages 
      <strong> Machine Learning</strong> and 
      <strong> Natural Language Processing (NLP)</strong> to automate resume analysis.
    </p>
    <h2 className="slide-up delay-2"> Key Features</h2>
    <ul className="fade-in delay-2">
      <li>PDF Upload & Parsing</li>
      <li>Candidate Info Extraction (Name, Email, Phone, Skills)</li>
      <li>Automatic Role Prediction using ML</li>
      <li>Real-time confidence scoring</li>
    </ul>
    <h2 className="slide-up delay-3"> How It Works</h2>
    <ol className="fade-in delay-3">
      <li>Upload a resume via the home page</li>
      <li>Backend extracts and classifies the content</li>
      <li>NLP + ML predict the applicant’s role</li>
      <li>Information + confidence displayed instantly</li>
    </ol>
    <h2 className="slide-up delay-4"> Tech Stack</h2>
    <ul className="fade-in delay-4">
      <li><strong>Frontend:</strong> React</li>
      <li><strong>Backend:</strong> Flask</li>
      <li><strong>Parsing:</strong> PDFMiner</li>
      <li><strong>ML:</strong> TensorFlow, SpaCy</li>
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

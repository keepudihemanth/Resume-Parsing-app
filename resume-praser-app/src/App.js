import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
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
        <div className="nav-logo">Resume Classifier</div>
        <div className="nav-links">
          <a href="#">Home</a>
          <a href="#">About</a>
        </div>
      </header>

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

      <footer className="footer">
        &copy; {new Date().getFullYear()} Resume Classifier App | All rights reserved
      </footer>
    </div>
  );
}

export default App;

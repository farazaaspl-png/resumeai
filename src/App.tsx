import { useState } from 'react';
import './App.css'

function App() {
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResume(e.target.files[0]);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!resume) {
      setError('Please upload a resume');
      return;
    }
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('jobDescription', jobDescription);

      const response = await fetch('http://localhost:8000/analyse', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze resume');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 40, fontFamily: "sans-serif", maxWidth: 800, margin: '0 auto' }}>
      <h1>Resume Analyzer 📄</h1>
      
      <div style={{ marginBottom: 20 }}>
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold' }}>
          Upload Resume:
        </label>
        <input 
          type="file" 
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          style={{ padding: 8 }}
        />
        {resume && <p style={{ marginTop: 8, color: '#666' }}>Selected: {resume.name}</p>}
      </div>

      <div style={{ marginBottom: 20 }}>
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold' }}>
          Job Description:
        </label>
        <textarea 
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here..."
          rows={8}
          style={{ 
            width: '100%', 
            padding: 12, 
            fontSize: 14,
            borderRadius: 4,
            border: '1px solid #ccc'
          }}
        />
      </div>

      <button 
        onClick={handleAnalyze}
        disabled={loading}
        style={{ 
          padding: '12px 24px', 
          fontSize: 16,
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: 4,
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Resume'}
      </button>

      {error && (
        <div style={{ 
          marginTop: 20, 
          padding: 12, 
          backgroundColor: '#fee', 
          color: '#c00',
          borderRadius: 4 
        }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ 
          marginTop: 20, 
          padding: 20, 
          backgroundColor: '#f0f0f0',
          borderRadius: 4 
        }}>
          <h2>Analysis Result:</h2>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App

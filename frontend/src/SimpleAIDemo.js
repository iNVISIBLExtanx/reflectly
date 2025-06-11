import React, { useState, useEffect } from 'react';

const SimpleAIDemo = () => {
  const [emotions, setEmotions] = useState([]);
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [pathResult, setPathResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testText, setTestText] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Use relative URLs - React proxy will forward to backend
  const API_BASE = '/api';

  // Emotion colors for visualization
  const emotionColors = {
    joy: '#FFD700',
    sadness: '#4169E1',
    anger: '#DC143C',
    fear: '#9932CC',
    disgust: '#228B22',
    surprise: '#FF69B4',
    neutral: '#808080'
  };

  useEffect(() => {
    checkBackendStatus();
    loadEmotions();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (response.ok) {
        const data = await response.json();
        setBackendStatus('connected');
        console.log('✅ Backend connected:', data);
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('error');
      console.error('❌ Backend connection failed:', error);
    }
  };

  const loadEmotions = async () => {
    try {
      const response = await fetch(`${API_BASE}/emotions/available`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setEmotions(data.emotions);
      if (data.emotions.length > 0) {
        setCurrentEmotion(data.emotions[0]);
        setTargetEmotion('joy');
      }
    } catch (error) {
      console.error('Error loading emotions:', error);
      setBackendStatus('error');
    }
  };

  const analyzeText = async () => {
    if (!testText.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: testText,
          user_email: 'demo@example.com'
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setAnalysisResult(data);
      setCurrentEmotion(data.primary_emotion);
      console.log('✅ Emotion analysis result:', data);
    } catch (error) {
      console.error('Error analyzing text:', error);
      alert('Failed to analyze text. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const findPath = async () => {
    if (!currentEmotion || !targetEmotion) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_emotion: currentEmotion,
          target_emotion: targetEmotion
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setPathResult(data);
      console.log('✅ Path finding result:', data);
    } catch (error) {
      console.error('Error finding path:', error);
      alert('Failed to find path. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const getSuggestions = async () => {
    if (!currentEmotion) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_emotion: currentEmotion })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error getting suggestions:', error);
      alert('Failed to get suggestions. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const testAlgorithm = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/test-algorithm`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      alert('Algorithm test results logged to console. Check browser console for details!');
      console.log('🧪 Algorithm Test Results:');
      console.table(data.algorithm_tests);
      console.log('📊 Summary:', {
        'Total Tests': data.total_tests,
        'Algorithm': data.algorithm,
        'Average Success Rate': (data.average_success_rate * 100).toFixed(1) + '%'
      });
    } catch (error) {
      console.error('Error testing algorithm:', error);
      alert('Failed to test algorithm. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const renderEmotionCircle = (emotion, isSelected = false, isTarget = false) => (
    <div
      key={emotion}
      style={{
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        backgroundColor: emotionColors[emotion] || '#ccc',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '5px',
        border: isSelected ? '3px solid black' : isTarget ? '3px solid orange' : '1px solid #ccc',
        fontSize: '12px',
        fontWeight: isSelected || isTarget ? 'bold' : 'normal',
        cursor: 'pointer',
        textAlign: 'center',
        position: 'relative'
      }}
      onClick={() => {
        if (isTarget) {
          setTargetEmotion(emotion);
        } else {
          setCurrentEmotion(emotion);
        }
      }}
    >
      {emotion}
      {isSelected && <div style={{fontSize: '8px', position: 'absolute', top: '70px'}}>CURRENT</div>}
      {isTarget && <div style={{fontSize: '8px', position: 'absolute', top: '70px'}}>TARGET</div>}
    </div>
  );

  const renderPath = () => {
    if (!pathResult || !pathResult.path) return null;
    
    return (
      <div style={{margin: '20px 0'}}>
        <h3>🎯 Optimal Path Found!</h3>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '10px 0', flexWrap: 'wrap'}}>
          {pathResult.path.map((emotion, index) => (
            <React.Fragment key={index}>
              {renderEmotionCircle(emotion, emotion === currentEmotion, emotion === targetEmotion)}
              {index < pathResult.path.length - 1 && (
                <div style={{margin: '0 10px', fontSize: '20px'}}>→</div>
              )}
            </React.Fragment>
          ))}
        </div>
        <div style={{textAlign: 'center', marginTop: '15px'}}>
          <p><strong>Success Rate:</strong> {(pathResult.estimated_success_rate * 100).toFixed(1)}%</p>
          <p><strong>Total Cost:</strong> {pathResult.total_cost?.toFixed(2)}</p>
        </div>
        
        {pathResult.actions && pathResult.actions.length > 0 && (
          <div style={{marginTop: '20px'}}>
            <h4>📋 Step-by-Step Actions:</h4>
            {pathResult.actions.map((action, index) => (
              <div key={index} style={{
                background: '#f0f8ff',
                padding: '10px',
                margin: '5px 0',
                borderRadius: '5px',
                borderLeft: '4px solid #4169E1'
              }}>
                <div style={{fontWeight: 'bold'}}>{action.from} → {action.to}</div>
                <div>{action.action}</div>
                <div style={{fontSize: '12px', color: '#666'}}>
                  Success Rate: {(action.success_rate * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderBackendStatus = () => {
    const statusInfo = {
      checking: { color: '#ffc107', text: 'Checking backend...', icon: '🔍' },
      connected: { color: '#28a745', text: 'Backend connected', icon: '✅' },
      error: { color: '#dc3545', text: 'Backend not connected', icon: '❌' }
    };

    const status = statusInfo[backendStatus] || statusInfo.error;

    return (
      <div style={{
        background: status.color,
        color: 'white',
        padding: '8px 15px',
        borderRadius: '5px',
        margin: '10px 0',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: 'bold'
      }}>
        {status.icon} {status.text}
        {backendStatus === 'error' && (
          <div style={{fontSize: '12px', marginTop: '5px', fontWeight: 'normal'}}>
            Make sure to run: ./start-backend.sh
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{padding: '20px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'Arial, sans-serif'}}>
      <h1 style={{textAlign: 'center', color: '#333'}}>
        🧠 Simple AI Emotional Pathfinding Demo
      </h1>
      <p style={{textAlign: 'center', color: '#666', marginBottom: '20px'}}>
        Algorithm Development Focus - No Docker, No Database, Pure Python + React
      </p>

      {renderBackendStatus()}

      {/* Text Analysis Section */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>📝 1. Analyze Text Emotion</h2>
        <div style={{display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap'}}>
          <input
            type="text"
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            placeholder="Enter text to analyze emotion (e.g., 'I feel really excited about this!')"
            style={{
              flex: 1,
              minWidth: '300px',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '5px',
              fontSize: '14px'
            }}
          />
          <button
            onClick={analyzeText}
            disabled={loading || !testText.trim() || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        
        {analysisResult && (
          <div style={{background: '#e8f5e8', padding: '15px', borderRadius: '5px', marginTop: '10px'}}>
            <h4>Analysis Result:</h4>
            <p><strong>Primary Emotion:</strong> {analysisResult.primary_emotion}</p>
            <p><strong>Confidence:</strong> {(analysisResult.confidence * 100).toFixed(1)}%</p>
            <p><strong>Is Positive:</strong> {analysisResult.is_positive ? 'Yes' : 'No'}</p>
            <div style={{marginTop: '10px'}}>
              <strong>All Emotion Scores:</strong>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '5px'}}>
                {Object.entries(analysisResult.emotion_scores || {}).map(([emotion, score]) => (
                  <span key={emotion} style={{
                    background: emotionColors[emotion] || '#ccc',
                    color: 'white',
                    padding: '3px 8px',
                    borderRadius: '15px',
                    fontSize: '12px'
                  }}>
                    {emotion}: {(score * 100).toFixed(0)}%
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Emotion Selection */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>🎯 2. Select Emotions for Pathfinding</h2>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
          <div>
            <h4>Current Emotion:</h4>
            <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center'}}>
              {emotions.map(emotion => renderEmotionCircle(emotion, emotion === currentEmotion, false))}
            </div>
          </div>
          <div>
            <h4>Target Emotion:</h4>
            <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center'}}>
              {emotions.map(emotion => renderEmotionCircle(emotion, false, emotion === targetEmotion))}
            </div>
          </div>
        </div>
        
        <div style={{textAlign: 'center', marginTop: '20px'}}>
          <button
            onClick={findPath}
            disabled={loading || !currentEmotion || !targetEmotion || backendStatus !== 'connected'}
            style={{
              padding: '15px 30px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            {loading ? 'Finding Path...' : '🔍 Find Optimal Path (A* Algorithm)'}
          </button>
        </div>
      </div>

      {/* Path Result */}
      {pathResult && (
        <div style={{background: '#e8f5e8', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
          {renderPath()}
        </div>
      )}

      {/* Suggestions */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>💡 3. Get Suggestions</h2>
        <div style={{textAlign: 'center'}}>
          <button
            onClick={getSuggestions}
            disabled={loading || !currentEmotion || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#ffc107',
              color: 'black',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Loading...' : `Get Suggestions for ${currentEmotion}`}
          </button>
        </div>
        
        {suggestions.length > 0 && (
          <div style={{marginTop: '15px'}}>
            <h4>Suggestions for {currentEmotion}:</h4>
            <ul style={{listStyle: 'none', padding: 0}}>
              {suggestions.map((suggestion, index) => (
                <li key={index} style={{
                  background: '#fff3cd',
                  padding: '10px',
                  margin: '5px 0',
                  borderRadius: '5px',
                  borderLeft: '4px solid #ffc107'
                }}>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Algorithm Testing */}
      <div style={{background: '#e3f2fd', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>🔬 4. Test Algorithm</h2>
        <p>Run automated tests to verify the A* pathfinding algorithm is working correctly.</p>
        <div style={{textAlign: 'center'}}>
          <button
            onClick={testAlgorithm}
            disabled={loading || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Testing...' : '🧪 Run Algorithm Tests'}
          </button>
        </div>
        <p style={{fontSize: '12px', color: '#666', textAlign: 'center', marginTop: '10px'}}>
          Check browser console (F12) for detailed test results
        </p>
      </div>

      {/* Development Info */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', border: '1px solid #ddd'}}>
        <h3>🔧 Development Info</h3>
        <p><strong>Backend:</strong> Simple Python Flask (proxied via React dev server)</p>
        <p><strong>Frontend:</strong> Basic React (this page)</p>
        <p><strong>Storage:</strong> In-memory (no database)</p>
        <p><strong>Focus:</strong> Algorithm development and testing</p>
        
        <div style={{marginTop: '15px'}}>
          <h4>Key Algorithm Files:</h4>
          <ul style={{fontSize: '14px', color: '#666'}}>
            <li><code>backend/simple_app.py</code> - Main backend with A* algorithm</li>
            <li><code>SimpleEmotionAnalyzer</code> - Text emotion analysis</li>
            <li><code>AStarPathfinder</code> - A* pathfinding implementation</li>
          </ul>
        </div>

        <div style={{marginTop: '15px'}}>
          <h4>🚀 Quick Commands:</h4>
          <ul style={{fontSize: '14px', color: '#666'}}>
            <li><code>./start-simple.sh</code> - Start both frontend and backend</li>
            <li><code>./start-backend.sh</code> - Start backend only</li>
            <li><code>./start-frontend.sh</code> - Start frontend only</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SimpleAIDemo;

import React, { useState, useEffect, useCallback } from 'react';

const EnhancedIntelligentAgentApp = () => {
  const [activeTab, setActiveTab] = useState('conversation');
  const [backendUrl, setBackendUrl] = useState('http://localhost:5001');
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [iemocapLoaded, setIemocapLoaded] = useState(false);
  const [validationResults, setValidationResults] = useState([]);
  const [iemocapStats, setIemocapStats] = useState(null);

  // Make API call helper
  const makeApiCall = useCallback(async (endpoint, options = {}) => {
    try {
      const response = await fetch(backendUrl + '/api' + endpoint, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }, [backendUrl]);

  // Check backend connection
  const checkConnection = useCallback(async () => {
    try {
      const response = await makeApiCall('/health');
      const health = await response.json();
      setConnectionStatus('connected');
      setIemocapLoaded(health.iemocap_loaded || false);
      return true;
    } catch (error) {
      setConnectionStatus('error');
      return false;
    }
  }, [makeApiCall]);

  // Load IEMOCAP data
  const loadIemocapData = async (dataPath) => {
    try {
      const response = await makeApiCall('/load-iemocap', {
        method: 'POST',
        body: JSON.stringify({ data_path: dataPath })
      });
      
      const result = await response.json();
      if (result.success) {
        setIemocapLoaded(true);
        await loadIemocapStats();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load IEMOCAP data:', error);
      return false;
    }
  };

  // Load IEMOCAP statistics
  const loadIemocapStats = async () => {
    try {
      const response = await makeApiCall('/iemocap-stats');
      const stats = await response.json();
      setIemocapStats(stats);
    } catch (error) {
      console.error('Failed to load IEMOCAP stats:', error);
    }
  };

  // Load validation results
  const loadValidationResults = async () => {
    try {
      const response = await makeApiCall('/validation-results');
      const data = await response.json();
      setValidationResults(data.validation_results || []);
    } catch (error) {
      console.error('Failed to load validation results:', error);
    }
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkConnection]);

  useEffect(() => {
    if (iemocapLoaded) {
      loadValidationResults();
    }
  }, [iemocapLoaded]);

  const renderConnectionStatus = () => {
    const statusColors = {
      connecting: '#ffc107',
      connected: '#28a745',
      error: '#dc3545'
    };

    const statusMessages = {
      connecting: 'Connecting to backend...',
      connected: 'Connected to Enhanced AI Backend',
      error: 'Backend connection failed'
    };

    return (
      <div style={{
        padding: '10px',
        backgroundColor: statusColors[connectionStatus],
        color: 'white',
        textAlign: 'center',
        fontWeight: 'bold'
      }}>
        {statusMessages[connectionStatus]}
        {iemocapLoaded && connectionStatus === 'connected' && ' • IEMOCAP Dataset Loaded'}
      </div>
    );
  };

  const renderTabNavigation = () => (
    <div style={{
      display: 'flex',
      borderBottom: '2px solid #e9ecef',
      backgroundColor: '#f8f9fa'
    }}>
      {[
        { id: 'conversation', label: '💬 Conversation & Memory', icon: '🧠' },
        { id: 'algorithm', label: '🏁 Algorithm Racing', icon: '⚡' },
        { id: 'dataset', label: '📊 IEMOCAP Integration', icon: '🔬' },
        { id: 'validation', label: '🧪 Validation Results', icon: '📈' }
      ].map(tab => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          style={{
            flex: 1,
            padding: '15px',
            border: 'none',
            backgroundColor: activeTab === tab.id ? '#007bff' : 'transparent',
            color: activeTab === tab.id ? 'white' : '#666',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: activeTab === tab.id ? 'bold' : 'normal',
            transition: 'all 0.2s ease'
          }}
        >
          {tab.icon} {tab.label}
        </button>
      ))}
    </div>
  );

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      fontFamily: 'Arial, sans-serif'
    }}>
      {renderConnectionStatus()}
      
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '30px',
            textAlign: 'center'
          }}>
            <h1 style={{ margin: '0 0 10px 0', fontSize: '2.5rem' }}>
              🤖 Enhanced Reflectly AI
            </h1>
            <p style={{ margin: 0, fontSize: '1.1rem', opacity: 0.9 }}>
              Emotional Intelligence with IEMOCAP Dataset Integration
            </p>
          </div>

          {renderTabNavigation()}

          <div style={{ padding: '20px' }}>
            {activeTab === 'conversation' && (
              <ConversationTab 
                makeApiCall={makeApiCall} 
                connectionStatus={connectionStatus}
              />
            )}
            {activeTab === 'algorithm' && (
              <AlgorithmRacingTab 
                makeApiCall={makeApiCall} 
                connectionStatus={connectionStatus}
              />
            )}
            {activeTab === 'dataset' && (
              <IEMOCAPIntegrationTab 
                makeApiCall={makeApiCall}
                iemocapLoaded={iemocapLoaded}
                iemocapStats={iemocapStats}
                onLoadIemocap={loadIemocapData}
                onStatsUpdate={loadIemocapStats}
              />
            )}
            {activeTab === 'validation' && (
              <ValidationResultsTab 
                makeApiCall={makeApiCall}
                validationResults={validationResults}
                onResultsUpdate={loadValidationResults}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Conversation Tab Component
const ConversationTab = ({ makeApiCall, connectionStatus }) => {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [memoryMap, setMemoryMap] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || connectionStatus !== 'connected') return;

    setIsProcessing(true);
    try {
      const response = await makeApiCall('/process-input', {
        method: 'POST',
        body: JSON.stringify({ text: input, user_id: 'demo_user' })
      });
      
      const result = await response.json();
      setResponse(result);
      setInput('');
      
      // Refresh memory map
      loadMemoryMap();
    } catch (error) {
      console.error('Error processing input:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const loadMemoryMap = async () => {
    try {
      const response = await makeApiCall('/memory-map');
      const data = await response.json();
      setMemoryMap(data);
    } catch (error) {
      console.error('Failed to load memory map:', error);
    }
  };

  useEffect(() => {
    if (connectionStatus === 'connected') {
      loadMemoryMap();
    }
  }, [connectionStatus]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        border: '1px solid #e9ecef'
      }}>
        <h3 style={{ marginTop: 0, color: '#333' }}>💬 Emotional Conversation</h3>
        
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Share how you're feeling... (e.g., 'I'm feeling sad and overwhelmed today')"
            style={{
              width: '100%',
              height: '100px',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px',
              resize: 'vertical'
            }}
            disabled={connectionStatus !== 'connected'}
          />
          <button
            type="submit"
            disabled={!input.trim() || isProcessing || connectionStatus !== 'connected'}
            style={{
              marginTop: '10px',
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              width: '100%'
            }}
          >
            {isProcessing ? '🤖 Processing...' : '💭 Share Feeling'}
          </button>
        </form>

        {response && (
          <div style={{
            backgroundColor: 'white',
            padding: '15px',
            borderRadius: '5px',
            border: '1px solid #dee2e6'
          }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#007bff' }}>
              🤖 AI Response
            </h4>
            <p style={{ margin: '0 0 10px 0', lineHeight: '1.5' }}>
              {response.message}
            </p>
            
            {response.suggestions && response.suggestions.length > 0 && (
              <div style={{ marginTop: '10px' }}>
                <strong>💡 Suggestions:</strong>
                <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px' }}>
                  {response.suggestions.map((suggestion, index) => (
                    <li key={index} style={{ margin: '2px 0' }}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {response.algorithm_used && (
              <div style={{
                marginTop: '10px',
                padding: '8px',
                backgroundColor: '#e7f3ff',
                borderRadius: '4px',
                fontSize: '12px'
              }}>
                <strong>🔍 Algorithm Used:</strong> {response.algorithm_used}
                {response.algorithm_performance && (
                  <span> • {response.algorithm_performance.time_ms?.toFixed(1)}ms</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        border: '1px solid #e9ecef'
      }}>
        <h3 style={{ marginTop: 0, color: '#333' }}>🧠 Memory Map</h3>
        
        {memoryMap ? (
          <div>
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#666' }}>
                📊 Statistics
              </h4>
              <div style={{ fontSize: '12px', color: '#666' }}>
                <div>Experiences: {memoryMap.nodes?.length || 0}</div>
                <div>Transitions: {memoryMap.edges?.length || 0}</div>
                <div>Emotions: {new Set(memoryMap.nodes?.map(n => n.emotion) || []).size}</div>
              </div>
            </div>

            <div style={{
              maxHeight: '300px',
              overflowY: 'auto',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              padding: '10px',
              backgroundColor: 'white'
            }}>
              {memoryMap.nodes?.map((node, index) => (
                <div key={index} style={{
                  padding: '8px',
                  margin: '5px 0',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '3px',
                  fontSize: '12px'
                }}>
                  <strong>{node.emotion}:</strong> {node.count} experiences
                  {node.actions && node.actions.length > 0 && (
                    <div style={{ marginTop: '3px', fontSize: '11px', color: '#666' }}>
                      Actions: {node.actions.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            Start a conversation to build your memory map!
          </div>
        )}
      </div>
    </div>
  );
};

// Algorithm Racing Tab Component (Enhanced)
const AlgorithmRacingTab = ({ makeApiCall, connectionStatus }) => {
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [startEmotion, setStartEmotion] = useState('sad');
  const [goalEmotion, setGoalEmotion] = useState('happy');

  const emotions = ['happy', 'sad', 'anxious', 'angry', 'confused', 'tired', 'neutral'];

  const compareAlgorithms = async () => {
    setIsComparing(true);
    try {
      const response = await makeApiCall('/compare-algorithms', {
        method: 'POST',
        body: JSON.stringify({
          start_emotion: startEmotion,
          goal_emotion: goalEmotion
        })
      });

      const result = await response.json();
      setComparisonResult(result);
    } catch (error) {
      console.error('Error comparing algorithms:', error);
      alert('Failed to compare algorithms. Make sure the backend is running.');
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '15px',
        marginBottom: '30px',
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px'
      }}>
        <label>
          From:
          <select 
            value={startEmotion} 
            onChange={(e) => setStartEmotion(e.target.value)}
            style={{
              marginLeft: '8px',
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: '5px'
            }}
          >
            {emotions.map(emotion => (
              <option key={emotion} value={emotion}>
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </option>
            ))}
          </select>
        </label>

        <span style={{ fontSize: '20px', color: '#666' }}>→</span>

        <label>
          To:
          <select 
            value={goalEmotion} 
            onChange={(e) => setGoalEmotion(e.target.value)}
            style={{
              marginLeft: '8px',
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: '5px'
            }}
          >
            {emotions.map(emotion => (
              <option key={emotion} value={emotion}>
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </option>
            ))}
          </select>
        </label>

        <button 
          onClick={compareAlgorithms} 
          disabled={isComparing || startEmotion === goalEmotion || connectionStatus !== 'connected'}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {isComparing ? '🔄 Racing...' : '🏁 Start Race!'}
        </button>
      </div>

      {isComparing && (
        <div style={{
          textAlign: 'center',
          padding: '30px',
          backgroundColor: '#e7f3ff',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <p style={{ fontSize: '18px', margin: '0 0 10px 0' }}>
            🏃‍♂️ Algorithms racing from <strong>{startEmotion}</strong> to <strong>{goalEmotion}</strong>...
          </p>
          <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>
            Testing A*, Bidirectional Search, and Dijkstra's algorithms
          </p>
        </div>
      )}

      {comparisonResult && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {Object.entries(comparisonResult.results).map(([algorithm, result]) => {
            const isWinner = comparisonResult.winner?.algorithm === algorithm;
            const metrics = result.metrics;
            
            return (
              <div key={algorithm} style={{
                border: `2px solid ${isWinner ? '#28a745' : '#e9ecef'}`,
                borderRadius: '8px',
                padding: '20px',
                backgroundColor: isWinner ? '#f8fff9' : 'white'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '15px'
                }}>
                  <h4 style={{ margin: 0, color: '#333' }}>{algorithm}</h4>
                  {isWinner && (
                    <span style={{
                      backgroundColor: '#28a745',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}>
                      🏆 WINNER
                    </span>
                  )}
                </div>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px',
                  marginBottom: '15px'
                }}>
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <div style={{ color: '#666' }}>⏱️ Time:</div>
                    <div style={{ fontWeight: 'bold' }}>
                      {metrics.execution_time_ms.toFixed(2)}ms
                    </div>
                  </div>
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <div style={{ color: '#666' }}>🔍 Nodes:</div>
                    <div style={{ fontWeight: 'bold' }}>{metrics.nodes_explored}</div>
                  </div>
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <div style={{ color: '#666' }}>📏 Path Length:</div>
                    <div style={{ fontWeight: 'bold' }}>{metrics.path_length}</div>
                  </div>
                  <div style={{
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <div style={{ color: '#666' }}>✅ Success:</div>
                    <div style={{ fontWeight: 'bold' }}>
                      {metrics.path_found ? 'Yes' : 'No'}
                    </div>
                  </div>
                </div>
                
                {result.path && result.path.length > 0 && (
                  <div style={{
                    padding: '12px',
                    backgroundColor: '#e9ecef',
                    borderRadius: '5px'
                  }}>
                    <strong>Path:</strong>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '5px',
                      marginTop: '8px'
                    }}>
                      {result.path.map((emotion, index) => (
                        <React.Fragment key={index}>
                          <span style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            {emotion}
                          </span>
                          {index < result.path.length - 1 && (
                            <span style={{ color: '#666', fontWeight: 'bold' }}>→</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// IEMOCAP Integration Tab Component
const IEMOCAPIntegrationTab = ({ 
  makeApiCall, 
  iemocapLoaded, 
  iemocapStats, 
  onLoadIemocap, 
  onStatsUpdate 
}) => {
  const [dataPath, setDataPath] = useState('iemocap_validation_data.json');
  const [isLoading, setIsLoading] = useState(false);
  const [isRunningValidation, setIsRunningValidation] = useState(false);
  const [numTests, setNumTests] = useState(100);

  const handleLoadDataset = async () => {
    setIsLoading(true);
    try {
      const success = await onLoadIemocap(dataPath);
      if (success) {
        alert('IEMOCAP dataset loaded successfully!');
        onStatsUpdate();
      } else {
        alert('Failed to load IEMOCAP dataset. Check the file path.');
      }
    } catch (error) {
      alert('Error loading dataset: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const runValidation = async () => {
    setIsRunningValidation(true);
    try {
      const response = await makeApiCall('/run-validation', {
        method: 'POST',
        body: JSON.stringify({ num_tests: numTests })
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`Validation completed! Ran ${numTests} tests.`);
      } else {
        alert('Validation failed: ' + result.error);
      }
    } catch (error) {
      alert('Error running validation: ' + error.message);
    } finally {
      setIsRunningValidation(false);
    }
  };

  return (
    <div>
      <div style={{
        marginBottom: '30px',
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e9ecef'
      }}>
        <h3 style={{ marginTop: 0, color: '#333' }}>
          📊 IEMOCAP Dataset Integration
        </h3>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Dataset Path:
          </label>
          <input
            type="text"
            value={dataPath}
            onChange={(e) => setDataPath(e.target.value)}
            placeholder="Path to IEMOCAP validation data JSON file"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px'
            }}
            disabled={isLoading}
          />
        </div>

        <button
          onClick={handleLoadDataset}
          disabled={isLoading || !dataPath.trim()}
          style={{
            padding: '10px 20px',
            backgroundColor: iemocapLoaded ? '#28a745' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: 'bold',
            marginRight: '10px'
          }}
        >
          {isLoading ? '📥 Loading...' : iemocapLoaded ? '✅ Dataset Loaded' : '📥 Load Dataset'}
        </button>

        {iemocapLoaded && (
          <div style={{ marginTop: '20px' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>
              🧪 Run Algorithm Validation
            </h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <label>
                Number of tests:
                <input
                  type="number"
                  value={numTests}
                  onChange={(e) => setNumTests(Math.max(1, parseInt(e.target.value) || 1))}
                  min="1"
                  max="1000"
                  style={{
                    marginLeft: '8px',
                    padding: '5px',
                    border: '1px solid #ddd',
                    borderRadius: '3px',
                    width: '80px'
                  }}
                />
              </label>
              <button
                onClick={runValidation}
                disabled={isRunningValidation}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                {isRunningValidation ? '🔄 Running...' : '🧪 Run Validation'}
              </button>
            </div>
          </div>
        )}
      </div>

      {iemocapStats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          <div style={{
            padding: '20px',
            backgroundColor: 'white',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ marginTop: 0, color: '#333' }}>📈 Dataset Statistics</h4>
            <div style={{ fontSize: '14px' }}>
              <div style={{ margin: '5px 0' }}>
                <strong>Conversations:</strong> {iemocapStats.conversations}
              </div>
              <div style={{ margin: '5px 0' }}>
                <strong>Emotions:</strong> {iemocapStats.emotional_map?.nodes?.length || 0}
              </div>
              <div style={{ margin: '5px 0' }}>
                <strong>Transitions:</strong> {iemocapStats.emotional_map?.edges?.length || 0}
              </div>
            </div>
          </div>

          <div style={{
            padding: '20px',
            backgroundColor: 'white',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ marginTop: 0, color: '#333' }}>🤖 ML Model Info</h4>
            {iemocapStats.ml_model_info?.accuracy ? (
              <div style={{ fontSize: '14px' }}>
                <div style={{ margin: '5px 0' }}>
                  <strong>Accuracy:</strong> {(iemocapStats.ml_model_info.accuracy * 100).toFixed(1)}%
                </div>
                <div style={{ margin: '5px 0' }}>
                  <strong>Trained:</strong> {new Date(iemocapStats.ml_model_info.trained_on).toLocaleDateString()}
                </div>
              </div>
            ) : (
              <div style={{ color: '#666', fontSize: '14px' }}>
                ML model not trained yet
              </div>
            )}
          </div>

          {iemocapStats.emotional_map?.nodes && (
            <div style={{
              padding: '20px',
              backgroundColor: 'white',
              borderRadius: '8px',
              border: '1px solid #e9ecef',
              gridColumn: 'span 2'
            }}>
              <h4 style={{ marginTop: 0, color: '#333' }}>🗺️ Emotional Map</h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '10px',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {iemocapStats.emotional_map.nodes.map((node, index) => (
                  <div key={index} style={{
                    padding: '10px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '5px',
                    fontSize: '12px'
                  }}>
                    <strong>{node.label || node.id}:</strong> {node.count} samples
                    {node.common_actions && node.common_actions.length > 0 && (
                      <div style={{ marginTop: '5px', color: '#666' }}>
                        Actions: {node.common_actions.slice(0, 3).join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Validation Results Tab Component
const ValidationResultsTab = ({ makeApiCall, validationResults, onResultsUpdate }) => {
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    onResultsUpdate();
  }, []);

  const formatAlgorithmMetrics = (metrics) => {
    if (!metrics) return 'No data';
    
    return (
      <div style={{ fontSize: '12px' }}>
        <div>Success Rate: {(metrics.success_rate * 100).toFixed(1)}%</div>
        <div>Avg Time: {metrics.avg_time_ms?.toFixed(2)}ms</div>
        <div>Avg Nodes: {metrics.avg_nodes_explored?.toFixed(1)}</div>
      </div>
    );
  };

  return (
    <div>
      <div style={{
        marginBottom: '20px',
        padding: '15px',
        backgroundColor: '#e7f3ff',
        borderRadius: '8px',
        border: '1px solid #bee5eb'
      }}>
        <h3 style={{ marginTop: 0, color: '#0c5460' }}>
          🧪 Algorithm Validation Results
        </h3>
        <p style={{ margin: 0, color: '#0c5460' }}>
          Results from testing algorithms against IEMOCAP emotional speech dataset
        </p>
      </div>

      {validationResults.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          color: '#666'
        }}>
          <p style={{ fontSize: '18px', margin: '0 0 10px 0' }}>
            No validation results yet
          </p>
          <p style={{ margin: 0 }}>
            Load IEMOCAP dataset and run validation to see results here
          </p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr',
          gap: '20px'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ marginTop: 0, color: '#333' }}>📊 Validation Sessions</h4>
            <div style={{
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              {validationResults.map((result, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedResult(result)}
                  style={{
                    padding: '12px',
                    margin: '8px 0',
                    backgroundColor: selectedResult === result ? '#e7f3ff' : '#f8f9fa',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    border: selectedResult === result ? '2px solid #007bff' : '1px solid #e9ecef',
                    fontSize: '14px'
                  }}
                >
                  <div style={{ fontWeight: 'bold' }}>
                    Validation #{index + 1}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {new Date(result.timestamp).toLocaleDateString()}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {result.results?.total_tests || 0} tests
                  </div>
                  {result.best_algorithm && (
                    <div style={{ fontSize: '11px', color: '#28a745' }}>
                      Best: {result.best_algorithm.algorithm}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            {selectedResult ? (
              <div>
                <h4 style={{ marginTop: 0, color: '#333' }}>
                  📈 Detailed Results
                </h4>
                
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Date:</strong> {new Date(selectedResult.timestamp).toLocaleString()}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Total Tests:</strong> {selectedResult.results?.total_tests || 0}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Dataset:</strong> {selectedResult.dataset || 'IEMOCAP'}
                  </div>
                </div>

                {selectedResult.best_algorithm && (
                  <div style={{
                    padding: '15px',
                    backgroundColor: '#d4edda',
                    borderRadius: '5px',
                    marginBottom: '20px',
                    border: '1px solid #c3e6cb'
                  }}>
                    <h5 style={{ margin: '0 0 10px 0', color: '#155724' }}>
                      🏆 Best Performing Algorithm
                    </h5>
                    <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#155724' }}>
                      {selectedResult.best_algorithm.algorithm}
                    </div>
                    <div style={{ fontSize: '14px', color: '#155724' }}>
                      Score: {selectedResult.best_algorithm.score?.toFixed(3)}
                    </div>
                  </div>
                )}

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '15px'
                }}>
                  {Object.entries(selectedResult.results?.average_metrics || {}).map(([algorithm, metrics]) => (
                    <div key={algorithm} style={{
                      padding: '15px',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '5px',
                      border: '1px solid #e9ecef'
                    }}>
                      <h6 style={{ margin: '0 0 10px 0', color: '#333' }}>
                        {algorithm}
                      </h6>
                      {formatAlgorithmMetrics(metrics)}
                    </div>
                  ))}
                </div>

                {selectedResult.results?.test_cases && (
                  <div style={{ marginTop: '20px' }}>
                    <h5 style={{ color: '#333' }}>Sample Test Cases</h5>
                    <div style={{
                      maxHeight: '200px',
                      overflowY: 'auto',
                      border: '1px solid #e9ecef',
                      borderRadius: '5px'
                    }}>
                      {selectedResult.results.test_cases.map((testCase, index) => (
                        <div key={index} style={{
                          padding: '10px',
                          borderBottom: '1px solid #f8f9fa',
                          fontSize: '12px'
                        }}>
                          <strong>{testCase.start} → {testCase.goal}</strong>
                          <div style={{ color: '#666', marginTop: '3px' }}>
                            Context: {testCase.context?.substring(0, 50)}...
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                color: '#666'
              }}>
                <p>Select a validation session to view detailed results</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedIntelligentAgentApp;
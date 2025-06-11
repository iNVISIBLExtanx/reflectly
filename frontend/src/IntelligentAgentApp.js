import React, { useState, useEffect } from 'react';

const IntelligentAgentApp = () => {
  const [inputText, setInputText] = useState('');
  const [conversation, setConversation] = useState([]);
  const [memoryMap, setMemoryMap] = useState({ nodes: [], edges: [] });
  const [memoryStats, setMemoryStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [showingStepsForm, setShowingStepsForm] = useState(false);
  const [currentExperienceId, setCurrentExperienceId] = useState('');
  const [stepsInput, setStepsInput] = useState(['']);

  const API_BASE = '/api';

  // Emotion colors for map visualization
  const emotionColors = {
    happy: '#4CAF50',      // Green
    sad: '#2196F3',        // Blue  
    anxious: '#FF9800',    // Orange
    angry: '#F44336',      // Red
    confused: '#9C27B0',   // Purple
    tired: '#607D8B',      // Blue Grey
    neutral: '#9E9E9E'     // Grey
  };

  useEffect(() => {
    loadMemoryMap();
    loadMemoryStats();
  }, []);

  const loadMemoryMap = async () => {
    try {
      const response = await fetch(`${API_BASE}/memory-map`);
      if (response.ok) {
        const data = await response.json();
        setMemoryMap(data);
      }
    } catch (error) {
      console.error('Error loading memory map:', error);
    }
  };

  const loadMemoryStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/memory-stats`);
      if (response.ok) {
        const data = await response.json();
        setMemoryStats(data);
      }
    } catch (error) {
      console.error('Error loading memory stats:', error);
    }
  };

  const processInput = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/process-input`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: inputText,
          user_id: 'user1'
        })
      });

      if (response.ok) {
        const agentResponse = await response.json();
        
        // Add user input and agent response to conversation
        setConversation(prev => [
          ...prev,
          {
            type: 'user',
            text: inputText,
            timestamp: new Date().toLocaleTimeString()
          },
          {
            type: 'agent',
            ...agentResponse,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);

        // Clear input
        setInputText('');

        // If agent asks for steps, show steps form
        if (agentResponse.type === 'ask_for_steps') {
          setShowingStepsForm(true);
          setCurrentExperienceId(agentResponse.experience_id);
          setStepsInput(['']);
        }

        // Reload memory map and stats
        await loadMemoryMap();
        await loadMemoryStats();
      }
    } catch (error) {
      console.error('Error processing input:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSteps = async () => {
    const steps = stepsInput.filter(step => step.trim() !== '');
    if (steps.length === 0) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/save-steps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experience_id: currentExperienceId,
          steps: steps
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Add confirmation to conversation
        setConversation(prev => [
          ...prev,
          {
            type: 'agent',
            message: result.message,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);

        // Clear steps form
        setShowingStepsForm(false);
        setCurrentExperienceId('');
        setStepsInput(['']);

        // Reload memory map and stats
        await loadMemoryMap();
        await loadMemoryStats();
      }
    } catch (error) {
      console.error('Error saving steps:', error);
    } finally {
      setLoading(false);
    }
  };

  const addStepInput = () => {
    setStepsInput(prev => [...prev, '']);
  };

  const updateStepInput = (index, value) => {
    setStepsInput(prev => {
      const newSteps = [...prev];
      newSteps[index] = value;
      return newSteps;
    });
  };

  const removeStepInput = (index) => {
    setStepsInput(prev => prev.filter((_, i) => i !== index));
  };

  const resetMemory = async () => {
    if (window.confirm('Are you sure you want to reset the memory map? This will clear all learned experiences.')) {
      try {
        const response = await fetch(`${API_BASE}/reset-memory`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
          setConversation([]);
          setMemoryMap({ nodes: [], edges: [] });
          setMemoryStats({});
          alert('Memory map reset successfully!');
        }
      } catch (error) {
        console.error('Error resetting memory:', error);
      }
    }
  };

  const renderMemoryMap = () => {
    const { nodes, edges } = memoryMap;
    
    if (!nodes.length) {
      return (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: '#666',
          fontStyle: 'italic'
        }}>
          No experiences yet. Start by sharing how you're feeling!
        </div>
      );
    }

    // Simple circular layout
    const centerX = 250;
    const centerY = 200;
    const radius = 120;
    const nodePositions = {};

    // Position nodes in a circle
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * 2 * Math.PI;
      nodePositions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    return (
      <div style={{ position: 'relative', width: '500px', height: '400px', border: '1px solid #ddd', borderRadius: '8px', background: '#f9f9f9' }}>
        <svg width="500" height="400">
          {/* Render edges */}
          {edges.map((edge, index) => {
            const fromPos = nodePositions[edge.from];
            const toPos = nodePositions[edge.to];
            if (!fromPos || !toPos) return null;

            return (
              <g key={index}>
                <line
                  x1={fromPos.x}
                  y1={fromPos.y}
                  x2={toPos.x}
                  y2={toPos.y}
                  stroke="#999"
                  strokeWidth={Math.min(edge.weight + 1, 5)}
                  opacity={0.7}
                />
                <text
                  x={(fromPos.x + toPos.x) / 2}
                  y={(fromPos.y + toPos.y) / 2}
                  fill="#666"
                  fontSize="10"
                  textAnchor="middle"
                >
                  {edge.actions}
                </text>
              </g>
            );
          })}

          {/* Render nodes */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id];
            const color = emotionColors[node.id] || '#999';
            
            return (
              <g key={node.id}>
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={20 + (node.count * 2)}
                  fill={color}
                  stroke="#fff"
                  strokeWidth="2"
                  opacity={0.8}
                />
                <text
                  x={pos.x}
                  y={pos.y + 4}
                  fill="#fff"
                  fontSize="12"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {node.label}
                </text>
                <text
                  x={pos.x}
                  y={pos.y + 35}
                  fill="#333"
                  fontSize="10"
                  textAnchor="middle"
                >
                  ({node.count})
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  const renderConversation = () => {
    return (
      <div style={{
        height: '400px',
        overflowY: 'auto',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '15px',
        background: '#fff',
        marginBottom: '15px'
      }}>
        {conversation.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#666', fontStyle: 'italic', marginTop: '150px' }}>
            👋 Hi! I'm your intelligent agent. Tell me how you're feeling and I'll learn from your experiences to help you better.
          </div>
        ) : (
          conversation.map((message, index) => (
            <div key={index} style={{
              marginBottom: '15px',
              display: 'flex',
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '10px 15px',
                borderRadius: '18px',
                background: message.type === 'user' ? '#007bff' : '#f1f1f1',
                color: message.type === 'user' ? '#fff' : '#333'
              }}>
                <div>{message.message || message.text}</div>
                <div style={{ fontSize: '11px', opacity: 0.7, marginTop: '5px' }}>
                  {message.timestamp}
                </div>
                {message.suggestions && message.suggestions.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>💡 Suggestions:</strong>
                    <ul style={{ margin: '5px 0', paddingLeft: '15px' }}>
                      {message.suggestions.map((suggestion, i) => (
                        <li key={i} style={{ marginBottom: '3px' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    );
  };

  const renderStepsForm = () => {
    if (!showingStepsForm) return null;

    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div style={{
          background: '#fff',
          padding: '30px',
          borderRadius: '12px',
          maxWidth: '500px',
          width: '90%',
          maxHeight: '80vh',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0, color: '#4CAF50' }}>🌟 Share Your Success Steps!</h3>
          <p>What specific steps or actions led to this positive feeling? This helps me learn and suggest similar actions to help in the future.</p>
          
          {stepsInput.map((step, index) => (
            <div key={index} style={{ marginBottom: '10px', display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={step}
                onChange={(e) => updateStepInput(index, e.target.value)}
                placeholder={`Step ${index + 1}...`}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px'
                }}
              />
              {stepsInput.length > 1 && (
                <button
                  onClick={() => removeStepInput(index)}
                  style={{
                    padding: '8px',
                    background: '#f44336',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          
          <button
            onClick={addStepInput}
            style={{
              padding: '8px 16px',
              background: '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            + Add Step
          </button>
          
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => setShowingStepsForm(false)}
              style={{
                padding: '10px 20px',
                background: '#666',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              onClick={saveSteps}
              disabled={loading || stepsInput.every(step => !step.trim())}
              style={{
                padding: '10px 20px',
                background: '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                opacity: (loading || stepsInput.every(step => !step.trim())) ? 0.6 : 1
              }}
            >
              {loading ? 'Saving...' : 'Save Steps'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '10px' }}>
        🤖 Intelligent Agent with Memory Map
      </h1>
      <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px' }}>
        An AI that learns from your experiences and uses A* search to suggest helpful actions
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Left Side - Conversation */}
        <div>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>💬 Conversation</h2>
          
          {renderConversation()}
          
          {/* Input Area */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && processInput()}
              placeholder="Tell me how you're feeling... (e.g., 'I'm feeling really happy today' or 'I'm sad and stressed')"
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
            <button
              onClick={processInput}
              disabled={loading || !inputText.trim()}
              style={{
                padding: '12px 24px',
                background: '#007bff',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? '🤔' : '💭'}
            </button>
          </div>

          {/* Example inputs */}
          <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
            <strong>Try these examples:</strong>
            <div style={{ marginTop: '5px' }}>
              • "I'm feeling really happy and excited!"
            </div>
            <div>
              • "I'm sad and don't know what to do"
            </div>
            <div>
              • "I'm feeling anxious about work"
            </div>
          </div>
        </div>

        {/* Right Side - Memory Map */}
        <div>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>🗺️ Memory Map</h2>
          
          {renderMemoryMap()}
          
          {/* Memory Stats */}
          <div style={{
            marginTop: '15px',
            padding: '15px',
            background: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>📊 Learning Stats</h4>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div>Total Experiences: <strong>{memoryStats.total_experiences || 0}</strong></div>
              <div>Emotions Learned: <strong>{memoryStats.emotions_learned || 0}</strong></div>
              <div>Transitions Learned: <strong>{memoryStats.transitions_learned || 0}</strong></div>
            </div>
          </div>

          {/* Legend */}
          <div style={{
            marginTop: '15px',
            padding: '10px',
            background: '#fff',
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}>
            <h5 style={{ margin: '0 0 8px 0', color: '#333' }}>🎨 Map Legend</h5>
            <div style={{ fontSize: '12px', color: '#666' }}>
              <div>• Circle size = Number of experiences</div>
              <div>• Line thickness = Number of learned transitions</div>
              <div>• Numbers on lines = Available action suggestions</div>
            </div>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetMemory}
            style={{
              marginTop: '15px',
              padding: '8px 16px',
              background: '#dc3545',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            🗑️ Reset Memory
          </button>
        </div>
      </div>

      {/* How it Works */}
      <div style={{
        marginTop: '40px',
        padding: '20px',
        background: '#e8f5e8',
        borderRadius: '10px',
        border: '1px solid #c3e6c3'
      }}>
        <h3 style={{ color: '#2e7d32', marginTop: 0 }}>🧠 How the Intelligent Agent Works</h3>
        <div style={{ color: '#1b5e20', lineHeight: 1.6 }}>
          <p><strong>😊 When you share positive emotions:</strong> The agent asks what steps led to that feeling and saves them to its memory map.</p>
          <p><strong>😢 When you share negative emotions:</strong> The agent uses A* search through its learned experiences to suggest actions that previously helped transition to positive emotions.</p>
          <p><strong>🗺️ Memory Map Evolution:</strong> Each interaction builds the emotional graph, creating connections between emotions and the actions that successfully bridge them.</p>
          <p><strong>🎯 A* Search:</strong> The algorithm finds optimal paths through emotional states, suggesting the most effective sequences of actions based on past successes.</p>
        </div>
      </div>

      {renderStepsForm()}
    </div>
  );
};

export default IntelligentAgentApp;

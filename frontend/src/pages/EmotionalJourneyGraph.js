import React, { useState, useEffect, useCallback } from 'react';
import axios from '../utils/axiosConfig';

const EmotionalJourneyGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [], history: [] });
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [pathResult, setPathResult] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [availableEmotions, setAvailableEmotions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userEmail] = useState('demo@reflectly.ai'); // Demo user for AI testing

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

  // Load available emotions on component mount
  useEffect(() => {
    loadAvailableEmotions();
    loadGraphData();
  }, []);

  const loadAvailableEmotions = async () => {
    try {
      const response = await axios.get('/api/emotions/available');
      setAvailableEmotions(response.data.emotions);
      if (response.data.emotions.length > 0) {
        setCurrentEmotion(response.data.emotions[0]);
        setTargetEmotion('joy'); // Default target
      }
    } catch (error) {
      console.error('Error loading emotions:', error);
    }
  };

  const loadGraphData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/emotions/graph-data/${userEmail}`);
      setGraphData(response.data);
    } catch (error) {
      console.error('Error loading graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const findOptimalPath = async () => {
    if (!currentEmotion || !targetEmotion) return;
    
    try {
      setLoading(true);
      const response = await axios.post('/api/emotions/path', {
        user_email: userEmail,
        current_emotion: currentEmotion,
        target_emotion: targetEmotion,
        max_depth: 10
      });
      setPathResult(response.data);
    } catch (error) {
      console.error('Error finding path:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSuggestions = async () => {
    if (!currentEmotion) return;
    
    try {
      const response = await axios.post('/api/emotions/suggestions', {
        user_email: userEmail,
        current_emotion: currentEmotion
      });
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Error getting suggestions:', error);
    }
  };

  const analyzeText = async (text) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/emotions/analyze', {
        text: text,
        user_email: userEmail
      });
      
      // Update current emotion based on analysis
      setCurrentEmotion(response.data.primary_emotion);
      
      // Reload graph data to show new transition
      await loadGraphData();
      
      return response.data;
    } catch (error) {
      console.error('Error analyzing text:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderGraph = () => {
    const { nodes, edges } = graphData;
    
    if (!nodes.length) {
      return (
        <div className=\"graph-placeholder\">
          <p>No emotional data yet. Try analyzing some text or finding a path!</p>
        </div>
      );
    }

    return (
      <div className=\"emotion-graph\">
        <svg width=\"600\" height=\"400\" viewBox=\"0 0 600 400\">
          {/* Render edges */}
          {edges.map((edge, index) => {
            const fromNode = nodes.find(n => n.id === edge.from);
            const toNode = nodes.find(n => n.id === edge.to);
            if (!fromNode || !toNode) return null;
            
            const fromIndex = nodes.indexOf(fromNode);
            const toIndex = nodes.indexOf(toNode);
            
            // Simple circular layout
            const centerX = 300, centerY = 200, radius = 120;
            const fromAngle = (fromIndex / nodes.length) * 2 * Math.PI;
            const toAngle = (toIndex / nodes.length) * 2 * Math.PI;
            
            const x1 = centerX + radius * Math.cos(fromAngle);
            const y1 = centerY + radius * Math.sin(fromAngle);
            const x2 = centerX + radius * Math.cos(toAngle);
            const y2 = centerY + radius * Math.sin(toAngle);
            
            return (
              <line
                key={index}
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke=\"#ccc\"
                strokeWidth={Math.min(edge.weight, 5)}
                opacity={0.6}
              />
            );
          })}
          
          {/* Render nodes */}
          {nodes.map((node, index) => {
            const centerX = 300, centerY = 200, radius = 120;
            const angle = (index / nodes.length) * 2 * Math.PI;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            const isCurrentEmotion = node.id === currentEmotion;
            const isTargetEmotion = node.id === targetEmotion;
            const isInPath = pathResult && pathResult.path && pathResult.path.includes(node.id);
            
            return (
              <g key={node.id}>
                <circle
                  cx={x} cy={y} r={isCurrentEmotion || isTargetEmotion ? \"25\" : \"20\"}
                  fill={emotionColors[node.id] || '#808080'}
                  stroke={isInPath ? '#ff6b35' : (isCurrentEmotion ? '#000' : '#666')}
                  strokeWidth={isInPath ? \"4\" : (isCurrentEmotion ? \"3\" : \"1\")}
                  opacity={isInPath ? 1 : 0.8}
                />
                <text
                  x={x} y={y + 5}
                  textAnchor=\"middle\"
                  fontSize=\"12\"
                  fontWeight={isCurrentEmotion ? \"bold\" : \"normal\"}
                  fill={isCurrentEmotion ? \"#000\" : \"#333\"}
                >
                  {node.label}
                </text>
                {isCurrentEmotion && (
                  <text x={x} y={y - 35} textAnchor=\"middle\" fontSize=\"10\" fill=\"#000\">
                    CURRENT
                  </text>
                )}
                {isTargetEmotion && (
                  <text x={x} y={y - 35} textAnchor=\"middle\" fontSize=\"10\" fill=\"#000\">
                    TARGET
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  const renderPathResult = () => {
    if (!pathResult) return null;
    
    return (
      <div className=\"path-result\">
        <h3>🎯 Optimal Emotional Path</h3>
        <div className=\"path-info\">
          <p><strong>Path:</strong> {pathResult.path ? pathResult.path.join(' → ') : 'No path found'}</p>
          <p><strong>Estimated Success Rate:</strong> {(pathResult.estimated_success_rate * 100).toFixed(1)}%</p>
          <p><strong>Total Cost:</strong> {pathResult.total_cost?.toFixed(2)}</p>
        </div>
        
        {pathResult.actions && pathResult.actions.length > 0 && (
          <div className=\"path-actions\">
            <h4>📋 Recommended Actions:</h4>
            {pathResult.actions.map((action, index) => (
              <div key={index} className=\"action-step\">
                <div className=\"action-transition\">
                  <strong>{action.from} → {action.to}</strong>
                </div>
                <div className=\"action-description\">{action.action}</div>
                <div className=\"action-success\">
                  Success Rate: {(action.success_rate * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className=\"emotional-journey-page\">
      <div className=\"page-header\">
        <h1>🧠 AI Emotional Pathfinding</h1>
        <p>Discover optimal paths between emotional states using A* search algorithm</p>
      </div>

      <div className=\"ai-controls\">
        <div className=\"pathfinding-section\">
          <h2>🔍 Find Optimal Path</h2>
          <div className=\"emotion-selectors\">
            <div className=\"selector-group\">
              <label>Current Emotion:</label>
              <select 
                value={currentEmotion} 
                onChange={(e) => setCurrentEmotion(e.target.value)}
              >
                {availableEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>{emotion}</option>
                ))}
              </select>
            </div>
            
            <div className=\"selector-group\">
              <label>Target Emotion:</label>
              <select 
                value={targetEmotion} 
                onChange={(e) => setTargetEmotion(e.target.value)}
              >
                {availableEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>{emotion}</option>
                ))}
              </select>
            </div>
            
            <button 
              onClick={findOptimalPath}
              disabled={loading || !currentEmotion || !targetEmotion}
              className=\"find-path-btn\"
            >
              {loading ? 'Finding Path...' : '🎯 Find Optimal Path'}
            </button>
          </div>
        </div>

        <div className=\"text-analysis-section\">
          <h2>📝 Analyze Text</h2>
          <div className=\"text-input-group\">
            <textarea
              placeholder=\"Enter text to analyze emotional state...\"
              rows=\"3\"
              id=\"text-input\"
            />
            <button 
              onClick={() => {
                const text = document.getElementById('text-input').value;
                if (text.trim()) {
                  analyzeText(text);
                  document.getElementById('text-input').value = '';
                }
              }}
              disabled={loading}
              className=\"analyze-btn\"
            >
              {loading ? 'Analyzing...' : '🔬 Analyze Emotion'}
            </button>
          </div>
        </div>

        <button 
          onClick={getSuggestions}
          disabled={loading || !currentEmotion}
          className=\"suggestions-btn\"
        >
          💡 Get Suggestions for {currentEmotion}
        </button>
      </div>

      <div className=\"visualization-section\">
        <h2>🗺️ Emotional Graph Visualization</h2>
        {loading ? (
          <div className=\"loading\">Loading graph data...</div>
        ) : (
          renderGraph()
        )}
      </div>

      {pathResult && renderPathResult()}

      {suggestions.length > 0 && (
        <div className=\"suggestions-section\">
          <h3>💡 Personalized Suggestions</h3>
          <ul className=\"suggestions-list\">
            {suggestions.map((suggestion, index) => (
              <li key={index} className=\"suggestion-item\">
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className=\"graph-legend\">
        <h3>🎨 Graph Legend</h3>
        <div className=\"legend-items\">
          {Object.entries(emotionColors).map(([emotion, color]) => (
            <div key={emotion} className=\"legend-item\">
              <div 
                className=\"legend-color\" 
                style={{ backgroundColor: color }}
              ></div>
              <span>{emotion}</span>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .emotional-journey-page {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .page-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .page-header h1 {
          color: #2c3e50;
          margin-bottom: 10px;
        }

        .ai-controls {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 30px;
        }

        .pathfinding-section, .text-analysis-section {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
        }

        .emotion-selectors {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .selector-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .selector-group label {
          font-weight: 600;
          color: #495057;
        }

        .selector-group select {
          padding: 8px;
          border: 1px solid #ced4da;
          border-radius: 5px;
          font-size: 14px;
        }

        .find-path-btn, .analyze-btn, .suggestions-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 25px;
          cursor: pointer;
          font-weight: 600;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .find-path-btn:hover, .analyze-btn:hover, .suggestions-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .find-path-btn:disabled, .analyze-btn:disabled, .suggestions-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .suggestions-btn {
          grid-column: 1 / -1;
          justify-self: center;
          margin-top: 10px;
        }

        .text-input-group {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .text-input-group textarea {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 5px;
          resize: vertical;
          font-family: inherit;
        }

        .visualization-section {
          background: #ffffff;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
          margin-bottom: 20px;
          text-align: center;
        }

        .emotion-graph {
          display: flex;
          justify-content: center;
          margin: 20px 0;
        }

        .graph-placeholder {
          padding: 60px;
          color: #6c757d;
          font-style: italic;
        }

        .loading {
          padding: 40px;
          color: #6c757d;
          font-style: italic;
        }

        .path-result {
          background: #e8f5e8;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #c3e6c3;
          margin-bottom: 20px;
        }

        .path-info {
          margin-bottom: 15px;
        }

        .path-info p {
          margin: 5px 0;
        }

        .path-actions {
          margin-top: 15px;
        }

        .action-step {
          background: #f8f9fa;
          padding: 12px;
          margin: 8px 0;
          border-radius: 5px;
          border-left: 4px solid #28a745;
        }

        .action-transition {
          font-weight: 600;
          color: #495057;
          margin-bottom: 5px;
        }

        .action-description {
          color: #343a40;
          margin-bottom: 5px;
        }

        .action-success {
          font-size: 12px;
          color: #28a745;
          font-weight: 600;
        }

        .suggestions-section {
          background: #fff3cd;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #ffeaa7;
          margin-bottom: 20px;
        }

        .suggestions-list {
          list-style: none;
          padding: 0;
        }

        .suggestion-item {
          background: #ffffff;
          padding: 12px;
          margin: 8px 0;
          border-radius: 5px;
          border-left: 4px solid #ffc107;
        }

        .graph-legend {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
        }

        .legend-items {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          margin-top: 10px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .legend-color {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 1px solid #ccc;
        }

        @media (max-width: 768px) {
          .ai-controls {
            grid-template-columns: 1fr;
          }
          
          .emotion-selectors {
            gap: 10px;
          }
          
          .legend-items {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default EmotionalJourneyGraph;

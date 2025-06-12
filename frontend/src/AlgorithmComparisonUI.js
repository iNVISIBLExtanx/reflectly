// frontend/src/AlgorithmComparisonUI.js
import React, { useState, useEffect, useCallback } from 'react';

const AlgorithmComparisonUI = ({ makeApiCall }) => {
  const [comparisonResult, setComparisonResult] = useState(null);
  const [performanceStats, setPerformanceStats] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [startEmotion, setStartEmotion] = useState('sad');
  const [goalEmotion, setGoalEmotion] = useState('happy');
  const [backendStatus, setBackendStatus] = useState('connected');

  const emotions = ['happy', 'sad', 'anxious', 'angry', 'confused', 'tired', 'neutral'];

  const loadPerformanceStats = useCallback(async () => {
    try {
      const response = await makeApiCall('/algorithm-performance');
      if (response.ok) {
        const data = await response.json();
        setPerformanceStats(data);
      }
    } catch (error) {
      console.error('Error loading performance stats:', error);
      setBackendStatus('error');
    }
  }, [makeApiCall]);

  useEffect(() => {
    loadPerformanceStats();
  }, [loadPerformanceStats]);

  const compareAlgorithms = async () => {
    setIsComparing(true);
    try {
      const response = await makeApiCall('/compare-algorithms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_emotion: startEmotion,
          goal_emotion: goalEmotion
        })
      });

      if (response.ok) {
        const result = await response.json();
        setComparisonResult(result);
        await loadPerformanceStats(); // Refresh stats
        setBackendStatus('connected');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Error comparing algorithms:', error);
      setBackendStatus('error');
      alert('Failed to compare algorithms. Make sure the backend is running.');
    } finally {
      setIsComparing(false);
    }
  };

  const renderAlgorithmResult = (algorithmName, result) => {
    const metrics = result.metrics;
    const isWinner = comparisonResult?.winner?.algorithm === algorithmName;
    
    return (
      <div key={algorithmName} className={`algorithm-result ${isWinner ? 'winner' : ''}`}>
        <div className="algorithm-header">
          <h4>
            {algorithmName} 
            {isWinner && <span className="winner-badge">🏆 WINNER</span>}
          </h4>
        </div>
        
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">⏱️ Time:</span>
            <span className="metric-value">{metrics.execution_time_ms.toFixed(2)}ms</span>
          </div>
          <div className="metric">
            <span className="metric-label">🔍 Nodes Explored:</span>
            <span className="metric-value">{metrics.nodes_explored}</span>
          </div>
          <div className="metric">
            <span className="metric-label">📏 Path Length:</span>
            <span className="metric-value">{metrics.path_length}</span>
          </div>
          <div className="metric">
            <span className="metric-label">✅ Success:</span>
            <span className="metric-value">{metrics.path_found ? 'Yes' : 'No'}</span>
          </div>
          <div className="metric">
            <span className="metric-label">📊 Efficiency:</span>
            <span className="metric-value">{metrics.efficiency_score?.toFixed(2) || 'N/A'}</span>
          </div>
        </div>
        
        {result.path && result.path.length > 0 && (
          <div className="path-display">
            <strong>Path Found:</strong>
            <div className="path-chain">
              {result.path.map((emotion, index) => (
                <span key={index} className="path-emotion">
                  {emotion}
                  {index < result.path.length - 1 && <span className="path-arrow">→</span>}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPerformanceChart = () => {
    if (!performanceStats?.algorithm_statistics) {
      return (
        <div className="performance-chart">
          <h3>📊 Algorithm Performance Over Time</h3>
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            No performance data yet. Run some algorithm comparisons to see statistics!
          </div>
        </div>
      );
    }

    const algorithms = Object.keys(performanceStats.algorithm_statistics);
    
    return (
      <div className="performance-chart">
        <h3>📊 Algorithm Performance Over Time</h3>
        <div className="stats-summary">
          <p>Total Comparisons: <strong>{performanceStats.total_comparisons || 0}</strong></p>
        </div>
        <div className="chart-container">
          {algorithms.map(algorithm => {
            const stats = performanceStats.algorithm_statistics[algorithm];
            const winRate = stats.win_rate || 0;
            const avgTime = stats.avg_time_ms || 0;
            const successRate = stats.success_rate || 0;
            
            return (
              <div key={algorithm} className="algorithm-stats">
                <h4>{algorithm}</h4>
                <div className="stat-bars">
                  <div className="stat-bar">
                    <span className="stat-label">Win Rate:</span>
                    <div className="bar-container">
                      <div 
                        className="bar win-rate" 
                        style={{ width: `${winRate}%` }}
                      ></div>
                      <span className="bar-text">{winRate.toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="stat-bar">
                    <span className="stat-label">Success Rate:</span>
                    <div className="bar-container">
                      <div 
                        className="bar success-rate" 
                        style={{ width: `${successRate}%` }}
                      ></div>
                      <span className="bar-text">{successRate.toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="stat-bar">
                    <span className="stat-label">Avg Speed:</span>
                    <div className="bar-container">
                      <div 
                        className="bar speed" 
                        style={{ width: `${Math.min(avgTime / 10, 100)}%` }}
                      ></div>
                      <span className="bar-text">{avgTime.toFixed(1)}ms</span>
                    </div>
                  </div>
                  <div className="summary-stats">
                    <small>
                      {stats.total_uses} uses • {stats.wins} wins • {stats.avg_nodes_explored?.toFixed(1) || 0} avg nodes
                    </small>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderBackendStatus = () => {
    if (backendStatus === 'error') {
      return (
        <div style={{
          background: '#dc3545',
          color: 'white',
          padding: '10px 15px',
          borderRadius: '5px',
          margin: '10px 0',
          textAlign: 'center'
        }}>
          ❌ Backend connection failed. Make sure the backend is running!
        </div>
      );
    }
    return null;
  };

  return (
    <div className="algorithm-comparison-container">
      <style jsx>{`
        .algorithm-comparison-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }

        .comparison-header {
          text-align: center;
          margin-bottom: 30px;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 10px;
        }

        .comparison-controls {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 15px;
          margin-bottom: 30px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
          flex-wrap: wrap;
        }

        .emotion-select {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 5px;
          font-size: 14px;
          min-width: 100px;
        }

        .compare-button {
          padding: 10px 20px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          font-weight: bold;
          font-size: 14px;
          transition: background-color 0.2s;
        }

        .compare-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .compare-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .results-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .algorithm-result {
          border: 2px solid #e9ecef;
          border-radius: 8px;
          padding: 20px;
          background: white;
          transition: all 0.3s ease;
        }

        .algorithm-result.winner {
          border-color: #28a745;
          background: #f8fff9;
          box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
        }

        .algorithm-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 15px;
        }

        .algorithm-header h4 {
          margin: 0;
          color: #333;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .winner-badge {
          background: #28a745;
          color: white;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          margin-bottom: 15px;
        }

        .metric {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px;
          background: #f8f9fa;
          border-radius: 4px;
          font-size: 13px;
        }

        .metric-label {
          color: #666;
        }

        .metric-value {
          font-weight: bold;
          color: #333;
        }

        .path-display {
          margin-top: 15px;
          padding: 12px;
          background: #e9ecef;
          border-radius: 5px;
        }

        .path-chain {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 5px;
          margin-top: 8px;
        }

        .path-emotion {
          background: #007bff;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }

        .path-arrow {
          color: #666;
          font-weight: bold;
          margin: 0 5px;
        }

        .performance-chart {
          margin-top: 30px;
          padding: 20px;
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 8px;
        }

        .performance-chart h3 {
          margin-top: 0;
          color: #333;
        }

        .stats-summary {
          margin-bottom: 20px;
          text-align: center;
          color: #666;
        }

        .chart-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
        }

        .algorithm-stats {
          padding: 15px;
          background: #f8f9fa;
          border-radius: 5px;
          border: 1px solid #e9ecef;
        }

        .algorithm-stats h4 {
          margin: 0 0 15px 0;
          color: #333;
          text-align: center;
        }

        .stat-bars {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .stat-bar {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .stat-label {
          min-width: 85px;
          font-size: 12px;
          color: #666;
          font-weight: 500;
        }

        .bar-container {
          flex: 1;
          position: relative;
          height: 20px;
          background: #e9ecef;
          border-radius: 10px;
          overflow: hidden;
        }

        .bar {
          height: 100%;
          border-radius: 10px;
          transition: width 0.5s ease;
        }

        .bar.win-rate {
          background: linear-gradient(90deg, #28a745, #20c997);
        }

        .bar.success-rate {
          background: linear-gradient(90deg, #17a2b8, #138496);
        }

        .bar.speed {
          background: linear-gradient(90deg, #6f42c1, #563d7c);
        }

        .bar-text {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 11px;
          font-weight: bold;
          color: #333;
        }

        .summary-stats {
          margin-top: 10px;
          color: #666;
          text-align: center;
          font-size: 11px;
        }

        .loading {
          text-align: center;
          padding: 30px;
          color: #666;
          background: #f8f9fa;
          border-radius: 8px;
          margin: 20px 0;
        }

        .comparison-summary {
          margin-top: 20px;
          padding: 20px;
          background: #e7f3ff;
          border-left: 4px solid #007bff;
          border-radius: 5px;
        }

        .comparison-summary h3 {
          margin-top: 0;
          color: #0066cc;
        }

        .recent-races {
          margin-top: 20px;
        }

        .race-history {
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #e9ecef;
          border-radius: 5px;
        }

        .race-item {
          padding: 12px;
          margin: 0;
          background: #f8f9fa;
          border-bottom: 1px solid #e9ecef;
          font-size: 14px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .race-item:last-child {
          border-bottom: none;
        }

        .race-item:nth-child(even) {
          background: #ffffff;
        }

        @media (max-width: 768px) {
          .comparison-controls {
            flex-direction: column;
            gap: 10px;
          }
          
          .results-container {
            grid-template-columns: 1fr;
          }
          
          .chart-container {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <div className="comparison-header">
        <h1>🏁 Pathfinding Algorithm Race</h1>
        <p>Compare A*, Bidirectional Search, and Dijkstra's Algorithm for emotional navigation</p>
      </div>

      {renderBackendStatus()}

      <div className="comparison-controls">
        <label>
          From:
          <select 
            value={startEmotion} 
            onChange={(e) => setStartEmotion(e.target.value)}
            className="emotion-select"
          >
            {emotions.map(emotion => (
              <option key={emotion} value={emotion}>{emotion.charAt(0).toUpperCase() + emotion.slice(1)}</option>
            ))}
          </select>
        </label>

        <span style={{ fontSize: '20px', color: '#666' }}>→</span>

        <label>
          To:
          <select 
            value={goalEmotion} 
            onChange={(e) => setGoalEmotion(e.target.value)}
            className="emotion-select"
          >
            {emotions.map(emotion => (
              <option key={emotion} value={emotion}>{emotion.charAt(0).toUpperCase() + emotion.slice(1)}</option>
            ))}
          </select>
        </label>

        <button 
          onClick={compareAlgorithms} 
          disabled={isComparing || startEmotion === goalEmotion || backendStatus === 'error'}
          className="compare-button"
        >
          {isComparing ? '🔄 Racing...' : '🏁 Start Race!'}
        </button>
      </div>

      {isComparing && (
        <div className="loading">
          <p>🏃‍♂️ Algorithms are racing to find the best path from <strong>{startEmotion}</strong> to <strong>{goalEmotion}</strong>...</p>
          <p style={{ fontSize: '14px', color: '#999', marginTop: '10px' }}>
            Testing A*, Bidirectional Search, and Dijkstra's algorithms
          </p>
        </div>
      )}

      {comparisonResult && (
        <>
          <div className="results-container">
            {Object.entries(comparisonResult.results).map(([algorithm, result]) =>
              renderAlgorithmResult(algorithm, result)
            )}
          </div>

          <div className="comparison-summary">
            <h3>🏆 Race Results</h3>
            <p>
              <strong>{comparisonResult.winner.algorithm}</strong> won the race from{' '}
              <strong>{comparisonResult.start_emotion}</strong> to{' '}
              <strong>{comparisonResult.goal_emotion}</strong> in{' '}
              <strong>{comparisonResult.winner.time_ms?.toFixed(2)}ms</strong> by exploring{' '}
              <strong>{comparisonResult.winner.nodes_explored}</strong> emotional states.
            </p>
            <div style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
              Race completed at: {new Date(comparisonResult.timestamp).toLocaleString()}
            </div>
          </div>
        </>
      )}

      {renderPerformanceChart()}

      {performanceStats?.recent_comparisons && performanceStats.recent_comparisons.length > 0 && (
        <div className="performance-chart recent-races">
          <h3>📝 Recent Races ({performanceStats.recent_comparisons.length})</h3>
          <div className="race-history">
            {performanceStats.recent_comparisons.slice(-10).reverse().map((comp, index) => (
              <div key={index} className="race-item">
                <span>
                  <strong>{comp.start_emotion} → {comp.goal_emotion}</strong>
                </span>
                <span>
                  {comp.winner.algorithm} won ({comp.winner.time_ms?.toFixed(1)}ms)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AlgorithmComparisonUI;
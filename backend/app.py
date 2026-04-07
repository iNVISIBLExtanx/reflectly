"""
Reflectly Backend — Flask API
LLM + GNN + A* Pathfinding for emotional wellbeing
"""
import os
import datetime
from collections import defaultdict

from flask import Flask, request, jsonify
from flask_cors import CORS

from core.agent import IntelligentAgent, memory_map

app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Accept", "Authorization"],
    "supports_credentials": False
}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response


agent = IntelligentAgent()


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Reflectly — LLM + GNN + A* Pathfinding",
        "algorithms": ["A*", "Bidirectional Search", "Dijkstra"],
        "memory_stats": {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotional_states": len(memory_map["emotional_states"]),
            "learned_transitions": len(memory_map["transitions"]),
            "algorithm_comparisons": len(memory_map["algorithm_comparisons"])
        }
    })


@app.route('/api/process-input', methods=['POST', 'OPTIONS'])
def process_input():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_id = data.get('user_id', 'default_user')
        if not text.strip():
            return jsonify({"error": "Text input is required"}), 400
        return jsonify(agent.process_input(text, user_id))
    except Exception as e:
        return jsonify({"error": f"Failed to process input: {str(e)}"}), 500


@app.route('/api/compare-algorithms', methods=['POST', 'OPTIONS'])
def compare_algorithms():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        start = data.get('start_emotion', 'sad')
        goal = data.get('goal_emotion', 'happy')
        result = agent.pathfinding_comparator.compare_algorithms(start, goal)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to compare algorithms: {str(e)}"}), 500


@app.route('/api/algorithm-performance', methods=['GET'])
def get_algorithm_performance():
    try:
        if not memory_map["algorithm_comparisons"]:
            return jsonify({"message": "No algorithm comparisons performed yet"})

        algorithm_stats = defaultdict(lambda: {
            'total_uses': 0, 'wins': 0,
            'avg_time_ms': 0, 'avg_nodes_explored': 0, 'success_rate': 0
        })

        for comparison in memory_map["algorithm_comparisons"]:
            winner = comparison['winner']['algorithm']
            for algo, data in comparison['results'].items():
                stats = algorithm_stats[algo]
                stats['total_uses'] += 1
                if data['metrics']['path_found']:
                    stats['success_rate'] += 1
                    stats['avg_time_ms'] += data['metrics']['execution_time_ms']
                    stats['avg_nodes_explored'] += data['metrics']['nodes_explored']
                if algo == winner:
                    stats['wins'] += 1

        for stats in algorithm_stats.values():
            if stats['success_rate'] > 0:
                stats['avg_time_ms'] /= stats['success_rate']
                stats['avg_nodes_explored'] /= stats['success_rate']
            stats['success_rate'] = (stats['success_rate'] / stats['total_uses']) * 100
            stats['win_rate'] = (stats['wins'] / stats['total_uses']) * 100

        return jsonify({
            'total_comparisons': len(memory_map["algorithm_comparisons"]),
            'algorithm_statistics': dict(algorithm_stats),
            'recent_comparisons': memory_map["algorithm_comparisons"][-5:]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get performance data: {str(e)}"}), 500


@app.route('/api/memory-map', methods=['GET'])
def get_memory_map():
    try:
        nodes = [
            {
                'id': emotion,
                'label': emotion.title(),
                'count': len(experiences),
                'type': ('positive' if emotion == 'happy'
                         else 'negative' if emotion in ['sad', 'anxious', 'angry']
                         else 'neutral')
            }
            for emotion, experiences in memory_map["emotional_states"].items()
        ]
        edges = [
            {'from': from_e, 'to': to_e, 'actions': len(actions), 'weight': len(actions)}
            for (from_e, to_e), actions in memory_map["transitions"].items()
        ]
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'total_experiences': len(memory_map["user_experiences"]),
            'total_transitions': len(memory_map["transitions"])
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get memory map: {str(e)}"}), 500


@app.route('/api/reset-memory', methods=['POST', 'OPTIONS'])
def reset_memory():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        for key in ("emotional_states", "transitions", "user_experiences",
                    "graph_connections", "algorithm_comparisons"):
            memory_map[key].clear()
        return jsonify({"message": "Memory reset successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to reset memory: {str(e)}"}), 500


@app.route('/api/save-steps', methods=['POST', 'OPTIONS'])
def save_steps():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        experience_id = data.get('experience_id')
        steps = data.get('steps', [])
        if not experience_id or not steps:
            return jsonify({'error': 'Missing required fields'}), 400

        experience = next(
            (e for e in memory_map["user_experiences"] if e["id"] == experience_id), None
        )
        if not experience:
            return jsonify({'error': f'Experience {experience_id} not found'}), 404

        experience["activities"] = steps
        prev = agent._get_previous_emotion(experience)
        if prev and prev != experience['emotion']:
            agent._save_transition(prev, experience['emotion'], steps, experience_id)

        return jsonify({
            'message': f"Learned that {', '.join(steps)} can lead to feeling {experience['emotion']}!",
            'experience_id': experience_id,
            'emotion': experience['emotion'],
            'learned_activities': steps
        })
    except Exception as e:
        return jsonify({'error': f'Failed to save steps: {str(e)}'}), 500


@app.route('/api/memory-stats', methods=['GET'])
def get_memory_stats():
    try:
        algorithm_stats = {}
        for comp in memory_map["algorithm_comparisons"]:
            for algo, result in comp.get("results", {}).items():
                s = algorithm_stats.setdefault(algo, {"uses": 0, "wins": 0,
                                                       "avg_time_ms": 0, "avg_path_length": 0})
                s["uses"] += 1
                s["avg_time_ms"] += result.get("execution_time_ms", 0)
                s["avg_path_length"] += result.get("path_length", 0)
            winner_algo = comp.get("winner", {}).get("algorithm")
            if winner_algo and winner_algo in algorithm_stats:
                algorithm_stats[winner_algo]["wins"] += 1

        for algo, s in algorithm_stats.items():
            if s["uses"]:
                s["avg_time_ms"] = round(s["avg_time_ms"] / s["uses"], 2)
                s["avg_path_length"] = round(s["avg_path_length"] / s["uses"], 2)
                s["win_rate"] = round((s["wins"] / s["uses"]) * 100, 1)

        return jsonify({
            "total_experiences": len(memory_map["user_experiences"]),
            "emotions_learned": len(memory_map["emotional_states"]),
            "transitions_learned": len(memory_map["transitions"]),
            "algorithm_comparisons": len(memory_map["algorithm_comparisons"]),
            "algorithm_performance": algorithm_stats
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get memory stats: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Reflectly backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

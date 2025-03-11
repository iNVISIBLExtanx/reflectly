import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import redis
import json
from dotenv import load_dotenv
from models.emotion_analyzer import EmotionAnalyzer
from models.response_generator import ResponseGenerator
from models.memory_manager import MemoryManager, MongoJSONEncoder
from models.goal_tracker import GoalTracker

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask to use our custom JSON encoder
app.json_encoder = MongoJSONEncoder

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

# Redis connection
redis_uri = os.environ.get('REDIS_URI', 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_uri)

# Mock Kafka producer for local development
class MockKafkaProducer:
    def send(self, topic, value):
        print(f"[MOCK KAFKA] Sending to topic {topic}: {value}")
        return self
    
    def flush(self):
        pass

kafka_producer = MockKafkaProducer()

# Initialize models
emotion_analyzer = EmotionAnalyzer()
response_generator = ResponseGenerator()
memory_manager = MemoryManager(db, redis_client)
goal_tracker = GoalTracker(db)

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 409
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data.get('name', ''),
        'created_at': datetime.now()
    }
    
    db.users.insert_one(user)
    
    # Create access token
    access_token = create_access_token(identity=data['email'])
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Find user
    user = db.users.find_one({'email': data['email']})
    
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(identity=data['email'])
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

@app.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_user():
    user_email = get_jwt_identity()
    
    # Find user
    user = db.users.find_one({'email': user_email})
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Remove password before sending
    user.pop('password', None)
    user['_id'] = str(user['_id'])
    
    return jsonify(user), 200

# Journal entry routes
@app.route('/api/journal/entries', methods=['POST'])
@jwt_required()
def create_journal_entry():
    try:
        print("Received journal entry request")
        user_email = get_jwt_identity()
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Analyze emotion
        print("Analyzing emotion...")
        emotion_data = emotion_analyzer.analyze(data['content'])
        print(f"Emotion analysis result: {emotion_data}")
        
        # Generate response
        print("Generating response...")
        response = response_generator.generate(data['content'], emotion_data)
        print(f"Generated response: {response}")
        
        # Create journal entry
        entry = {
            'user_email': user_email,
            'content': data['content'],
            'emotion': emotion_data,
            'response': response,
            'created_at': datetime.now()
        }
        print(f"Created entry object: {entry}")
        
        result = db.journal_entries.insert_one(entry)
        print(f"MongoDB insert result: {result.inserted_id}")
        
        # Send to Kafka for processing
        kafka_data = {
            'entry_id': str(result.inserted_id),
            'user_email': user_email,
            'content': data['content'],
            'emotion': emotion_data
        }
        print(f"Sending to Kafka: {kafka_data}")
        kafka_producer.send('journal-entries', kafka_data)
        
        # Update memory
        print("Storing entry in memory manager...")
        memory_manager.store_entry(user_email, entry)
        print("Entry stored in memory manager")
        
        response_data = {
            'message': 'Journal entry created',
            'entry_id': str(result.inserted_id),
            'response': response
        }
        print(f"Sending response: {response_data}")
        return jsonify(response_data), 201
    except Exception as e:
        print(f"Error in create_journal_entry: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/journal/entries', methods=['GET'])
@jwt_required()
def get_journal_entries():
    user_email = get_jwt_identity()
    
    # Get entries from database
    entries = list(db.journal_entries.find({'user_email': user_email}).sort('created_at', -1))
    
    # Convert ObjectId to string
    for entry in entries:
        entry['_id'] = str(entry['_id'])
    
    return jsonify(entries), 200

# Goal routes
@app.route('/api/goals', methods=['POST'])
@jwt_required()
def create_goal():
    user_email = get_jwt_identity()
    data = request.get_json()
    
    # Create goal
    goal = {
        'user_email': user_email,
        'title': data['title'],
        'description': data.get('description', ''),
        'target_date': data.get('target_date'),
        'progress': 0,
        'created_at': datetime.now()
    }
    
    result = db.goals.insert_one(goal)
    
    return jsonify({
        'message': 'Goal created',
        'goal_id': str(result.inserted_id)
    }), 201

@app.route('/api/goals', methods=['GET'])
@jwt_required()
def get_goals():
    user_email = get_jwt_identity()
    
    # Get goals from database
    goals = list(db.goals.find({'user_email': user_email}))
    
    # Convert ObjectId to string
    for goal in goals:
        goal['_id'] = str(goal['_id'])
    
    return jsonify(goals), 200

@app.route('/api/goals/<goal_id>/progress', methods=['PUT'])
@jwt_required()
def update_goal_progress(goal_id):
    user_email = get_jwt_identity()
    data = request.get_json()
    
    # Update goal progress
    db.goals.update_one(
        {'_id': ObjectId(goal_id), 'user_email': user_email},
        {'$set': {'progress': data['progress']}}
    )
    
    # Check if goal is completed
    if data['progress'] >= 100:
        # Send to Kafka for achievement processing
        kafka_producer.send('goal-achievements', {
            'goal_id': goal_id,
            'user_email': user_email
        })
    
    return jsonify({'message': 'Goal progress updated'}), 200

# Memory routes
@app.route('/api/memories', methods=['GET'])
@jwt_required()
def get_memories():
    user_email = get_jwt_identity()
    
    # Get query parameters
    emotion = request.args.get('emotion')
    tag = request.args.get('tag')
    favorite = request.args.get('favorite', '').lower() == 'true'
    
    # Get memories with optional filters
    memories = memory_manager.get_memories(user_email, emotion=emotion, tag=tag, favorite=favorite)
    
    return jsonify(memories), 200

@app.route('/api/memories/<memory_id>', methods=['GET'])
@jwt_required()
def get_memory(memory_id):
    user_email = get_jwt_identity()
    
    # Get specific memory
    memory = memory_manager.get_memory_by_id(user_email, memory_id)
    
    if not memory:
        return jsonify({'message': 'Memory not found'}), 404
    
    return jsonify(memory), 200

@app.route('/api/memories', methods=['POST'])
@jwt_required()
def create_memory():
    user_email = get_jwt_identity()
    data = request.get_json()
    
    # Create memory
    memory = {
        'user_email': user_email,
        'title': data['title'],
        'content': data['content'],
        'emotion': data.get('emotion'),
        'tags': data.get('tags', []),
        'favorite': data.get('favorite', False),
        'created_at': datetime.now()
    }
    
    result = db.memories.insert_one(memory)
    
    return jsonify({
        'message': 'Memory created',
        'memory_id': str(result.inserted_id)
    }), 201

@app.route('/api/memories/<memory_id>', methods=['PUT'])
@jwt_required()
def update_memory(memory_id):
    user_email = get_jwt_identity()
    data = request.get_json()
    
    # Update memory
    result = db.memories.update_one(
        {'_id': ObjectId(memory_id), 'user_email': user_email},
        {'$set': {
            'title': data.get('title'),
            'content': data.get('content'),
            'emotion': data.get('emotion'),
            'tags': data.get('tags'),
            'favorite': data.get('favorite'),
            'updated_at': datetime.now()
        }}
    )
    
    if result.matched_count == 0:
        return jsonify({'message': 'Memory not found'}), 404
    
    return jsonify({'message': 'Memory updated'}), 200

@app.route('/api/memories/<memory_id>', methods=['DELETE'])
@jwt_required()
def delete_memory(memory_id):
    user_email = get_jwt_identity()
    
    # Delete memory
    result = db.memories.delete_one({'_id': ObjectId(memory_id), 'user_email': user_email})
    
    if result.deleted_count == 0:
        return jsonify({'message': 'Memory not found'}), 404
    
    return jsonify({'message': 'Memory deleted'}), 200

@app.route('/api/memories/positive', methods=['GET'])
@jwt_required()
def get_positive_memories():
    user_email = get_jwt_identity()
    
    # Get positive memories
    memories = memory_manager.get_positive_memories(user_email)
    
    return jsonify(memories), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

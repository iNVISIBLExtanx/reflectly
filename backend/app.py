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
from models.goal_tracker import GoalTracker
from models.emotional_graph import EmotionalGraph

# Custom JSON encoder to handle MongoDB ObjectId and datetime objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

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

# Admin secret key for protected routes
ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'admin-secret-key')

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
goal_tracker = GoalTracker(db)
emotional_graph = EmotionalGraph(db)

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
    print("Login endpoint called")
    data = request.get_json()
    print(f"Login attempt for email: {data.get('email')}")
    
    try:
        # Find user
        user = db.users.find_one({'email': data['email']})
        print(f"User found: {user is not None}")
        
        if not user:
            print("User not found")
            return jsonify({'message': 'Invalid credentials'}), 401
            
        # Check password
        password_match = bcrypt.checkpw(data['password'].encode('utf-8'), user['password'])
        print(f"Password match: {password_match}")
        
        if not password_match:
            print("Password does not match")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=data['email'])
        print(f"Access token created successfully")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

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
        
        # Validate input data
        if not data or 'content' not in data:
            return jsonify({'message': 'Missing content in request'}), 400
            
        # Analyze emotion
        print("Analyzing emotion...")
        try:
            emotion_data = emotion_analyzer.analyze(data['content'])
            print(f"Emotion analysis result: {emotion_data}")
        except Exception as e:
            print(f"Error in emotion analysis: {str(e)}")
            # Provide default emotion data if analysis fails
            emotion_data = {
                'primary_emotion': 'neutral',
                'is_positive': False,
                'emotion_scores': {}
            }
            
        # Record emotion in emotional graph
        try:
            print("Recording emotion in emotional graph...")
            emotion_state_id = emotional_graph.record_emotion(user_email, emotion_data)
            print(f"Recorded emotion state: {emotion_state_id}")
            # Add emotional state ID to emotion data
            emotion_data['emotion_state_id'] = emotion_state_id
        except Exception as e:
            print(f"Error recording emotion in graph: {str(e)}")
        
        # Create journal entry object
        entry = {
            'user_email': user_email,
            'content': data['content'],
            'emotion': emotion_data,
            'created_at': datetime.now(),
            'isUserMessage': data.get('isUserMessage', True)
        }
        
        # Memory functionality removed as requested
        memories = []
        
        # Get user's emotional history for context
        print("Retrieving emotional history...")
        try:
            emotion_history = emotional_graph.get_emotion_history(user_email, limit=5)
            print(f"Retrieved {len(emotion_history)} emotional history records")
        except Exception as e:
            print(f"Error retrieving emotional history: {str(e)}")
            emotion_history = []
        
        # Get personalized suggested actions from emotional graph
        print("Getting personalized suggested actions...")
        try:
            suggested_actions = emotional_graph.get_suggested_actions(user_email, emotion_data['primary_emotion'])
            print(f"Suggested actions: {suggested_actions}")
        except Exception as e:
            print(f"Error getting suggested actions: {str(e)}")
            suggested_actions = ["Take a moment to breathe", "Write down your thoughts", "Connect with a friend"]
        
        # Generate personalized response with emotional history
        print("Generating personalized response...")
        try:
            response_obj = response_generator.generate_with_memory(
                data['content'], 
                emotion_data, 
                memories=memories, 
                suggested_actions=suggested_actions,
                emotion_history=emotion_history
            )
            print(f"Generated response object: {response_obj}")
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            response_obj = {
                'text': 'I appreciate your entry. How are you feeling about this?', 
                'suggested_actions': suggested_actions
            }
        
        # Store user entry in database
        print(f"Created user entry object: {entry}")
        result = db.journal_entries.insert_one(entry)
        user_entry_id = result.inserted_id
        print(f"MongoDB insert result for user entry: {user_entry_id}")
        
        # Create and store AI response as a separate entry
        ai_entry = {
            'user_email': user_email,
            'content': response_obj['text'],
            'created_at': datetime.now(),
            'isUserMessage': False,
            'parent_entry_id': str(user_entry_id)
        }
        
        ai_result = db.journal_entries.insert_one(ai_entry)
        print(f"MongoDB insert result for AI response: {ai_result.inserted_id}")
        
        # Memory functionality removed as requested
        memory_entry_id = None
        
        # Send to Kafka for processing
        kafka_data = {
            'entry_id': str(result.inserted_id),
            'user_email': user_email,
            'content': data['content'],
            'emotion': emotion_data,
            'emotion_state_id': emotion_data.get('emotion_state_id')
        }
        print(f"Sending to Kafka: {kafka_data}")
        kafka_producer.send('journal-entries', kafka_data)
        
        # Memory functionality removed as requested
        
        response_data = {
            'message': 'Journal entry created',
            'entry_id': str(user_entry_id),
            'response_id': str(ai_result.inserted_id),
            'response': {
                'text': response_obj['text'],
                'suggested_actions': response_obj.get('suggested_actions', [])
            }
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
    
    # Get entries from database - sort by created_at in ascending order (oldest first)
    entries = list(db.journal_entries.find({'user_email': user_email}).sort('created_at', 1))
    
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
# Memory routes have been removed as requested

# Admin routes for user management
@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    # Check admin secret key
    auth_header = request.headers.get('X-Admin-Key')
    if not auth_header or auth_header != ADMIN_SECRET:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # List all users
    users = list(db.users.find({}, {'password': 0}))
    for user in users:
        user['_id'] = str(user['_id'])
    
    return jsonify(users), 200

@app.route('/api/admin/users', methods=['POST'])
def admin_create_user():
    # Check admin secret key
    auth_header = request.headers.get('X-Admin-Key')
    if not auth_header or auth_header != ADMIN_SECRET:
        return jsonify({'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['email', 'password', 'name']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = db.users.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'message': f"User with email {data['email']} already exists"}), 400
    
    # Hash the password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create user document
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data['name'],
        'created_at': datetime.utcnow()
    }
    
    # Insert into database
    result = db.users.insert_one(user)
    
    if result.inserted_id:
        return jsonify({'message': f"User {data['email']} created successfully"}), 201
    else:
        return jsonify({'message': 'Failed to create user'}), 500

@app.route('/api/admin/users/<email>', methods=['DELETE'])
def admin_delete_user(email):
    # Check admin secret key
    auth_header = request.headers.get('X-Admin-Key')
    if not auth_header or auth_header != ADMIN_SECRET:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Delete user
    result = db.users.delete_one({'email': email})
    
    if result.deleted_count > 0:
        return jsonify({'message': f'User {email} deleted successfully'}), 200
    else:
        return jsonify({'message': f'User with email {email} not found'}), 404

@app.route('/api/admin/db', methods=['GET'])
def admin_view_db():
    # Check admin secret key
    auth_header = request.headers.get('X-Admin-Key')
    if not auth_header or auth_header != ADMIN_SECRET:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Get all collections in the database
    collections = db.list_collection_names()
    
    # Get document counts for each collection
    collection_counts = {}
    collection_samples = {}
    
    for collection in collections:
        collection_counts[collection] = db[collection].count_documents({})
        # Get all documents
        samples = []
        for doc in db[collection].find():
            # Convert ObjectId to string
            doc['_id'] = str(doc['_id'])
            # Convert binary data to string representation
            if 'password' in doc and isinstance(doc['password'], bytes):
                doc['password'] = 'HASHED_PASSWORD_BINARY'
            samples.append(doc)
        collection_samples[collection] = samples
    
    return jsonify({
        'database': 'reflectly',
        'collections': collections,
        'counts': collection_counts,
        'samples': collection_samples
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

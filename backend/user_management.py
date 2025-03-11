import os
from pymongo import MongoClient
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

def create_user(email, password, name):
    """
    Create a new user in the database
    """
    # Check if user already exists
    existing_user = db.users.find_one({'email': email})
    if existing_user:
        return {'success': False, 'message': f'User with email {email} already exists'}
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user document
    user = {
        'email': email,
        'password': hashed_password,
        'name': name,
        'created_at': datetime.utcnow()
    }
    
    # Insert into database
    result = db.users.insert_one(user)
    
    if result.inserted_id:
        return {'success': True, 'message': f'User {email} created successfully'}
    else:
        return {'success': False, 'message': 'Failed to create user'}

def verify_user_credentials(email, password):
    """
    Verify user credentials
    """
    # Find user
    user = db.users.find_one({'email': email})
    
    if not user:
        return {'success': False, 'message': f'User with email {email} not found'}
    
    # Check password
    password_match = bcrypt.checkpw(password.encode('utf-8'), user['password'])
    
    if password_match:
        return {'success': True, 'message': 'Credentials verified', 'user': user}
    else:
        return {'success': False, 'message': 'Invalid password'}

def list_users():
    """
    List all users in the database
    """
    users = list(db.users.find({}, {'password': 0}))  # Exclude password field
    return users

def delete_user(email):
    """
    Delete a user from the database
    """
    result = db.users.delete_one({'email': email})
    
    if result.deleted_count > 0:
        return {'success': True, 'message': f'User {email} deleted successfully'}
    else:
        return {'success': False, 'message': f'User with email {email} not found'}

# Add admin routes to app.py to manage users
if __name__ == "__main__":
    # Example usage
    print("User Management Module")
    print("Available functions:")
    print("1. create_user(email, password, name)")
    print("2. verify_user_credentials(email, password)")
    print("3. list_users()")
    print("4. delete_user(email)")

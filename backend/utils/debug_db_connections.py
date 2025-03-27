"""
Debug database connections to identify why we're getting inconsistent results
"""
from pymongo import MongoClient
import os
import sys
import datetime
import pprint

# Add the parent directory to the path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# First connection - the one used by the generate_test_data script
print("===== CONNECTION 1: Direct connection (used by generate_test_data.py) =====")
mongo_uri_1 = 'mongodb://localhost:27017/reflectly'
client_1 = MongoClient(mongo_uri_1)
db_1 = client_1.get_database()
print(f"Database name: {db_1.name}")
print(f"Collections: {db_1.list_collection_names()}")

# Count users and journal entries
user_count_1 = db_1.users.count_documents({})
journal_count_1 = db_1.journal_entries.count_documents({})
print(f"Total users: {user_count_1}")
print(f"Total journal entries: {journal_count_1}")

# Count entries for specific user
user_entries_1 = db_1.journal_entries.count_documents({'user_email': 'test@example.com'})
print(f"Journal entries for test@example.com: {user_entries_1}")

# Second connection - the one used by the Flask app (from MONGODB_URI environment variable)
print("\n===== CONNECTION 2: Environment variable connection (used by Flask app) =====")
mongo_uri_2 = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
client_2 = MongoClient(mongo_uri_2)
db_2 = client_2.get_database()
print(f"Database name: {db_2.name}")
print(f"Collections: {db_2.list_collection_names()}")

# Count users and journal entries
user_count_2 = db_2.users.count_documents({})
journal_count_2 = db_2.journal_entries.count_documents({})
print(f"Total users: {user_count_2}")
print(f"Total journal entries: {journal_count_2}")

# Count entries for specific user
user_entries_2 = db_2.journal_entries.count_documents({'user_email': 'test@example.com'})
print(f"Journal entries for test@example.com: {user_entries_2}")

# Show a sample entry
print("\n===== Sample journal entry from CONNECTION 1 =====")
sample_entry_1 = db_1.journal_entries.find_one({'user_email': 'test@example.com'})
if sample_entry_1:
    print(f"Entry ID: {sample_entry_1['_id']}")
    print(f"Created at: {sample_entry_1.get('created_at')}")
    print(f"Created at type: {type(sample_entry_1.get('created_at'))}")
    print(f"isUserMessage: {sample_entry_1.get('isUserMessage')}")
else:
    print("No sample entry found")

# Check all users in the database
print("\n===== All users in CONNECTION 1 =====")
for user in db_1.users.find():
    print(f"User: {user['email']}")

# Check all users in the second connection
print("\n===== All users in CONNECTION 2 =====")
for user in db_2.users.find():
    print(f"User: {user['email']}")

# Create test journal entry if none exists
if user_entries_1 == 0:
    print("\n===== Creating test journal entry =====")
    test_entry = {
        "user_email": "test@example.com",
        "content": "Test journal entry created for debugging",
        "emotion": {
            "primary_emotion": "neutral",
            "emotion_scores": {
                "joy": 0.1,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "disgust": 0.1,
                "neutral": 0.5
            }
        },
        "created_at": datetime.datetime.now(),
        "isUserMessage": True
    }
    result = db_1.journal_entries.insert_one(test_entry)
    print(f"Created test entry with ID: {result.inserted_id}")

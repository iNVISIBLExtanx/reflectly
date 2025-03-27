"""
Debug script to check database contents
"""
from pymongo import MongoClient
import datetime
import pprint

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/reflectly')
db = client.get_database()

print(f'Database name: {db.name}')
print(f'Collections: {db.list_collection_names()}')

# Check journal entries
user_entries = list(db.journal_entries.find({'user_email': 'test@example.com'}))
print(f'Found {len(user_entries)} entries for test@example.com')

if user_entries:
    sample_entry = user_entries[0]
    print("\nSample entry:")
    pprint.pprint(sample_entry)
    print(f"\nCreated at: {sample_entry.get('created_at')}")
    print(f"Created at type: {type(sample_entry.get('created_at'))}")
    
    # Check emotion field structure
    if 'emotion' in sample_entry:
        print("\nEmotion field structure:")
        pprint.pprint(sample_entry['emotion'])
        print(f"Primary emotion: {sample_entry['emotion'].get('primary_emotion')}")
    else:
        print("No emotion field found in the entry")

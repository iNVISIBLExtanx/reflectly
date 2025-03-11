import os
from flask import Flask, jsonify, render_template_string
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

# HTML template for the admin viewer
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Reflectly MongoDB Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1, h2 {
            color: #333;
        }
        .collection {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .document {
            background-color: #f9f9f9;
            border-radius: 3px;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #2196F3;
            overflow-x: auto;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
        }
        .stats {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>Reflectly MongoDB Viewer</h1>
    
    <div class="stats">
        <p>Database: <strong>{{ db_name }}</strong></p>
        <p>Collections: <strong>{{ collections|length }}</strong></p>
    </div>
    
    {% for collection_name in collections %}
    <div class="collection">
        <h2>{{ collection_name }} ({{ collection_counts[collection_name] }} documents)</h2>
        
        {% for document in collection_data[collection_name] %}
        <div class="document">
            <pre>{{ document }}</pre>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    # Get all collections in the database
    collections = db.list_collection_names()
    
    # Get document counts for each collection
    collection_counts = {}
    for collection in collections:
        collection_counts[collection] = db[collection].count_documents({})
    
    # Get all documents from each collection
    collection_data = {}
    for collection in collections:
        documents = list(db[collection].find())
        collection_data[collection] = [dumps(doc, indent=2) for doc in documents]
    
    # Render the HTML template
    return render_template_string(
        HTML_TEMPLATE, 
        db_name='reflectly',
        collections=collections,
        collection_counts=collection_counts,
        collection_data=collection_data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

"""
Enhanced Intelligent Agent with Pathfinding Algorithm Comparison
Compare A*, Bidirectional Search, and Dijkstra's Algorithm in real-time
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import re
import heapq
import time
from collections import defaultdict, deque
import uuid

app = Flask(__name__)

# ENHANCED CORS Configuration for Colab + Local Frontend
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Accept", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": False
     }})

# Additional CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

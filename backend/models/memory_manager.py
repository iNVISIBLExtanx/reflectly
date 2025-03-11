from datetime import datetime, timedelta
import json
import random
from bson.objectid import ObjectId

# Custom JSON encoder to handle MongoDB ObjectId and datetime objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

class MemoryManager:
    """
    Class for managing the storage and retrieval of journal entries and memories.
    """
    
    def __init__(self, db, redis_client):
        """
        Initialize the memory manager.
        
        Args:
            db: MongoDB database connection
            redis_client: Redis client for caching
        """
        self.db = db
        self.redis_client = redis_client
        
        # Define memory tiers
        self.tiers = {
            'short_term': {'max_age': timedelta(days=7)},
            'medium_term': {'max_age': timedelta(days=30)},
            'long_term': {'max_age': timedelta(days=365)}
        }
    
    def store_entry(self, user_email, entry):
        """
        Store a journal entry in the memory system.
        
        Args:
            user_email (str): The user's email
            entry (dict): The journal entry to store
        """
        try:
            print(f"MemoryManager.store_entry called with user_email: {user_email}")
            print(f"Entry before processing: {entry}")
            
            # Create a copy of the entry to avoid modifying the original
            entry_copy = entry.copy()
            print(f"Entry copy created: {entry_copy}")
            
            # Convert datetime objects to strings for JSON serialization
            if isinstance(entry_copy.get('created_at'), datetime):
                print("Converting datetime to ISO format")
                entry_copy['created_at'] = entry_copy['created_at'].isoformat()
                print(f"Datetime converted: {entry_copy['created_at']}")
            
            # Check for ObjectId in the entry
            if '_id' in entry_copy and isinstance(entry_copy['_id'], ObjectId):
                print(f"Converting ObjectId to string: {entry_copy['_id']}")
                entry_copy['_id'] = str(entry_copy['_id'])
                print(f"ObjectId converted: {entry_copy['_id']}")
            
            # Store in Redis for short-term access (7 days)
            entry_key = f"entry:{user_email}:{entry_copy['_id']}"
            print(f"Redis key: {entry_key}")
            
            # Serialize the entry with our custom JSON encoder
            json_data = json.dumps(entry_copy, cls=MongoJSONEncoder)
            print(f"JSON serialized data: {json_data}")
            
            # Convert timedelta to integer seconds for Redis
            expiry_seconds = int(self.tiers['short_term']['max_age'].total_seconds())
            print(f"Setting expiry time: {expiry_seconds} seconds")
            
            self.redis_client.setex(
                entry_key,
                expiry_seconds,
                json_data
            )
            print(f"Entry stored in Redis with key: {entry_key}")
        except Exception as e:
            print(f"Error in store_entry: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # If the entry has positive emotion, store in positive memories
        if entry['emotion']['is_positive']:
            positive_key = f"positive_memories:{user_email}"
            
            # Handle the date formatting - check if it's already a string or still a datetime
            date_str = entry['created_at']
            if isinstance(entry['created_at'], datetime):
                date_str = entry['created_at'].strftime('%Y-%m-%d')
            elif isinstance(entry['created_at'], str):
                # Try to parse the ISO format string
                try:
                    date_obj = datetime.fromisoformat(entry['created_at'])
                    date_str = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # If parsing fails, just use the first 10 chars (YYYY-MM-DD)
                    date_str = entry['created_at'][:10]
                    
            memory_data = {
                'entry_id': str(entry['_id']),
                'date': date_str,
                'emotion': entry['emotion']['primary_emotion'],
                'summary': self._generate_summary(entry['content']),
                'score': self._calculate_memory_score(entry)
            }
            
            # Store in Redis list
            self.redis_client.lpush(positive_key, json.dumps(memory_data, cls=MongoJSONEncoder))
            # Trim list to keep only the top 50 memories
            self.redis_client.ltrim(positive_key, 0, 49)
    
    def get_positive_memories(self, user_email, limit=5):
        """
        Retrieve positive memories for a user.
        
        Args:
            user_email (str): The user's email
            limit (int): Maximum number of memories to retrieve
            
        Returns:
            list: List of positive memories
        """
        positive_key = f"positive_memories:{user_email}"
        
        # Get all memories from Redis
        memory_items = self.redis_client.lrange(positive_key, 0, -1)
        
        if not memory_items:
            # If Redis is empty, fetch from MongoDB
            entries = list(self.db.journal_entries.find({
                'user_email': user_email,
                'emotion.is_positive': True
            }).sort('created_at', -1).limit(20))
            
            memory_items = []
            for entry in entries:
                memory_data = {
                    'entry_id': str(entry['_id']),
                    'date': entry['created_at'].strftime('%Y-%m-%d'),
                    'emotion': entry['emotion']['primary_emotion'],
                    'summary': self._generate_summary(entry['content']),
                    'score': self._calculate_memory_score(entry)
                }
                memory_items.append(json.dumps(memory_data))
                
                # Store in Redis for future use
                self.redis_client.lpush(positive_key, json.dumps(memory_data, cls=MongoJSONEncoder))
            
            # Trim list to keep only the top 50 memories
            self.redis_client.ltrim(positive_key, 0, 49)
        
        # Parse JSON strings to dictionaries
        memories = [json.loads(item) for item in memory_items]
        
        # Sort by score and select top memories
        memories.sort(key=lambda x: x['score'], reverse=True)
        
        # Return a random selection from the top memories
        top_memories = memories[:min(10, len(memories))]
        selected_memories = random.sample(top_memories, min(limit, len(top_memories)))
        
        return selected_memories
    
    def get_relevant_memories(self, user_email, current_entry, limit=3):
        """
        Retrieve memories relevant to the current entry.
        
        Args:
            user_email (str): The user's email
            current_entry (dict): The current journal entry
            limit (int): Maximum number of memories to retrieve
            
        Returns:
            list: List of relevant memories
        """
        # In a production system, this would use semantic search or embeddings
        # For now, we'll use a simple approach based on emotion
        
        # If current emotion is negative, get positive memories
        if not current_entry['emotion']['is_positive']:
            return self.get_positive_memories(user_email, limit)
        
        # Otherwise, get memories with the same emotion
        entries = list(self.db.journal_entries.find({
            'user_email': user_email,
            'emotion.primary_emotion': current_entry['emotion']['primary_emotion'],
            '_id': {'$ne': current_entry['_id']}
        }).sort('created_at', -1).limit(10))
        
        memories = []
        for entry in entries:
            memory_data = {
                'entry_id': str(entry['_id']),
                'date': entry['created_at'].strftime('%Y-%m-%d'),
                'emotion': entry['emotion']['primary_emotion'],
                'summary': self._generate_summary(entry['content']),
                'score': self._calculate_memory_score(entry)
            }
            memories.append(memory_data)
        
        # Sort by score and select top memories
        memories.sort(key=lambda x: x['score'], reverse=True)
        
        # Return a random selection from the top memories
        selected_memories = random.sample(memories[:min(5, len(memories))], min(limit, len(memories[:5])))
        
        return selected_memories
    
    def get_memories(self, user_email, emotion=None, tag=None, favorite=None):
        """
        Retrieve memories for a user with optional filters.
        
        Args:
            user_email (str): The user's email
            emotion (str, optional): Filter by emotion
            tag (str, optional): Filter by tag
            favorite (bool, optional): Filter by favorite status
            
        Returns:
            list: List of memories
        """
        # Build query
        query = {'user_email': user_email}
        
        if emotion:
            query['emotion'] = emotion
        
        if tag:
            query['tags'] = tag
        
        if favorite is not None:
            query['favorite'] = favorite
        
        # Get memories from database
        memories = list(self.db.memories.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for memory in memories:
            memory['_id'] = str(memory['_id'])
            memory['created_at'] = memory['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in memory:
                memory['updated_at'] = memory['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return memories
    
    def get_memory_by_id(self, user_email, memory_id):
        """
        Retrieve a specific memory by ID.
        
        Args:
            user_email (str): The user's email
            memory_id (str): The memory ID
            
        Returns:
            dict: The memory or None if not found
        """
        try:
            # Get memory from database
            memory = self.db.memories.find_one({
                '_id': ObjectId(memory_id),
                'user_email': user_email
            })
            
            if memory:
                # Convert ObjectId to string
                memory['_id'] = str(memory['_id'])
                memory['created_at'] = memory['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if 'updated_at' in memory:
                    memory['updated_at'] = memory['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return memory
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None
    
    def _generate_summary(self, content, max_length=100):
        """
        Generate a summary of the content.
        
        Args:
            content (str): The content to summarize
            max_length (int): Maximum length of the summary
            
        Returns:
            str: A summary of the content
        """
        # In a production system, this would use a summarization model
        # For now, we'll use a simple approach
        if len(content) <= max_length:
            return content
        
        # Truncate and add ellipsis
        return content[:max_length - 3] + "..."
    
    def _calculate_memory_score(self, entry):
        """
        Calculate a relevance score for a memory.
        
        Args:
            entry (dict): The journal entry
            
        Returns:
            float: A relevance score
        """
        # In a production system, this would use a more sophisticated approach
        # For now, we'll use a simple heuristic
        
        # Base score
        score = 1.0
        
        # Adjust based on emotion intensity
        primary_emotion = entry['emotion']['primary_emotion']
        emotion_score = entry['emotion']['emotion_scores'][primary_emotion]
        score *= (1.0 + emotion_score)
        
        # Adjust based on recency (newer entries get higher scores)
        days_old = (datetime.now() - entry['created_at']).days
        recency_factor = max(0.5, 1.0 - (days_old / 365.0))
        score *= recency_factor
        
        return score

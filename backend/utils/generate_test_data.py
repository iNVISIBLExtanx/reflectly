"""
Generate test data for Reflectly application
This script creates sample journal entries with emotional data for testing
"""
import sys
import os
import random
import datetime
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

# Add the parent directory to the path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MongoDB setup
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
client = MongoClient(MONGODB_URI)
db = client.get_database()

# Constants for test data generation
TEST_USERS = [
    {"email": "test@example.com", "name": "Test User"},
    {"email": "jane@example.com", "name": "Jane Smith"},
    {"email": "john@example.com", "name": "John Doe"}
]

EMOTIONS = {
    'primary': [
        'joy', 'sadness', 'anger', 'fear', 'disgust', 'neutral',
        'surprise', 'contentment', 'anxiety', 'disappointment'
    ],
    'secondary': [
        'gratitude', 'love', 'pride', 'hope', 'guilt', 'shame',
        'boredom', 'confusion', 'amusement', 'excitement'
    ]
}

# Journal entry templates for different emotions
JOURNAL_TEMPLATES = {
    'joy': [
        "Today was an amazing day. {detail} I felt really happy throughout.",
        "I'm feeling so joyful right now. {detail} Everything seems to be going well.",
        "I had a great experience today. {detail} It brought me a lot of joy."
    ],
    'sadness': [
        "I'm feeling down today. {detail} It's been hard to stay positive.",
        "Today was difficult. {detail} I've been feeling sad most of the day.",
        "I'm struggling with feelings of sadness. {detail} Things feel heavy right now."
    ],
    'anger': [
        "I'm really frustrated about what happened today. {detail} It made me angry.",
        "Something really annoyed me. {detail} I felt my anger building up all day.",
        "I had an argument today. {detail} I'm still feeling annoyed about it."
    ],
    'fear': [
        "I'm feeling anxious about {detail}. It's making me fearful about the future.",
        "I'm worried about {detail}. This fear is hard to shake off.",
        "Today I was scared by {detail}. I'm having trouble calming down."
    ],
    'disgust': [
        "I saw something that really bothered me today. {detail} It was disgusting.",
        "I had an experience that left me feeling uncomfortable. {detail} It was gross.",
        "Something happened that I found revolting. {detail} I'm still feeling disgusted."
    ],
    'neutral': [
        "Today was pretty ordinary. {detail} Nothing particularly exciting happened.",
        "I'm feeling neither good nor bad today. {detail} It's been a neutral day.",
        "Just another day. {detail} I don't have strong feelings one way or the other."
    ],
    'surprise': [
        "Something unexpected happened today! {detail} It really surprised me.",
        "I got some shocking news. {detail} I didn't see it coming at all.",
        "I was caught off guard by {detail}. It was a complete surprise."
    ],
    'contentment': [
        "I'm feeling at peace today. {detail} There's a sense of contentment.",
        "Today was simple but satisfying. {detail} I feel content with how things are.",
        "I have this warm feeling of contentment. {detail} Things feel right."
    ],
    'anxiety': [
        "I can't stop worrying about {detail}. My anxiety is really high.",
        "I'm feeling on edge today. {detail} My anxiety is making it hard to focus.",
        "There's this constant worry about {detail}. The anxiety is overwhelming."
    ],
    'disappointment': [
        "I had higher hopes for today. {detail} I'm feeling disappointed.",
        "Things didn't go as planned. {detail} It's left me feeling disappointed.",
        "I'm disappointed about {detail}. It didn't turn out as I expected."
    ]
}

# Details to insert into templates
DETAILS = {
    'joy': [
        "I got a promotion at work.",
        "My friend threw me a surprise party.",
        "I finished a project I've been working on for months.",
        "I reconnected with an old friend.",
        "I learned something new that really excited me."
    ],
    'sadness': [
        "I missed an important deadline.",
        "I remember a loved one who's no longer here.",
        "I didn't perform as well as I wanted to.",
        "It's raining and gloomy outside.",
        "I'm feeling lonely being away from friends and family."
    ],
    'anger': [
        "someone cut me off in traffic.",
        "my colleague took credit for my work.",
        "I was treated unfairly at the store.",
        "my roommate left a mess again.",
        "I received a rude message from someone."
    ],
    'fear': [
        "an upcoming presentation",
        "my health check results",
        "the economic uncertainty",
        "a big decision I need to make soon",
        "changes happening at work"
    ],
    'disgust': [
        "the state of the public bathroom",
        "how some people treated others at the event",
        "the food that had gone bad in my fridge",
        "the insensitive joke someone made",
        "the way that situation was handled"
    ],
    'neutral': [
        "I went through my usual routine.",
        "I did some errands around town.",
        "I watched a few shows and had dinner.",
        "I caught up on some work and chores.",
        "I took care of some basic tasks."
    ],
    'surprise': [
        "finding money I didn't know I had.",
        "running into an old acquaintance.",
        "getting an unexpected opportunity.",
        "learning something completely unexpected about a friend.",
        "receiving news I wasn't prepared for."
    ],
    'contentment': [
        "I spent time in nature.",
        "I had a quiet evening with a good book.",
        "I enjoyed a simple meal with good company.",
        "I took time to appreciate what I have.",
        "I had a moment of clarity about my life."
    ],
    'anxiety': [
        "an upcoming deadline",
        "the pile of work I need to finish",
        "my financial situation",
        "my relationship issues",
        "health concerns"
    ],
    'disappointment': [
        "not getting the job I interviewed for",
        "the canceled plans I was looking forward to",
        "the poor quality of something I purchased",
        "how a relationship has evolved",
        "my performance in the recent project"
    ]
}

def create_test_users():
    """Create test users in the database if they don't exist"""
    for user in TEST_USERS:
        existing = db.users.find_one({"email": user["email"]})
        if not existing:
            user_data = {
                "email": user["email"],
                "name": user["name"],
                "created_at": datetime.datetime.now(),
                "last_login": datetime.datetime.now(),
                "settings": {
                    "theme": "light",
                    "notifications": True,
                    "privacy": "private"
                }
            }
            db.users.insert_one(user_data)
            print(f"Created user: {user['email']}")
        else:
            print(f"User exists: {user['email']}")

def generate_emotion_data():
    """Generate random emotion data"""
    primary = random.choice(EMOTIONS['primary'])
    secondary = random.choice(EMOTIONS['secondary'])
    intensity = round(random.uniform(0.5, 1.0), 2)
    
    return {
        "primary_emotion": primary,
        "secondary_emotion": secondary,
        "intensity": intensity,
        "valence": random.uniform(-1.0, 1.0) if primary in ['sadness', 'anger', 'fear', 'disgust', 'anxiety', 'disappointment'] else random.uniform(0.0, 1.0),
        "arousal": random.uniform(0.0, 1.0)
    }

def create_emotional_journey(user_email, num_entries=30, days_back=30):
    """
    Create a series of journal entries that form an emotional journey
    
    This will create a somewhat realistic pattern of emotions over time
    """
    print(f"Creating emotional journey for {user_email}...")
    
    # Create a sequence of days going back from today
    today = datetime.datetime.now()
    days = [(today - datetime.timedelta(days=i)) for i in range(days_back)]
    
    # Define some emotional arcs
    # Start neutral, get happier
    if user_email == "test@example.com":
        emotion_sequence = ['neutral'] * 5 + ['contentment'] * 5 + ['joy'] * 5 + \
                          ['surprise', 'joy', 'joy', 'contentment', 'joy'] + \
                          ['joy'] * 5 + ['sadness'] * 3 + ['neutral'] * 2
    # Start happy, experience sadness, recover
    elif user_email == "jane@example.com":
        emotion_sequence = ['joy'] * 5 + ['contentment'] * 3 + ['surprise'] * 2 + \
                          ['sadness'] * 5 + ['fear'] * 3 + ['anxiety'] * 2 + \
                          ['neutral'] * 3 + ['contentment'] * 4 + ['joy'] * 3
    # More volatile emotional pattern
    else:
        emotion_sequence = ['neutral', 'joy', 'anger', 'neutral', 'contentment', 'joy', 'sadness', 
                           'fear', 'neutral', 'joy', 'contentment', 'disgust', 'anger', 'surprise', 
                           'joy', 'anxiety', 'contentment', 'neutral', 'sadness', 'joy',
                           'fear', 'surprise', 'joy', 'contentment', 'neutral', 'joy', 
                           'disappointment', 'anger', 'neutral', 'contentment']
    
    # Ensure we have enough emotions for the number of entries
    while len(emotion_sequence) < num_entries:
        emotion_sequence.append(random.choice(EMOTIONS['primary']))
    
    # Limit to requested number of entries
    emotion_sequence = emotion_sequence[:num_entries]
    
    # Create journal entries
    entries = []
    for i, day in enumerate(days[:num_entries]):
        emotion = emotion_sequence[i]
        # Create 1-3 entries per day
        num_entries_today = random.randint(1, 3)
        
        for j in range(num_entries_today):
            # Space entries throughout the day
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            entry_time = day.replace(hour=hour, minute=minute)
            
            # Select template and detail
            template = random.choice(JOURNAL_TEMPLATES[emotion])
            detail = random.choice(DETAILS[emotion])
            content = template.format(detail=detail)
            
            # Generate emotion data
            emotion_data = generate_emotion_data()
            # Override primary emotion to match sequence
            emotion_data["primary_emotion"] = emotion
            
            entry = {
                "user_email": user_email,
                "content": content,
                "emotion": emotion_data,
                "created_at": entry_time,
                "updated_at": entry_time,
                "isUserMessage": True,
                "tags": [emotion, random.choice(["work", "home", "family", "friends", "health", "personal"])]
            }
            
            entries.append(entry)
    
    # Insert all entries
    if entries:
        db.journal_entries.insert_many(entries)
        print(f"Created {len(entries)} journal entries for {user_email}")
    
    return len(entries)

def create_agent_states():
    """Create initial agent states for test users"""
    for user in TEST_USERS:
        email = user["email"]
        
        # Check if agent state exists
        existing = db.agent_states.find_one({"user_email": email})
        if not existing:
            # Get the most recent emotion for this user
            last_entry = db.journal_entries.find_one(
                {"user_email": email, "isUserMessage": True},
                sort=[("created_at", -1)]
            )
            
            current_emotion = "neutral"
            if last_entry and "emotion" in last_entry and "primary_emotion" in last_entry["emotion"]:
                current_emotion = last_entry["emotion"]["primary_emotion"]
            
            # Create agent state
            state = {
                "user_email": email,
                "current_emotion": current_emotion,
                "target_emotion": "joy" if current_emotion != "joy" else "contentment",
                "action_plan": [],
                "current_action_index": 0,
                "feedback_history": [],
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            
            db.agent_states.insert_one(state)
            print(f"Created agent state for {email}")
        else:
            print(f"Agent state exists for {email}")

def create_emotional_transitions():
    """Create emotional transition records based on journal entries"""
    print("Creating emotional transitions...")
    
    for user in TEST_USERS:
        email = user["email"]
        
        # Get all journal entries for this user sorted by time
        entries = list(db.journal_entries.find(
            {"user_email": email, "isUserMessage": True, "emotion.primary_emotion": {"$exists": True}},
            sort=[("created_at", 1)]
        ))
        
        # Create transitions between consecutive emotions
        transitions = []
        for i in range(1, len(entries)):
            prev_entry = entries[i-1]
            curr_entry = entries[i]
            
            if "emotion" in prev_entry and "primary_emotion" in prev_entry["emotion"] and \
               "emotion" in curr_entry and "primary_emotion" in curr_entry["emotion"]:
                
                from_emotion = prev_entry["emotion"]["primary_emotion"]
                to_emotion = curr_entry["emotion"]["primary_emotion"]
                
                transition = {
                    "user_email": email,
                    "from_emotion": from_emotion,
                    "to_emotion": to_emotion,
                    "timestamp": curr_entry["created_at"],
                    "duration": (curr_entry["created_at"] - prev_entry["created_at"]).total_seconds(),
                    "context": {
                        "tags": curr_entry.get("tags", []),
                        "preceding_entry_id": str(prev_entry["_id"]),
                        "following_entry_id": str(curr_entry["_id"])
                    }
                }
                
                transitions.append(transition)
        
        # Insert transitions
        if transitions:
            db.emotional_transitions.insert_many(transitions)
            print(f"Created {len(transitions)} emotional transitions for {email}")

def clean_test_data():
    """Remove all test data"""
    for user in TEST_USERS:
        email = user["email"]
        
        # Remove journal entries
        result = db.journal_entries.delete_many({"user_email": email})
        print(f"Deleted {result.deleted_count} journal entries for {email}")
        
        # Remove agent states
        result = db.agent_states.delete_many({"user_email": email})
        print(f"Deleted {result.deleted_count} agent states for {email}")
        
        # Remove emotional transitions
        result = db.emotional_transitions.delete_many({"user_email": email})
        print(f"Deleted {result.deleted_count} emotional transitions for {email}")
        
        # Remove user
        result = db.users.delete_many({"email": email})
        print(f"Deleted {result.deleted_count} users with email {email}")

def main():
    """Main function to generate test data"""
    # Check if we should clean data first
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        clean_test_data()
    
    # Create test users
    create_test_users()
    
    # Create journal entries with emotional journeys
    total_entries = 0
    for user in TEST_USERS:
        total_entries += create_emotional_journey(user["email"])
    
    # Create emotional transitions
    create_emotional_transitions()
    
    # Create agent states
    create_agent_states()
    
    print(f"Test data generation complete. Created {total_entries} journal entries for {len(TEST_USERS)} users.")

if __name__ == "__main__":
    main()

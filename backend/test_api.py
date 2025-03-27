"""
Test script for Reflectly API endpoints
This script tests the newly implemented API endpoints
"""
import sys
import os
import requests
import json
import datetime
from pprint import pprint

# API Configuration
BASE_URL = "http://localhost:5004"
USER_EMAIL = "test@example.com"
PASSWORD = "testpassword123"  # For testing purposes only

def create_test_user():
    """Create a test user with known credentials"""
    from pymongo import MongoClient
    import hashlib
    import datetime
    
    # Set up MongoDB connection
    mongo_uri = 'mongodb://localhost:27017/reflectly'
    print(f"Connecting to MongoDB at: {mongo_uri}")
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    # Check if user exists
    user = db.users.find_one({"email": USER_EMAIL})
    
    # Create password hash exactly like in the login endpoint
    hashed_password = hashlib.sha256(PASSWORD.encode()).hexdigest()
    print(f"Generated password hash: {hashed_password}")
    
    if not user:
        # Create user with known password
        user_data = {
            "email": USER_EMAIL,
            "name": "Test User",
            "password": hashed_password,
            "created_at": datetime.datetime.now(),
            "last_login": datetime.datetime.now(),
            "settings": {
                "theme": "light",
                "notifications": True,
                "privacy": "private"
            }
        }
        result = db.users.insert_one(user_data)
        print(f"Created test user: {USER_EMAIL} with ID: {result.inserted_id}")
    else:
        # Update user with new password
        result = db.users.update_one(
            {"email": USER_EMAIL},
            {"$set": {
                "password": hashed_password,
                "last_login": datetime.datetime.now()
            }}
        )
        print(f"Updated password for user: {USER_EMAIL} (modified count: {result.modified_count})")
        
        # Verify the update by retrieving the user again
        updated_user = db.users.find_one({"email": USER_EMAIL})
        if updated_user and updated_user.get("password") == hashed_password:
            print("Password update verified successfully")
        else:
            print("Warning: Password update could not be verified")
    
    # Clean up connection
    client.close()
    return True

def get_auth_token():
    """Get JWT auth token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": USER_EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def test_emotional_journey():
    """Test the emotional journey endpoint"""
    print("\nTesting emotional journey endpoint...")
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test emotional journey")
        return
    
    print(f"Authentication successful, token: {token[:10]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different time periods
    time_periods = ["week", "month", "all"]
    
    for period in time_periods:
        print(f"\nRequesting emotional journey for time period: {period}")
        url = f"{BASE_URL}/api/analyze/emotional-journey?time_period={period}&include_insights=true"
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(
            url,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nEmotional Journey ({period}):")
            print(f"- Number of data points: {len(result.get('data', []))}")
            print(f"- Time period: {result.get('time_period')}")
            if 'insights' in result:
                print(f"- Insights: {len(result.get('insights', []))} provided")
                for i, insight in enumerate(result.get('insights', [])[:2]):
                    print(f"  Insight {i+1}: {insight.get('description')}")
            else:
                print("- No insights provided")
        else:
            print(f"Emotional journey request failed ({period}): {response.text}")

def test_detect_anomalies():
    """Test the anomaly detection endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test anomaly detection")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different sensitivities
    sensitivities = [0.5, 0.7, 0.9]
    
    for sensitivity in sensitivities:
        response = requests.get(
            f"{BASE_URL}/api/detect/anomalies?lookback_period=30&sensitivity={sensitivity}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAnomaly Detection (sensitivity={sensitivity}):")
            print(f"- Number of anomalies: {len(result.get('anomalies', []))}")
            if result.get('anomalies'):
                for i, anomaly in enumerate(result.get('anomalies', [])[:2]):
                    print(f"  Anomaly {i+1}: {anomaly.get('description')} (confidence: {anomaly.get('confidence')})")
        else:
            print(f"Anomaly detection request failed: {response.text}")

def test_predict_emotion():
    """Test the emotion prediction endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test emotion prediction")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different current emotions
    emotions = ["joy", "sadness", "neutral", "anger"]
    
    for emotion in emotions:
        data = {
            "current_emotion": emotion,
            "context": f"The user is feeling {emotion} because of a recent event."
        }
        
        response = requests.post(
            f"{BASE_URL}/api/predict/emotion",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nEmotion Prediction (from {emotion}):")
            print(f"- Next emotion: {result.get('predicted_emotion')}")
            print(f"- Confidence: {result.get('confidence')}")
            print(f"- Top alternatives:")
            for alt in result.get('alternatives', [])[:3]:
                print(f"  - {alt.get('emotion')}: {alt.get('probability')}")
        else:
            print(f"Emotion prediction request failed: {response.text}")

def test_predict_emotional_sequence():
    """Test the emotional sequence prediction endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test sequence prediction")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test sequence prediction with different starting emotions
    emotions = ["joy", "sadness", "anger"]
    
    for emotion in emotions:
        data = {
            "current_emotion": emotion,
            "sequence_length": 5,
            "include_metadata": True,
            "model_type": "markov"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/predict/emotional-sequence",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nEmotional Sequence Prediction (from {emotion}):")
            print(f"- Sequence: {result.get('sequence')}")
            if result.get('probabilities'):
                print(f"- Step probabilities provided: {len(result.get('probabilities'))}")
        else:
            print(f"Sequence prediction request failed: {response.text}")

def test_agent_respond():
    """Test the agent response endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test agent response")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different emotions and inputs
    test_cases = [
        {"emotion": "joy", "input": "I got a promotion today!"},
        {"emotion": "sadness", "input": "I'm feeling down today."},
        {"emotion": "anger", "input": "Someone was rude to me."}
    ]
    
    for case in test_cases:
        data = {
            "user_input": case["input"],
            "current_emotion": case["emotion"],
            "include_agent_state": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agent/respond",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAgent Response (emotion={case['emotion']}):")
            print(f"- Response: {result.get('response')}")
            print(f"- Tags: {result.get('tags')}")
            if result.get('agent_state'):
                print(f"- Agent state included with {len(result.get('agent_state'))} attributes")
        else:
            print(f"Agent response request failed: {response.text}")

def test_interventions_rank():
    """Test the interventions ranking endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test interventions ranking")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different emotions
    emotions = ["joy", "sadness", "anger", "fear", "neutral"]
    
    for emotion in emotions:
        data = {
            "emotion": emotion,
            "target_emotion": "joy" if emotion != "joy" else "contentment",
            "limit": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/interventions/rank",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nInterventions Ranking (from {emotion}):")
            print(f"- Number of interventions: {len(result.get('interventions', []))}")
            if result.get('interventions'):
                for i, intervention in enumerate(result.get('interventions', [])):
                    print(f"  {i+1}. {intervention.get('name')} - {intervention.get('predicted_effectiveness')}")
        else:
            print(f"Interventions ranking request failed: {response.text}")

def test_get_emotional_graph():
    """Test the emotional graph endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test emotional graph")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different parameters
    test_cases = [
        {"include_dataset": False, "include_transitions": True},
        {"include_dataset": True, "include_transitions": True}
    ]
    
    for case in test_cases:
        include_dataset = "true" if case["include_dataset"] else "false"
        include_transitions = "true" if case["include_transitions"] else "false"
        
        response = requests.get(
            f"{BASE_URL}/api/probabilistic/emotional-graph?include_dataset_data={include_dataset}&include_transitions={include_transitions}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nEmotional Graph (dataset={include_dataset}, transitions={include_transitions}):")
            if 'graph' in result:
                print(f"- Graph data retrieved with {len(result['graph'])} attributes")
                if case["include_dataset"] and 'source' in result['graph']:
                    print(f"- Dataset source: {result['graph'].get('source')}")
                    if 'sample_size' in result['graph']:
                        print(f"- Sample size: {result['graph'].get('sample_size')}")
        else:
            print(f"Emotional graph request failed: {response.text}")

def test_search_emotional_path():
    """Test the search for emotional path endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test emotional path search")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different from/to emotion combinations
    test_cases = [
        {"from": "sadness", "to": "joy"},
        {"from": "anger", "to": "contentment"},
        {"from": "fear", "to": "neutral"}
    ]
    
    for case in test_cases:
        data = {
            "from_emotion": case["from"],
            "to_emotion": case["to"],
            "include_actions": True,
            "max_path_length": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/search/emotional-path",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nEmotional Path Search ({case['from']} to {case['to']}):")
            print(f"- Path found: {result.get('success')}")
            if result.get('success'):
                print(f"- Path: {' -> '.join(result.get('path', []))}")
                print(f"- Cost: {result.get('cost')}")
                if 'actions' in result:
                    print(f"- Actions provided: {len(result.get('actions', []))}")
        else:
            print(f"Emotional path search failed: {response.text}")

def test_analyze_decision():
    """Test the decision analysis endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test decision analysis")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with a sample decision
    data = {
        "current_emotion": "neutral",
        "decision": "Should I change jobs?",
        "options": [
            "Stay at current job",
            "Accept the new offer",
            "Continue looking for better opportunities"
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/agent/analyze-decision",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nDecision Analysis:")
        print(f"- Decision: {result.get('decision')}")
        print(f"- Number of options analyzed: {len(result.get('options', []))}")
        if result.get('options'):
            options = result.get('options', [])
            for i, option in enumerate(options):
                # Check if option is a dictionary or string
                if isinstance(option, dict):
                    # It's a dictionary, use .get()
                    print(f"\n  Option {i+1}: {option.get('text', 'No text')}")
                    print(f"  - Emotional outcome: {option.get('predicted_emotion', 'Unknown')}")
                    print(f"  - Confidence: {option.get('confidence', 0.0)}")
                    if 'reasoning' in option:
                        reasoning = option.get('reasoning', '')
                        print(f"  - Reasoning: {reasoning[:50]}..." if reasoning else 'No reasoning')
                else:
                    # It's a string or other type
                    print(f"\n  Option {i+1}: {option}")
                    print(f"  - Details: Limited information available")
    else:
        print(f"Decision analysis request failed: {response.text}")

def test_agent_state():
    """Test the agent state endpoint"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, cannot test agent state")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with different parameters
    test_cases = [
        {"predictions": False, "journey": False, "anomalies": False},
        {"predictions": True, "journey": False, "anomalies": False},
        {"predictions": True, "journey": True, "anomalies": True}
    ]
    
    for i, case in enumerate(test_cases):
        include_predictions = "true" if case["predictions"] else "false"
        include_journey = "true" if case["journey"] else "false"
        include_anomalies = "true" if case["anomalies"] else "false"
        
        response = requests.get(
            f"{BASE_URL}/api/agent/state?include_predictions={include_predictions}&include_journey={include_journey}&include_anomalies={include_anomalies}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAgent State (test case {i+1}):")
            print(f"- Current emotion: {result.get('current_emotion')}")
            print(f"- Target emotion: {result.get('target_emotion')}")
            
            if case["predictions"] and 'predictions' in result:
                print(f"- Predictions included: {len(result.get('predictions', {}))}")
            
            if case["journey"] and 'emotional_journey' in result:
                print(f"- Journey included with {len(result.get('emotional_journey', {}).get('data', []))} data points")
            
            if case["anomalies"] and 'anomalies' in result:
                print(f"- Anomalies included: {len(result.get('anomalies', []))}")
        else:
            print(f"Agent state request failed: {response.text}")

def main():
    """Main function to run all tests"""
    print("=== TESTING REFLECTLY API ENDPOINTS ===")
    print("Setting up test user:", USER_EMAIL)
    
    # Ensure test user exists with known credentials
    create_test_user()
    
    # Uncomment the tests you want to run
    test_emotional_journey()
    test_detect_anomalies()
    test_predict_emotion()
    test_predict_emotional_sequence()
    test_agent_respond()
    test_interventions_rank()
    test_get_emotional_graph()
    test_search_emotional_path()
    test_analyze_decision()
    test_agent_state()
    
    print("\n=== TESTING COMPLETE ===")

if __name__ == "__main__":
    main()

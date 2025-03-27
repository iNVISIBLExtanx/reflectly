"""
Test script for emotional journey endpoint
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5004"
USER_EMAIL = "test@example.com"
PASSWORD = "password123"  # For testing only

def get_auth_token():
    """Get JWT token for authentication"""
    login_url = f"{BASE_URL}/api/auth/login"
    login_data = {
        "email": USER_EMAIL,
        "password": PASSWORD
    }
    
    print(f"Authenticating as {USER_EMAIL}...")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"Authentication failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    token = response.json().get("access_token")
    print(f"Authentication successful")
    return token

def test_emotional_journey():
    """Test emotional journey endpoint"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with all time periods
    time_periods = ["day", "week", "month", "all"]
    
    for period in time_periods:
        print(f"\nTesting emotional journey with time_period={period}, include_insights=True")
        url = f"{BASE_URL}/api/analyze/emotional-journey?time_period={period}&include_insights=true"
        
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Data points: {len(data.get('data', []))}")
            
            if data.get('data'):
                print(f"First data point: {json.dumps(data['data'][0], indent=2)}")
                print(f"Total data points: {len(data['data'])}")
            
            if data.get('insights'):
                print(f"Insights: {json.dumps(data['insights'], indent=2)}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_emotional_journey()

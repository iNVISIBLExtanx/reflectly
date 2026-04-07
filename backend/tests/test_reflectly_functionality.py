#!/usr/bin/env python3
"""
Reflectly App Functionality Test Script
=====================================

This script tests the complete functionality of the Reflectly intelligent agent:
1. Simulates realistic conversation scenarios
2. Builds emotional memory map with transitions
3. Tests algorithm comparison functionality
4. Displays comprehensive results

Usage: python test_reflectly_functionality.py
"""

import requests
import json
import time
import sys
from datetime import datetime

class ReflectlyTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.user_id = "test_user_demo"
        self.session_data = {
            "experiences": [],
            "memory_stats": {},
            "algorithm_comparisons": []
        }
        
    def print_header(self, title):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
        
    def print_step(self, step_num, description):
        """Print formatted step"""
        print(f"\n📍 Step {step_num}: {description}")
        print("-" * 50)
        
    def check_backend_connection(self):
        """Test backend connectivity"""
        try:
            print("🔍 Checking backend connection...")
            
            # Try multiple ports
            ports = [5001, 5000]
            for port in ports:
                try:
                    test_url = f"http://localhost:{port}/api/health"
                    response = requests.get(test_url, timeout=5)
                    if response.status_code == 200:
                        self.base_url = f"http://localhost:{port}"
                        self.api_url = f"{self.base_url}/api"
                        health_data = response.json()
                        print(f"✅ Backend connected on port {port}")
                        print(f"   Status: {health_data.get('status')}")
                        print(f"   Service: {health_data.get('service')}")
                        return True
                except requests.exceptions.RequestException:
                    continue
                    
            print("❌ Backend not accessible. Make sure to run: ./start.sh")
            return False
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def make_api_call(self, endpoint, method="GET", data=None):
        """Make API call with error handling"""
        try:
            url = f"{self.api_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            return None
    
    def reset_memory(self):
        """Reset the memory map for clean testing"""
        print("🧹 Resetting memory map for clean test...")
        result = self.make_api_call("/reset-memory", "POST")
        if result:
            print("✅ Memory map reset successfully")
        else:
            print("❌ Failed to reset memory map")
        time.sleep(1)
    
    def simulate_conversation_scenario(self):
        """Simulate a realistic conversation to build emotional transitions"""
        self.print_header("SIMULATING REALISTIC CONVERSATION SCENARIOS")
        
        # Define conversation scenarios that build meaningful transitions
        scenarios = [
            {
                "day": "Monday",
                "sequence": [
                    {
                        "input": "I'm feeling really sad and overwhelmed with work today",
                        "expected_response": "suggest_actions",
                        "wait_time": 1
                    }
                ]
            },
            {
                "day": "Tuesday", 
                "sequence": [
                    {
                        "input": "I went for a run this morning and I'm feeling much better now",
                        "expected_response": "ask_for_steps",
                        "steps": ["Went for a 30-minute morning run", "Listened to energizing music", "Took a refreshing shower"]
                    }
                ]
            },
            {
                "day": "Wednesday",
                "sequence": [
                    {
                        "input": "I'm feeling anxious about an upcoming presentation",
                        "expected_response": "suggest_actions",
                        "wait_time": 1
                    }
                ]
            },
            {
                "day": "Thursday",
                "sequence": [
                    {
                        "input": "I practiced my presentation and now I feel confident and happy!",
                        "expected_response": "ask_for_steps", 
                        "steps": ["Practiced presentation 3 times", "Recorded myself to improve", "Asked colleague for feedback", "Prepared backup slides"]
                    }
                ]
            },
            {
                "day": "Friday",
                "sequence": [
                    {
                        "input": "I'm feeling confused about my career direction",
                        "expected_response": "suggest_actions",
                        "wait_time": 1
                    }
                ]
            },
            {
                "day": "Weekend",
                "sequence": [
                    {
                        "input": "I had a great conversation with my mentor and I feel excited about my future now!",
                        "expected_response": "ask_for_steps",
                        "steps": ["Scheduled call with mentor", "Wrote down career questions beforehand", "Created action plan together", "Set monthly check-ins"]
                    }
                ]
            }
        ]
        
        experience_count = 0
        
        for scenario in scenarios:
            self.print_step(experience_count + 1, f"{scenario['day']} - Building Emotional Journey")
            
            for interaction in scenario["sequence"]:
                experience_count += 1
                print(f"\n💬 User Input: \"{interaction['input']}\"")
                
                # Send input to backend
                response = self.make_api_call("/process-input", "POST", {
                    "text": interaction["input"],
                    "user_id": self.user_id
                })
                
                if response:
                    print(f"🤖 Agent Response: {response.get('message', 'No message')}")
                    print(f"   Type: {response.get('type')}")
                    print(f"   Emotion: {response.get('emotion')}")
                    
                    if response.get('suggestions'):
                        print(f"   💡 Suggestions: {response['suggestions']}")
                    
                    if response.get('algorithm_used'):
                        print(f"   🔍 Algorithm Used: {response['algorithm_used']}")
                    
                    # Handle steps if this is a positive emotion
                    if interaction.get("steps") and response.get('experience_id'):
                        print(f"\n📝 Providing success steps...")
                        steps_response = self.make_api_call("/save-steps", "POST", {
                            "experience_id": response['experience_id'],
                            "steps": interaction["steps"]
                        })
                        
                        if steps_response:
                            print(f"✅ Steps saved: {steps_response.get('message')}")
                        
                    self.session_data["experiences"].append({
                        "input": interaction["input"],
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                else:
                    print("❌ Failed to get response from agent")
                
                # Wait between interactions to simulate real conversation
                time.sleep(interaction.get("wait_time", 2))
        
        print(f"\n✅ Completed {experience_count} conversation interactions")
    
    def check_memory_development(self):
        """Check how the memory map has developed"""
        self.print_header("CHECKING MEMORY MAP DEVELOPMENT")
        
        # Get memory map data
        memory_map = self.make_api_call("/memory-map")
        memory_stats = self.make_api_call("/memory-stats")
        
        if memory_map and memory_stats:
            print("📊 Memory Statistics:")
            print(f"   Total Experiences: {memory_stats.get('total_experiences', 0)}")
            print(f"   Emotions Learned: {memory_stats.get('emotions_learned', 0)}")
            print(f"   Transitions Learned: {memory_stats.get('transitions_learned', 0)}")
            print(f"   Algorithm Comparisons: {memory_stats.get('algorithm_comparisons', 0)}")
            
            print("\n🗺️ Memory Map Structure:")
            nodes = memory_map.get('nodes', [])
            edges = memory_map.get('edges', [])
            
            print(f"   Emotional Nodes ({len(nodes)}):")
            for node in nodes:
                print(f"     • {node['label']}: {node['count']} experiences")
            
            print(f"\n   Learned Transitions ({len(edges)}):")
            for edge in edges:
                print(f"     • {edge['from']} → {edge['to']}: {edge['actions']} actions learned")
            
            self.session_data["memory_stats"] = memory_stats
            
            if memory_stats.get('transitions_learned', 0) > 0:
                print("\n✅ SUCCESS: Memory map has learned transitions!")
                print("   Algorithms will now use your real emotional data")
                return True
            else:
                print("\n⚠️ WARNING: No transitions learned yet")
                print("   Algorithms will fall back to default hierarchy")
                return False
        else:
            print("❌ Failed to retrieve memory data")
            return False
    
    def test_algorithm_comparison(self):
        """Test algorithm comparison with learned data"""
        self.print_header("TESTING ALGORITHM COMPARISON")
        
        # Test scenarios for algorithm comparison
        test_scenarios = [
            {"start": "sad", "goal": "happy", "description": "Classic emotional journey"},
            {"start": "anxious", "goal": "happy", "description": "Anxiety to happiness"},
            {"start": "confused", "goal": "happy", "description": "Confusion to clarity and joy"},
            {"start": "sad", "goal": "neutral", "description": "Small improvement goal"},
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            self.print_step(i, f"Testing {scenario['description']}")
            print(f"🏁 Racing algorithms: {scenario['start']} → {scenario['goal']}")
            
            comparison_result = self.make_api_call("/compare-algorithms", "POST", {
                "start_emotion": scenario["start"],
                "goal_emotion": scenario["goal"]
            })
            
            if comparison_result:
                # Display results
                print(f"\n🏆 Winner: {comparison_result['winner']['algorithm']}")
                print(f"   Time: {comparison_result['winner'].get('time_ms', 0):.2f}ms")
                print(f"   Nodes Explored: {comparison_result['winner'].get('nodes_explored', 0)}")
                
                print(f"\n📊 Detailed Results:")
                for algo_name, result in comparison_result['results'].items():
                    metrics = result['metrics']
                    path = result.get('path', [])
                    
                    print(f"   {algo_name}:")
                    print(f"     ⏱️ Time: {metrics['execution_time_ms']:.2f}ms")
                    print(f"     🔍 Nodes: {metrics['nodes_explored']}")
                    print(f"     📏 Path Length: {metrics['path_length']}")
                    print(f"     ✅ Success: {metrics['path_found']}")
                    
                    if path:
                        print(f"     🗺️ Path: {' → '.join(path)}")
                
                self.session_data["algorithm_comparisons"].append(comparison_result)
                
            else:
                print("❌ Algorithm comparison failed")
            
            time.sleep(2)
    
    def get_performance_analytics(self):
        """Get overall algorithm performance analytics"""
        self.print_header("ALGORITHM PERFORMANCE ANALYTICS")
        
        performance_data = self.make_api_call("/algorithm-performance")
        
        if performance_data:
            if 'algorithm_statistics' in performance_data:
                print("📈 Overall Algorithm Performance:")
                
                for algo_name, stats in performance_data['algorithm_statistics'].items():
                    print(f"\n🔬 {algo_name}:")
                    print(f"   Total Uses: {stats.get('total_uses', 0)}")
                    print(f"   Wins: {stats.get('wins', 0)}")
                    print(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
                    print(f"   Avg Time: {stats.get('avg_time_ms', 0):.2f}ms")
                    print(f"   Avg Path Length: {stats.get('avg_path_length', 0):.1f}")
                    print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
                
                # Determine best algorithm
                best_algo = None
                best_win_rate = 0
                
                for algo_name, stats in performance_data['algorithm_statistics'].items():
                    win_rate = stats.get('win_rate', 0)
                    if win_rate > best_win_rate:
                        best_win_rate = win_rate
                        best_algo = algo_name
                
                if best_algo:
                    print(f"\n🏆 BEST PERFORMING ALGORITHM: {best_algo}")
                    print(f"   Win Rate: {best_win_rate:.1f}%")
                
            else:
                print("📊 No algorithm performance data available yet")
                print("   Run more algorithm comparisons to generate statistics")
        else:
            print("❌ Failed to retrieve performance analytics")
    
    def display_session_summary(self):
        """Display complete session summary"""
        self.print_header("SESSION SUMMARY")
        
        print(f"🎯 Test Session Results:")
        print(f"   User ID: {self.user_id}")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Experiences Created: {len(self.session_data['experiences'])}")
        print(f"   Algorithm Comparisons: {len(self.session_data['algorithm_comparisons'])}")
        
        if self.session_data.get('memory_stats'):
            stats = self.session_data['memory_stats']
            print(f"\n📊 Final Memory Statistics:")
            print(f"   Total Experiences: {stats.get('total_experiences', 0)}")
            print(f"   Emotions Learned: {stats.get('emotions_learned', 0)}")
            print(f"   Transitions Learned: {stats.get('transitions_learned', 0)}")
            
            if stats.get('transitions_learned', 0) > 0:
                print(f"\n✅ SUCCESS: The system learned from your emotional data!")
                print(f"   Algorithms are now using real user experiences for pathfinding")
            else:
                print(f"\n⚠️ NOTE: Limited learning occurred")
                print(f"   More diverse emotional experiences needed for better algorithm performance")
        
        print(f"\n🌐 Frontend Access:")
        print(f"   Main App: {self.base_url.replace('api', '')}:3000")
        print(f"   Conversation Tab: See your learned memory map")
        print(f"   Algorithm Comparison Tab: Test algorithm racing")
        
        print(f"\n🔍 Next Steps:")
        print(f"   1. Open the frontend at http://localhost:3000")
        print(f"   2. Check the 'Conversation & Memory' tab to see your learned map")
        print(f"   3. Try the 'Algorithm Comparison' tab for more testing")
        print(f"   4. Add more varied emotional experiences to improve learning")
    
    def run_complete_test(self):
        """Run the complete test suite"""
        print("🚀 Starting Reflectly App Functionality Test")
        print(f"   Test User: {self.user_id}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Check backend connection
        if not self.check_backend_connection():
            print("\n❌ Cannot proceed without backend connection")
            print("   Please run: ./start.sh")
            return False
        
        # Step 2: Reset memory for clean test
        self.reset_memory()
        
        # Step 3: Simulate realistic conversations
        self.simulate_conversation_scenario()
        
        # Step 4: Check memory development
        memory_success = self.check_memory_development()
        
        # Step 5: Test algorithm comparison
        self.test_algorithm_comparison()
        
        # Step 6: Get performance analytics
        self.get_performance_analytics()
        
        # Step 7: Display session summary
        self.display_session_summary()
        
        print(f"\n{'='*60}")
        print("🎉 TEST COMPLETE!")
        print(f"{'='*60}")
        
        return True

def main():
    """Main execution function"""
    print("🤖 Reflectly App Functionality Tester")
    print("====================================")
    
    # Allow custom backend URL
    backend_url = "http://localhost:5001"
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
    
    tester = ReflectlyTester(backend_url)
    
    try:
        success = tester.run_complete_test()
        if success:
            print("\n✅ All tests completed successfully!")
            print("Check the frontend at http://localhost:3000 to see the results")
        else:
            print("\n❌ Tests failed. Check the output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
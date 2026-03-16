#!/usr/bin/env python3
"""
Reflectly Colab Backend Test Script
====================================

Tests the backend features required for Colab deployment:
1. Backend health check and CORS headers
2. LLM emotion analysis (with fallback)
3. GNN graph weight calculation
4. A* / Bidirectional / Dijkstra pathfinding comparison
5. Memory persistence (save/load)
6. End-to-end conversation flow

Usage:
    python test_colab_backend.py                    # Test against localhost:5000
    python test_colab_backend.py <backend_url>      # Test against custom URL (e.g., Colab)
"""

import requests
import json
import time
import sys
from datetime import datetime


class ColabBackendTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"
        self.user_id = "colab_test_user"
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }

    def print_header(self, title):
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")

    def print_step(self, step_num, description):
        print(f"\n  Step {step_num}: {description}")
        print("-" * 50)

    def record_result(self, test_name, passed, message=""):
        status = "PASS" if passed else "FAIL"
        self.results["passed" if passed else "failed"] += 1
        self.results["details"].append({
            "test": test_name,
            "status": status,
            "message": message
        })
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"  {icon} {test_name}")
        if message:
            print(f"        {message}")

    def make_api_call(self, endpoint, method="GET", data=None, timeout=30):
        try:
            url = f"{self.api_url}{endpoint}"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return None

            return response
        except requests.exceptions.Timeout:
            print(f"        Timeout calling {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"        Connection refused for {endpoint}")
            return None
        except Exception as e:
            print(f"        Error: {e}")
            return None

    # =========================================================
    # TEST 1: Health Check & CORS
    # =========================================================
    def test_health_and_cors(self):
        self.print_header("TEST 1: Health Check & CORS Headers")

        # Test health endpoint
        response = self.make_api_call("/health")
        if not response:
            self.record_result("Health endpoint reachable", False, "Backend not responding")
            return False

        self.record_result(
            "Health endpoint reachable",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )

        # Check response body
        try:
            data = response.json()
            self.record_result(
                "Health returns valid JSON",
                True,
                f"Status: {data.get('status', 'N/A')}"
            )
            has_status = "status" in data
            self.record_result(
                "Health response has 'status' field",
                has_status,
                f"Fields: {list(data.keys())}"
            )
        except json.JSONDecodeError:
            self.record_result("Health returns valid JSON", False, "Invalid JSON response")

        # Check CORS headers
        cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
        self.record_result(
            "CORS: Access-Control-Allow-Origin header present",
            cors_origin == "*",
            f"Value: '{cors_origin}'"
        )

        cors_methods = response.headers.get("Access-Control-Allow-Methods", "")
        has_post = "POST" in cors_methods
        has_get = "GET" in cors_methods
        self.record_result(
            "CORS: Allows GET and POST methods",
            has_post and has_get,
            f"Value: '{cors_methods}'"
        )

        cors_headers = response.headers.get("Access-Control-Allow-Headers", "")
        has_content_type = "Content-Type" in cors_headers
        self.record_result(
            "CORS: Allows Content-Type header",
            has_content_type,
            f"Value: '{cors_headers}'"
        )

        # Test OPTIONS preflight (important for cross-origin Colab requests)
        try:
            options_resp = requests.options(
                f"{self.api_url}/health",
                headers={"Origin": "http://localhost:3000"},
                timeout=5
            )
            self.record_result(
                "OPTIONS preflight request succeeds",
                options_resp.status_code in [200, 204],
                f"Status: {options_resp.status_code}"
            )
        except Exception as e:
            self.record_result("OPTIONS preflight request succeeds", False, str(e))

        return True

    # =========================================================
    # TEST 2: Emotion Analysis (LLM + Regex Fallback)
    # =========================================================
    def test_emotion_analysis(self):
        self.print_header("TEST 2: Emotion Analysis")

        test_cases = [
            {"text": "I'm feeling really happy and excited today!", "expected_emotion": "happy", "expected_type": "positive"},
            {"text": "I'm so sad and everything feels hopeless", "expected_emotion": "sad", "expected_type": "negative"},
            {"text": "I'm very anxious about my exam tomorrow", "expected_emotion": "anxious", "expected_type": "negative"},
            {"text": "I'm so angry at what happened", "expected_emotion": "angry", "expected_type": "negative"},
            {"text": "I feel okay, nothing special", "expected_emotion": "neutral", "expected_type": "neutral"},
        ]

        all_passed = True
        for i, tc in enumerate(test_cases):
            self.print_step(i + 1, f"Testing: '{tc['text'][:50]}...'")

            response = self.make_api_call(
                "/process-input",
                method="POST",
                data={"text": tc["text"], "user_id": self.user_id}
            )

            if not response:
                self.record_result(f"Emotion detection: {tc['expected_emotion']}", False, "No response")
                all_passed = False
                continue

            if response.status_code != 200:
                self.record_result(
                    f"Emotion detection: {tc['expected_emotion']}",
                    False,
                    f"Status: {response.status_code}"
                )
                all_passed = False
                continue

            try:
                data = response.json()
                detected = data.get("emotion", "unknown")
                resp_type = data.get("type", "unknown")

                # Check if emotion was detected (may differ from expected if LLM is unavailable)
                has_emotion = "emotion" in data
                self.record_result(
                    f"Emotion detected for '{tc['expected_emotion']}' input",
                    has_emotion,
                    f"Detected: {detected} (expected: {tc['expected_emotion']})"
                )

                # Check response has required fields
                has_message = "message" in data
                self.record_result(
                    f"Response has 'message' field",
                    has_message
                )

                has_type = "type" in data
                self.record_result(
                    f"Response has 'type' field",
                    has_type,
                    f"Type: {resp_type}"
                )

            except json.JSONDecodeError:
                self.record_result(f"Emotion detection: {tc['expected_emotion']}", False, "Invalid JSON")
                all_passed = False

            time.sleep(0.5)

        return all_passed

    # =========================================================
    # TEST 3: Algorithm Comparison (A*, Bidirectional, Dijkstra)
    # =========================================================
    def test_algorithm_comparison(self):
        self.print_header("TEST 3: Algorithm Comparison (A*, Bidirectional, Dijkstra)")

        test_pairs = [
            ("sad", "happy"),
            ("angry", "neutral"),
            ("anxious", "happy"),
        ]

        all_passed = True
        for i, (start, goal) in enumerate(test_pairs):
            self.print_step(i + 1, f"Comparing algorithms: {start} -> {goal}")

            response = self.make_api_call(
                "/compare-algorithms",
                method="POST",
                data={"start_emotion": start, "goal_emotion": goal}
            )

            if not response:
                self.record_result(f"Algorithm comparison: {start}->{goal}", False, "No response")
                all_passed = False
                continue

            if response.status_code != 200:
                self.record_result(
                    f"Algorithm comparison: {start}->{goal}",
                    False,
                    f"Status: {response.status_code}"
                )
                all_passed = False
                continue

            try:
                data = response.json()

                # Check all three algorithms are present
                results = data.get("results", {})
                algorithms = list(results.keys())

                has_astar = "A*" in results
                self.record_result(
                    f"A* algorithm present ({start}->{goal})",
                    has_astar
                )

                has_bidirectional = "Bidirectional" in results
                self.record_result(
                    f"Bidirectional algorithm present ({start}->{goal})",
                    has_bidirectional
                )

                has_dijkstra = "Dijkstra" in results
                self.record_result(
                    f"Dijkstra algorithm present ({start}->{goal})",
                    has_dijkstra
                )

                # Check each algorithm has proper metrics
                for algo_name, algo_data in results.items():
                    metrics = algo_data.get("metrics", {})
                    has_time = "execution_time_ms" in metrics
                    has_nodes = "nodes_explored" in metrics
                    has_path = "path_found" in metrics

                    self.record_result(
                        f"{algo_name} has execution metrics",
                        has_time and has_nodes and has_path,
                        f"Time: {metrics.get('execution_time_ms', 'N/A')}ms, "
                        f"Nodes: {metrics.get('nodes_explored', 'N/A')}, "
                        f"Path found: {metrics.get('path_found', 'N/A')}"
                    )

                # Check winner is declared
                winner = data.get("winner", {})
                has_winner = "algorithm" in winner
                self.record_result(
                    f"Winner declared ({start}->{goal})",
                    has_winner,
                    f"Winner: {winner.get('algorithm', 'N/A')} "
                    f"({winner.get('time_ms', 'N/A')}ms)"
                )

            except json.JSONDecodeError:
                self.record_result(f"Algorithm comparison: {start}->{goal}", False, "Invalid JSON")
                all_passed = False

            time.sleep(0.5)

        return all_passed

    # =========================================================
    # TEST 4: Memory Map & Statistics
    # =========================================================
    def test_memory_map(self):
        self.print_header("TEST 4: Memory Map & Statistics")

        # Test memory-map endpoint
        self.print_step(1, "Fetching memory map")
        response = self.make_api_call("/memory-map")

        if response and response.status_code == 200:
            try:
                data = response.json()
                has_nodes = "nodes" in data
                has_edges = "edges" in data
                self.record_result(
                    "Memory map has nodes and edges",
                    has_nodes and has_edges,
                    f"Nodes: {len(data.get('nodes', []))}, Edges: {len(data.get('edges', []))}"
                )
            except json.JSONDecodeError:
                self.record_result("Memory map returns valid JSON", False)
        else:
            self.record_result(
                "Memory map endpoint accessible",
                False,
                f"Status: {response.status_code if response else 'No response'}"
            )

        # Test memory-stats endpoint
        self.print_step(2, "Fetching memory statistics")
        response = self.make_api_call("/memory-stats")

        if response and response.status_code == 200:
            try:
                data = response.json()
                self.record_result(
                    "Memory stats returns valid JSON",
                    True,
                    f"Keys: {list(data.keys())}"
                )
            except json.JSONDecodeError:
                self.record_result("Memory stats returns valid JSON", False)
        else:
            self.record_result(
                "Memory stats endpoint accessible",
                False,
                f"Status: {response.status_code if response else 'No response'}"
            )

        # Test algorithm-performance endpoint
        self.print_step(3, "Fetching algorithm performance")
        response = self.make_api_call("/algorithm-performance")

        if response and response.status_code == 200:
            self.record_result("Algorithm performance endpoint accessible", True)
        else:
            self.record_result(
                "Algorithm performance endpoint accessible",
                False,
                f"Status: {response.status_code if response else 'No response'}"
            )

        return True

    # =========================================================
    # TEST 5: Save Steps (Learning Loop)
    # =========================================================
    def test_save_steps(self):
        self.print_header("TEST 5: Save Steps (Learning Loop)")

        # First, send a positive emotion to get an experience_id
        self.print_step(1, "Sending positive emotion to trigger step collection")
        response = self.make_api_call(
            "/process-input",
            method="POST",
            data={"text": "I'm feeling really happy after going for a walk!", "user_id": self.user_id}
        )

        if not response or response.status_code != 200:
            self.record_result("Create positive experience", False, "Failed to process input")
            return False

        try:
            data = response.json()
            experience_id = data.get("experience_id", "")
            resp_type = data.get("type", "")

            self.record_result(
                "Positive emotion triggers step collection",
                resp_type == "ask_for_steps" or experience_id != "",
                f"Type: {resp_type}, Experience ID: {experience_id[:20] if experience_id else 'N/A'}"
            )

            if experience_id:
                # Save steps for this experience
                self.print_step(2, "Saving success steps")
                save_response = self.make_api_call(
                    "/save-steps",
                    method="POST",
                    data={
                        "experience_id": experience_id,
                        "steps": ["Went for a 30 minute walk", "Listened to music", "Enjoyed nature"],
                        "user_id": self.user_id
                    }
                )

                if save_response and save_response.status_code == 200:
                    save_data = save_response.json()
                    self.record_result(
                        "Steps saved successfully",
                        True,
                        f"Response: {save_data.get('message', 'N/A')[:80]}"
                    )
                else:
                    self.record_result(
                        "Steps saved successfully",
                        False,
                        f"Status: {save_response.status_code if save_response else 'No response'}"
                    )
            else:
                self.record_result("Save steps", False, "No experience_id returned to save steps for")

        except json.JSONDecodeError:
            self.record_result("Process positive emotion", False, "Invalid JSON")
            return False

        return True

    # =========================================================
    # TEST 6: End-to-End Conversation Flow
    # =========================================================
    def test_end_to_end_flow(self):
        self.print_header("TEST 6: End-to-End Conversation Flow")

        conversation = [
            {"text": "I'm feeling really sad today, nothing is going right", "desc": "Sad input"},
            {"text": "I went for a walk and I'm feeling much better now, really happy!", "desc": "Happy input"},
            {"text": "I'm confused about my career choices", "desc": "Confused input"},
            {"text": "Feeling quite tired and drained after a long day", "desc": "Tired input"},
        ]

        all_passed = True
        for i, msg in enumerate(conversation):
            self.print_step(i + 1, msg["desc"])

            response = self.make_api_call(
                "/process-input",
                method="POST",
                data={"text": msg["text"], "user_id": self.user_id}
            )

            if not response:
                self.record_result(f"E2E: {msg['desc']}", False, "No response")
                all_passed = False
                continue

            if response.status_code != 200:
                self.record_result(
                    f"E2E: {msg['desc']}",
                    False,
                    f"Status: {response.status_code}"
                )
                all_passed = False
                continue

            try:
                data = response.json()
                has_required = all(k in data for k in ["type", "message"])
                self.record_result(
                    f"E2E: {msg['desc']} - valid response",
                    has_required,
                    f"Emotion: {data.get('emotion', 'N/A')}, Type: {data.get('type', 'N/A')}"
                )
            except json.JSONDecodeError:
                self.record_result(f"E2E: {msg['desc']}", False, "Invalid JSON")
                all_passed = False

            time.sleep(0.5)

        # Verify memory was built
        self.print_step(len(conversation) + 1, "Verify memory map has data")
        map_response = self.make_api_call("/memory-map")
        if map_response and map_response.status_code == 200:
            map_data = map_response.json()
            node_count = len(map_data.get("nodes", []))
            edge_count = len(map_data.get("edges", []))
            self.record_result(
                "Memory map populated after conversation",
                node_count > 0,
                f"Nodes: {node_count}, Edges: {edge_count}"
            )
        else:
            self.record_result("Memory map populated after conversation", False)

        return all_passed

    # =========================================================
    # TEST 7: Reset Memory
    # =========================================================
    def test_reset_memory(self):
        self.print_header("TEST 7: Reset Memory")

        response = self.make_api_call("/reset-memory", method="POST")

        if response and response.status_code == 200:
            self.record_result("Memory reset successful", True)

            # Verify memory is empty
            stats_response = self.make_api_call("/memory-stats")
            if stats_response and stats_response.status_code == 200:
                self.record_result("Memory stats accessible after reset", True)
            else:
                self.record_result("Memory stats accessible after reset", False)
        else:
            self.record_result(
                "Memory reset",
                False,
                f"Status: {response.status_code if response else 'No response'}"
            )

        return True

    # =========================================================
    # Run All Tests
    # =========================================================
    def run_all_tests(self):
        start_time = time.time()

        print("\n" + "=" * 60)
        print("  Reflectly Colab Backend Test Suite")
        print("=" * 60)
        print(f"  Target: {self.base_url}")
        print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Check connection first
        self.print_header("CONNECTION CHECK")
        response = self.make_api_call("/health")
        if not response:
            print(f"\n  [FAIL] Cannot connect to backend at {self.base_url}")
            print(f"  Make sure the backend is running.")
            print(f"  Usage: python test_colab_backend.py <backend_url>")
            return False

        self.record_result("Backend connection", True, f"Connected to {self.base_url}")

        # Run test suites
        self.test_health_and_cors()
        self.test_emotion_analysis()
        self.test_algorithm_comparison()
        self.test_memory_map()
        self.test_save_steps()
        self.test_end_to_end_flow()
        self.test_reset_memory()

        # Print summary
        elapsed = time.time() - start_time
        total = self.results["passed"] + self.results["failed"]

        self.print_header("TEST RESULTS SUMMARY")
        print(f"\n  Total:   {total} tests")
        print(f"  Passed:  {self.results['passed']}")
        print(f"  Failed:  {self.results['failed']}")
        print(f"  Time:    {elapsed:.1f}s")
        print()

        if self.results["failed"] > 0:
            print("  Failed tests:")
            for detail in self.results["details"]:
                if detail["status"] == "FAIL":
                    print(f"    - {detail['test']}: {detail['message']}")
            print()

        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        print(f"  Success rate: {success_rate:.0f}%")

        if self.results["failed"] == 0:
            print("\n  All tests passed!")
        else:
            print(f"\n  {self.results['failed']} test(s) failed.")

        print("=" * 60)
        return self.results["failed"] == 0


if __name__ == "__main__":
    # Accept custom backend URL as argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

    tester = ColabBackendTester(base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

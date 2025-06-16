#!/usr/bin/env python3
"""
Comprehensive IEMOCAP Validation Test Script
===========================================

This script performs comprehensive testing of the enhanced Reflectly AI system
with IEMOCAP dataset integration. It validates emotion recognition, algorithm
performance, and generates detailed analytics.

Features:
- IEMOCAP dataset processing and validation
- Large-scale algorithm performance testing
- Emotional map generation and validation
- Performance benchmarking and reporting
- Comprehensive analytics and visualization

Usage:
    python comprehensive_test_script.py [options]

Requirements:
    - IEMOCAP dataset (downloaded from Kaggle)
    - Enhanced Reflectly backend running
    - Python packages: requests, pandas, numpy, matplotlib, seaborn
"""

import argparse
import json
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import sys
from collections import defaultdict, Counter
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iemocap_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class IEMOCAPValidationTester:
    """
    Comprehensive validation tester for IEMOCAP integration
    """
    
    def __init__(self, backend_url="http://localhost:5001", dataset_path=None):
        self.backend_url = backend_url
        self.api_url = f"{backend_url}/api"
        self.dataset_path = dataset_path
        self.results = {
            "test_session_id": f"test_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "dataset_validation": {},
            "algorithm_performance": {},
            "emotion_recognition": {},
            "comprehensive_analysis": {},
            "performance_benchmarks": {}
        }
        
        # Test configuration
        self.test_config = {
            "algorithm_tests": 100,
            "emotion_samples": 50,
            "conversation_simulations": 20,
            "benchmark_iterations": 10
        }
        
        logger.info(f"Initialized IEMOCAP Validation Tester")
        logger.info(f"Backend URL: {self.backend_url}")
        logger.info(f"Dataset Path: {self.dataset_path}")
    
    def make_api_call(self, endpoint, method="GET", data=None, timeout=30):
        """Make API call with error handling and retries"""
        url = f"{self.api_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        for attempt in range(3):  # 3 retry attempts
            try:
                if method == "GET":
                    response = requests.get(url, timeout=timeout)
                elif method == "POST":
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # Last attempt
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def check_backend_connection(self):
        """Verify backend is running and accessible"""
        logger.info("Checking backend connection...")
        
        try:
            health_data = self.make_api_call("/health")
            logger.info(f"✅ Backend connected successfully")
            logger.info(f"   Service: {health_data.get('service', 'Unknown')}")
            logger.info(f"   Features: {', '.join(health_data.get('features', []))}")
            logger.info(f"   IEMOCAP Loaded: {health_data.get('iemocap_loaded', False)}")
            
            self.results["backend_info"] = health_data
            return True
            
        except Exception as e:
            logger.error(f"❌ Backend connection failed: {e}")
            return False
    
    def setup_iemocap_dataset(self):
        """Setup and validate IEMOCAP dataset"""
        logger.info("Setting up IEMOCAP dataset...")
        
        if not self.dataset_path or not os.path.exists(self.dataset_path):
            logger.warning("IEMOCAP dataset path not provided or doesn't exist")
            logger.info("Generating synthetic IEMOCAP data for testing...")
            
            # Generate synthetic dataset for testing
            synthetic_data = self.generate_synthetic_iemocap_data()
            synthetic_path = "synthetic_iemocap_validation_data.json"
            
            with open(synthetic_path, 'w') as f:
                json.dump(synthetic_data, f, indent=2)
            
            self.dataset_path = synthetic_path
            logger.info(f"✅ Synthetic dataset created: {synthetic_path}")
        
        # Process dataset
        try:
            from iemocap_loader import IEMOCAPDatasetLoader
            
            loader = IEMOCAPDatasetLoader(os.path.dirname(self.dataset_path))
            
            # For synthetic data, load directly
            if "synthetic" in self.dataset_path:
                with open(self.dataset_path, 'r') as f:
                    validation_data = json.load(f)
            else:
                # Process real IEMOCAP dataset
                if loader.load_dataset() and loader.preprocess_data():
                    validation_data = {
                        "conversations": [],
                        "emotional_map": loader.generate_emotional_map(),
                        "statistics": loader.processed_data
                    }
                    loader.export_for_validation(self.dataset_path)
                else:
                    raise Exception("Failed to process IEMOCAP dataset")
            
            # Load dataset into backend
            load_result = self.make_api_call("/load-iemocap", "POST", {
                "data_path": self.dataset_path
            })
            
            if load_result.get("success"):
                logger.info("✅ IEMOCAP dataset loaded into backend successfully")
                self.results["dataset_validation"] = {
                    "loaded": True,
                    "conversations": load_result.get("conversations", 0),
                    "emotional_map_nodes": load_result.get("emotional_map_nodes", 0),
                    "dataset_path": self.dataset_path
                }
                return True
            else:
                raise Exception("Backend failed to load IEMOCAP dataset")
                
        except Exception as e:
            logger.error(f"❌ Dataset setup failed: {e}")
            self.results["dataset_validation"] = {"loaded": False, "error": str(e)}
            return False
    
    def generate_synthetic_iemocap_data(self):
        """Generate synthetic IEMOCAP-like data for testing"""
        logger.info("Generating synthetic IEMOCAP data...")
        
        emotions = ['angry', 'happy', 'sad', 'neutral', 'anxious', 'confused', 'tired', 'frustrated', 'excited']
        
        # Generate conversations
        conversations = []
        for session_id in range(1, 21):  # 20 sessions
            conversation = {
                "session_id": f"Session{session_id:02d}",
                "turns": []
            }
            
            # Generate 5-15 turns per conversation
            num_turns = np.random.randint(5, 16)
            current_emotion = np.random.choice(emotions)
            
            for turn_id in range(num_turns):
                # Emotion transition logic
                if np.random.random() < 0.3:  # 30% chance to change emotion
                    current_emotion = np.random.choice(emotions)
                
                # Generate text based on emotion
                text_templates = {
                    'angry': [
                        "I'm so frustrated with this situation",
                        "This is making me really angry",
                        "I can't believe this is happening again"
                    ],
                    'happy': [
                        "I'm feeling really good about this",
                        "This makes me so happy and excited",
                        "Everything is going wonderfully today"
                    ],
                    'sad': [
                        "I'm feeling really down about this",
                        "This situation makes me feel sad",
                        "I'm having a difficult time with everything"
                    ],
                    'anxious': [
                        "I'm worried about what might happen",
                        "This is making me feel really nervous",
                        "I can't stop thinking about the worst case scenario"
                    ]
                }
                
                text = np.random.choice(
                    text_templates.get(current_emotion, ["I'm feeling quite neutral about this"])
                )
                
                # Generate actions based on emotion
                action_templates = {
                    'angry': ['complain', 'argue', 'vent', 'express frustration'],
                    'happy': ['celebrate', 'share good news', 'smile', 'laugh'],
                    'sad': ['cry', 'withdraw', 'seek comfort', 'reflect'],
                    'anxious': ['worry', 'pace', 'seek reassurance', 'overthink']
                }
                
                actions = action_templates.get(current_emotion, ['think', 'consider'])
                
                conversation["turns"].append({
                    "text": text,
                    "emotion": current_emotion,
                    "actions": np.random.choice(actions, size=np.random.randint(1, 3)).tolist(),
                    "speaker": f"Speaker{turn_id % 2 + 1}"
                })
            
            conversations.append(conversation)
        
        # Generate emotional map
        emotional_map = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "dataset": "Synthetic IEMOCAP",
                "total_samples": sum(len(conv["turns"]) for conv in conversations),
                "processing_date": datetime.now().isoformat()
            }
        }
        
        # Create nodes
        emotion_counts = Counter()
        for conv in conversations:
            for turn in conv["turns"]:
                emotion_counts[turn["emotion"]] += 1
        
        for emotion, count in emotion_counts.items():
            emotional_map["nodes"].append({
                "id": emotion,
                "label": emotion.title(),
                "count": count,
                "common_actions": list(set(
                    action for conv in conversations 
                    for turn in conv["turns"] 
                    if turn["emotion"] == emotion 
                    for action in turn["actions"]
                ))[:5]
            })
        
        # Create edges (transitions)
        transitions = Counter()
        for conv in conversations:
            turns = conv["turns"]
            for i in range(len(turns) - 1):
                from_emotion = turns[i]["emotion"]
                to_emotion = turns[i + 1]["emotion"]
                if from_emotion != to_emotion:
                    transitions[(from_emotion, to_emotion)] += 1
        
        for (from_emotion, to_emotion), count in transitions.items():
            emotional_map["edges"].append({
                "from": from_emotion,
                "to": to_emotion,
                "weight": count,
                "actions": ["transition_action"]
            })
        
        return {
            "conversations": conversations,
            "emotional_map": emotional_map,
            "statistics": {
                "dataset_stats": {
                    "total_samples": len([turn for conv in conversations for turn in conv["turns"]]),
                    "unique_emotions": len(emotion_counts),
                    "sessions": len(conversations),
                    "speakers": 2
                }
            }
        }
    
    def test_emotion_recognition_accuracy(self):
        """Test emotion recognition accuracy using IEMOCAP data"""
        logger.info("Testing emotion recognition accuracy...")
        
        # Get IEMOCAP stats to access test data
        try:
            iemocap_stats = self.make_api_call("/iemocap-stats")
            
            # Test emotion recognition on sample texts
            test_cases = []
            correct_predictions = 0
            total_predictions = 0
            
            # Use conversations from IEMOCAP data for testing
            if "conversations" in iemocap_stats:
                conversations = iemocap_stats.get("conversations", [])[:5]  # Test first 5 conversations
                
                for conv in conversations:
                    for turn in conv.get("turns", [])[:10]:  # First 10 turns per conversation
                        text = turn.get("text", "")
                        expected_emotion = turn.get("emotion", "neutral")
                        
                        if text.strip():
                            # Process input through backend
                            response = self.make_api_call("/process-input", "POST", {
                                "text": text,
                                "user_id": "validation_test"
                            })
                            
                            predicted_emotion = response.get("emotion", "unknown")
                            confidence = response.get("confidence", 0.0)
                            
                            test_cases.append({
                                "text": text,
                                "expected": expected_emotion,
                                "predicted": predicted_emotion,
                                "confidence": confidence,
                                "correct": expected_emotion == predicted_emotion
                            })
                            
                            if expected_emotion == predicted_emotion:
                                correct_predictions += 1
                            total_predictions += 1
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
            
            self.results["emotion_recognition"] = {
                "total_tests": total_predictions,
                "correct_predictions": correct_predictions,
                "accuracy": accuracy,
                "test_cases": test_cases[:10],  # Store first 10 for analysis
                "emotion_breakdown": self._analyze_emotion_breakdown(test_cases)
            }
            
            logger.info(f"✅ Emotion recognition accuracy: {accuracy:.3f} ({correct_predictions}/{total_predictions})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Emotion recognition testing failed: {e}")
            self.results["emotion_recognition"] = {"error": str(e)}
            return False
    
    def run_algorithm_performance_tests(self):
        """Run comprehensive algorithm performance tests"""
        logger.info("Running algorithm performance tests...")
        
        try:
            # Run large-scale validation
            validation_result = self.make_api_call("/run-validation", "POST", {
                "num_tests": self.test_config["algorithm_tests"]
            }, timeout=300)  # 5 minute timeout for large tests
            
            if validation_result.get("success"):
                validation_data = validation_result["validation_result"]
                
                self.results["algorithm_performance"] = {
                    "validation_completed": True,
                    "total_tests": validation_data["results"]["total_tests"],
                    "algorithm_metrics": validation_data["results"]["average_metrics"],
                    "best_algorithm": validation_data.get("best_algorithm"),
                    "success_rates": {
                        algo: metrics.get("success_rate", 0) 
                        for algo, metrics in validation_data["results"]["average_metrics"].items()
                    },
                    "average_execution_times": {
                        algo: metrics.get("avg_time_ms", 0) 
                        for algo, metrics in validation_data["results"]["average_metrics"].items()
                    }
                }
                
                logger.info(f"✅ Algorithm performance tests completed")
                logger.info(f"   Total tests: {validation_data['results']['total_tests']}")
                
                if validation_data.get("best_algorithm"):
                    best = validation_data["best_algorithm"]
                    logger.info(f"   Best algorithm: {best['algorithm']} (score: {best['score']:.3f})")
                
                return True
            else:
                raise Exception("Validation failed on backend")
                
        except Exception as e:
            logger.error(f"❌ Algorithm performance testing failed: {e}")
            self.results["algorithm_performance"] = {"error": str(e)}
            return False
    
    def run_conversation_simulations(self):
        """Simulate realistic conversations to test system behavior"""
        logger.info("Running conversation simulations...")
        
        conversation_scenarios = [
            {
                "name": "Emotional Journey - Sad to Happy",
                "turns": [
                    "I'm feeling really sad and overwhelmed with work today",
                    "I took your advice and went for a walk, feeling a bit better",
                    "I talked to my friend about my problems and I feel much happier now"
                ]
            },
            {
                "name": "Anxiety Management",
                "turns": [
                    "I'm really anxious about my upcoming presentation",
                    "I practiced the breathing exercises you suggested",
                    "The presentation went well and I feel confident now"
                ]
            },
            {
                "name": "Anger Resolution",
                "turns": [
                    "I'm so angry about what happened at work today",
                    "I wrote down my feelings like you suggested",
                    "I feel calmer now and ready to address the issue constructively"
                ]
            }
        ]
        
        simulation_results = []
        
        try:
            for scenario in conversation_scenarios:
                scenario_result = {
                    "name": scenario["name"],
                    "turns": [],
                    "emotion_progression": [],
                    "algorithm_usage": [],
                    "learning_occurred": False
                }
                
                for turn_text in scenario["turns"]:
                    response = self.make_api_call("/process-input", "POST", {
                        "text": turn_text,
                        "user_id": f"simulation_{scenario['name'].replace(' ', '_')}"
                    })
                    
                    scenario_result["turns"].append({
                        "input": turn_text,
                        "response": response.get("message", ""),
                        "emotion": response.get("emotion", "unknown"),
                        "confidence": response.get("confidence", 0.0),
                        "type": response.get("type", "unknown")
                    })
                    
                    scenario_result["emotion_progression"].append(response.get("emotion", "unknown"))
                    
                    if response.get("algorithm_used"):
                        scenario_result["algorithm_usage"].append(response["algorithm_used"])
                    
                    if response.get("type") in ["ask_for_steps", "learned_automatically"]:
                        scenario_result["learning_occurred"] = True
                    
                    time.sleep(1)  # Small delay between turns
                
                simulation_results.append(scenario_result)
                logger.info(f"   ✅ Completed scenario: {scenario['name']}")
            
            self.results["conversation_simulations"] = {
                "completed": True,
                "scenarios": simulation_results,
                "total_scenarios": len(conversation_scenarios),
                "learning_scenarios": sum(1 for s in simulation_results if s["learning_occurred"]),
                "emotion_transitions": self._analyze_emotion_transitions(simulation_results)
            }
            
            logger.info(f"✅ Conversation simulations completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Conversation simulations failed: {e}")
            self.results["conversation_simulations"] = {"error": str(e)}
            return False
    
    def run_performance_benchmarks(self):
        """Run performance benchmarks for response times and throughput"""
        logger.info("Running performance benchmarks...")
        
        try:
            # Test response times
            response_times = []
            test_inputs = [
                "I'm feeling happy today",
                "I'm really sad about what happened",
                "I'm anxious about the future",
                "I'm angry at the situation",
                "I feel confused and lost"
            ]
            
            for iteration in range(self.test_config["benchmark_iterations"]):
                for test_input in test_inputs:
                    start_time = time.time()
                    
                    response = self.make_api_call("/process-input", "POST", {
                        "text": test_input,
                        "user_id": f"benchmark_user_{iteration}"
                    })
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    response_times.append(response_time)
            
            # Test algorithm comparison performance
            algorithm_times = []
            emotions = ['sad', 'angry', 'anxious', 'confused', 'tired']
            
            for _ in range(self.test_config["benchmark_iterations"]):
                start_emotion = np.random.choice(emotions)
                target_emotion = "happy"
                
                start_time = time.time()
                
                comparison_result = self.make_api_call("/compare-algorithms", "POST", {
                    "start_emotion": start_emotion,
                    "goal_emotion": target_emotion
                })
                
                end_time = time.time()
                algorithm_time = (end_time - start_time) * 1000
                algorithm_times.append(algorithm_time)
            
            self.results["performance_benchmarks"] = {
                "response_times": {
                    "mean": np.mean(response_times),
                    "median": np.median(response_times),
                    "std": np.std(response_times),
                    "min": np.min(response_times),
                    "max": np.max(response_times),
                    "samples": len(response_times)
                },
                "algorithm_times": {
                    "mean": np.mean(algorithm_times),
                    "median": np.median(algorithm_times),
                    "std": np.std(algorithm_times),
                    "min": np.min(algorithm_times),
                    "max": np.max(algorithm_times),
                    "samples": len(algorithm_times)
                },
                "throughput_estimate": 1000 / np.mean(response_times) if response_times else 0  # requests per second
            }
            
            logger.info(f"✅ Performance benchmarks completed")
            logger.info(f"   Average response time: {np.mean(response_times):.2f}ms")
            logger.info(f"   Average algorithm time: {np.mean(algorithm_times):.2f}ms")
            logger.info(f"   Estimated throughput: {self.results['performance_benchmarks']['throughput_estimate']:.2f} req/sec")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance benchmarking failed: {e}")
            self.results["performance_benchmarks"] = {"error": str(e)}
            return False
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        logger.info("Generating comprehensive analysis report...")
        
        try:
            # Calculate overall system score
            scores = []
            
            # Emotion recognition score (0-100)
            if "accuracy" in self.results.get("emotion_recognition", {}):
                emotion_score = self.results["emotion_recognition"]["accuracy"] * 100
                scores.append(("Emotion Recognition", emotion_score))
            
            # Algorithm performance score (based on success rate)
            if "algorithm_performance" in self.results and "success_rates" in self.results["algorithm_performance"]:
                success_rates = self.results["algorithm_performance"]["success_rates"]
                if success_rates:
                    avg_success_rate = np.mean(list(success_rates.values())) * 100
                    scores.append(("Algorithm Performance", avg_success_rate))
            
            # Response time score (inverse of response time, normalized)
            if "response_times" in self.results.get("performance_benchmarks", {}):
                avg_response_time = self.results["performance_benchmarks"]["response_times"]["mean"]
                # Score: 100 - (response_time / 10), capped at 0-100
                response_score = max(0, min(100, 100 - (avg_response_time / 10)))
                scores.append(("Response Time", response_score))
            
            # Learning capability score
            if "conversation_simulations" in self.results:
                learning_rate = self.results["conversation_simulations"].get("learning_scenarios", 0) / \
                               max(1, self.results["conversation_simulations"].get("total_scenarios", 1))
                learning_score = learning_rate * 100
                scores.append(("Learning Capability", learning_score))
            
            overall_score = np.mean([score for _, score in scores]) if scores else 0
            
            self.results["comprehensive_analysis"] = {
                "overall_score": overall_score,
                "component_scores": dict(scores),
                "test_summary": {
                    "total_tests_run": sum([
                        self.results.get("emotion_recognition", {}).get("total_tests", 0),
                        self.results.get("algorithm_performance", {}).get("total_tests", 0),
                        len(self.results.get("conversation_simulations", {}).get("scenarios", [])),
                        self.results.get("performance_benchmarks", {}).get("response_times", {}).get("samples", 0)
                    ]),
                    "tests_passed": sum([
                        1 if "accuracy" in self.results.get("emotion_recognition", {}) else 0,
                        1 if "validation_completed" in self.results.get("algorithm_performance", {}) else 0,
                        1 if "completed" in self.results.get("conversation_simulations", {}) else 0,
                        1 if "response_times" in self.results.get("performance_benchmarks", {}) else 0
                    ]),
                    "dataset_integration": "success" if self.results.get("dataset_validation", {}).get("loaded") else "failed"
                },
                "recommendations": self._generate_recommendations()
            }
            
            logger.info(f"✅ Comprehensive analysis completed")
            logger.info(f"   Overall Score: {overall_score:.1f}/100")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            self.results["comprehensive_analysis"] = {"error": str(e)}
            return False
    
    def _analyze_emotion_breakdown(self, test_cases):
        """Analyze emotion prediction breakdown"""
        emotion_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for case in test_cases:
            expected = case["expected"]
            correct = case["correct"]
            
            emotion_stats[expected]["total"] += 1
            if correct:
                emotion_stats[expected]["correct"] += 1
        
        return {
            emotion: {
                "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
                "correct": stats["correct"],
                "total": stats["total"]
            }
            for emotion, stats in emotion_stats.items()
        }
    
    def _analyze_emotion_transitions(self, simulation_results):
        """Analyze emotion transitions in simulations"""
        transitions = []
        
        for scenario in simulation_results:
            emotions = scenario["emotion_progression"]
            for i in range(len(emotions) - 1):
                transitions.append((emotions[i], emotions[i + 1]))
        
        transition_counts = Counter(transitions)
        return dict(transition_counts)
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Emotion recognition recommendations
        if "emotion_recognition" in self.results:
            accuracy = self.results["emotion_recognition"].get("accuracy", 0)
            if accuracy < 0.7:
                recommendations.append({
                    "category": "Emotion Recognition",
                    "priority": "High",
                    "issue": f"Low accuracy ({accuracy:.2f})",
                    "recommendation": "Consider training with more IEMOCAP data or improving feature extraction"
                })
        
        # Algorithm performance recommendations
        if "algorithm_performance" in self.results:
            success_rates = self.results["algorithm_performance"].get("success_rates", {})
            for algo, rate in success_rates.items():
                if rate < 0.8:
                    recommendations.append({
                        "category": "Algorithm Performance",
                        "priority": "Medium",
                        "issue": f"{algo} low success rate ({rate:.2f})",
                        "recommendation": f"Optimize {algo} implementation or graph connectivity"
                    })
        
        # Performance recommendations
        if "performance_benchmarks" in self.results:
            avg_response_time = self.results["performance_benchmarks"]["response_times"]["mean"]
            if avg_response_time > 1000:  # > 1 second
                recommendations.append({
                    "category": "Performance",
                    "priority": "High",
                    "issue": f"Slow response time ({avg_response_time:.0f}ms)",
                    "recommendation": "Optimize backend processing or consider caching strategies"
                })
        
        return recommendations
    
    def save_results(self, output_file=None):
        """Save test results to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"iemocap_validation_results_{timestamp}.json"
        
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = str(
            datetime.fromisoformat(self.results["end_time"]) - 
            datetime.fromisoformat(self.results["start_time"])
        )
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Results saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return None
    
    def generate_visual_report(self, output_dir="validation_report"):
        """Generate visual report with charts and graphs"""
        logger.info("Generating visual report...")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Set up matplotlib style
            plt.style.use('seaborn-v0_8' if hasattr(plt.style, 'seaborn-v0_8') else 'default')
            
            # 1. Algorithm Performance Comparison
            if "algorithm_performance" in self.results and "success_rates" in self.results["algorithm_performance"]:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                success_rates = self.results["algorithm_performance"]["success_rates"]
                execution_times = self.results["algorithm_performance"]["average_execution_times"]
                
                # Success rates bar chart
                algorithms = list(success_rates.keys())
                rates = [success_rates[algo] * 100 for algo in algorithms]
                
                bars1 = ax1.bar(algorithms, rates, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
                ax1.set_title('Algorithm Success Rates')
                ax1.set_ylabel('Success Rate (%)')
                ax1.set_ylim(0, 100)
                
                # Add value labels on bars
                for bar, rate in zip(bars1, rates):
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                            f'{rate:.1f}%', ha='center', va='bottom')
                
                # Execution times bar chart
                times = [execution_times[algo] for algo in algorithms]
                bars2 = ax2.bar(algorithms, times, color=['#d62728', '#9467bd', '#8c564b'])
                ax2.set_title('Algorithm Execution Times')
                ax2.set_ylabel('Average Time (ms)')
                
                # Add value labels on bars
                for bar, time in zip(bars2, times):
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                            f'{time:.1f}ms', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'algorithm_performance.png'), dpi=300, bbox_inches='tight')
                plt.close()
            
            # 2. Emotion Recognition Breakdown
            if "emotion_recognition" in self.results and "emotion_breakdown" in self.results["emotion_recognition"]:
                breakdown = self.results["emotion_recognition"]["emotion_breakdown"]
                
                emotions = list(breakdown.keys())
                accuracies = [breakdown[emotion]["accuracy"] * 100 for emotion in emotions]
                
                plt.figure(figsize=(10, 6))
                bars = plt.bar(emotions, accuracies, color=plt.cm.viridis(np.linspace(0, 1, len(emotions))))
                plt.title('Emotion Recognition Accuracy by Emotion')
                plt.ylabel('Accuracy (%)')
                plt.xticks(rotation=45)
                plt.ylim(0, 100)
                
                # Add value labels
                for bar, acc in zip(bars, accuracies):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                            f'{acc:.1f}%', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'emotion_recognition_breakdown.png'), dpi=300, bbox_inches='tight')
                plt.close()
            
            # 3. Performance Benchmarks
            if "performance_benchmarks" in self.results:
                benchmarks = self.results["performance_benchmarks"]
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Response time distribution (simulated)
                response_stats = benchmarks["response_times"]
                mean_time = response_stats["mean"]
                std_time = response_stats["std"]
                
                # Generate sample data for visualization
                sample_times = np.random.normal(mean_time, std_time, 100)
                sample_times = np.clip(sample_times, 0, None)  # Ensure positive values
                
                ax1.hist(sample_times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.axvline(mean_time, color='red', linestyle='--', label=f'Mean: {mean_time:.1f}ms')
                ax1.set_title('Response Time Distribution')
                ax1.set_xlabel('Response Time (ms)')
                ax1.set_ylabel('Frequency')
                ax1.legend()
                
                # Algorithm comparison times
                if "algorithm_times" in benchmarks:
                    algo_stats = benchmarks["algorithm_times"]
                    algo_mean = algo_stats["mean"]
                    
                    categories = ['Input Processing', 'Algorithm Comparison']
                    times = [mean_time, algo_mean]
                    
                    bars = ax2.bar(categories, times, color=['lightcoral', 'lightblue'])
                    ax2.set_title('Processing Time Comparison')
                    ax2.set_ylabel('Average Time (ms)')
                    
                    # Add value labels
                    for bar, time in zip(bars, times):
                        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                                f'{time:.1f}ms', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'performance_benchmarks.png'), dpi=300, bbox_inches='tight')
                plt.close()
            
            # 4. Overall System Score
            if "comprehensive_analysis" in self.results:
                analysis = self.results["comprehensive_analysis"]
                
                if "component_scores" in analysis:
                    components = list(analysis["component_scores"].keys())
                    scores = list(analysis["component_scores"].values())
                    
                    plt.figure(figsize=(10, 6))
                    bars = plt.barh(components, scores, color=plt.cm.RdYlGn(np.array(scores)/100))
                    plt.title('System Component Scores')
                    plt.xlabel('Score (0-100)')
                    plt.xlim(0, 100)
                    
                    # Add value labels
                    for bar, score in zip(bars, scores):
                        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                                f'{score:.1f}', ha='left', va='center')
                    
                    # Add overall score
                    overall_score = analysis["overall_score"]
                    plt.figtext(0.5, 0.02, f'Overall System Score: {overall_score:.1f}/100', 
                               ha='center', fontsize=14, fontweight='bold')
                    
                    plt.tight_layout()
                    plt.savefig(os.path.join(output_dir, 'system_scores.png'), dpi=300, bbox_inches='tight')
                    plt.close()
            
            logger.info(f"✅ Visual report generated in {output_dir}/")
            return output_dir
            
        except Exception as e:
            logger.error(f"❌ Failed to generate visual report: {e}")
            return None
    
    def print_summary_report(self):
        """Print a summary report to console"""
        print("\n" + "="*80)
        print("🔬 IEMOCAP VALIDATION TEST RESULTS SUMMARY")
        print("="*80)
        
        # Test session info
        print(f"📅 Test Session: {self.results['test_session_id']}")
        print(f"⏰ Duration: {self.results.get('total_duration', 'N/A')}")
        print(f"🔗 Backend: {self.backend_url}")
        
        # Dataset validation
        dataset = self.results.get("dataset_validation", {})
        if dataset.get("loaded"):
            print(f"✅ Dataset: Loaded ({dataset.get('conversations', 0)} conversations)")
        else:
            print(f"❌ Dataset: Failed to load")
        
        # Emotion recognition
        emotion = self.results.get("emotion_recognition", {})
        if "accuracy" in emotion:
            print(f"🧠 Emotion Recognition: {emotion['accuracy']:.3f} accuracy ({emotion['correct_predictions']}/{emotion['total_tests']})")
        else:
            print(f"❌ Emotion Recognition: Failed")
        
        # Algorithm performance
        algorithm = self.results.get("algorithm_performance", {})
        if "best_algorithm" in algorithm:
            best = algorithm["best_algorithm"]["algorithm"]
            print(f"🏁 Algorithm Performance: Best = {best}")
            for algo, rate in algorithm.get("success_rates", {}).items():
                print(f"   {algo}: {rate:.3f} success rate")
        else:
            print(f"❌ Algorithm Performance: Failed")
        
        # Performance benchmarks
        perf = self.results.get("performance_benchmarks", {})
        if "response_times" in perf:
            avg_time = perf["response_times"]["mean"]
            throughput = perf.get("throughput_estimate", 0)
            print(f"⚡ Performance: {avg_time:.1f}ms avg response, {throughput:.1f} req/sec throughput")
        else:
            print(f"❌ Performance: Failed")
        
        # Overall score
        analysis = self.results.get("comprehensive_analysis", {})
        if "overall_score" in analysis:
            score = analysis["overall_score"]
            print(f"📊 Overall Score: {score:.1f}/100")
            
            # Recommendations
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations ({len(recommendations)}):")
                for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                    print(f"   {i}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
        else:
            print(f"❌ Overall Analysis: Failed")
        
        print("="*80 + "\n")
    
    def run_full_validation(self):
        """Run the complete validation test suite"""
        logger.info("🚀 Starting comprehensive IEMOCAP validation test suite")
        
        # Test steps
        test_steps = [
            ("Backend Connection", self.check_backend_connection),
            ("IEMOCAP Dataset Setup", self.setup_iemocap_dataset),
            ("Emotion Recognition Testing", self.test_emotion_recognition_accuracy),
            ("Algorithm Performance Testing", self.run_algorithm_performance_tests),
            ("Conversation Simulations", self.run_conversation_simulations),
            ("Performance Benchmarking", self.run_performance_benchmarks),
            ("Comprehensive Analysis", self.generate_comprehensive_report)
        ]
        
        # Execute test steps
        passed_tests = 0
        total_tests = len(test_steps)
        
        for step_name, step_function in test_steps:
            logger.info(f"🔄 Running: {step_name}")
            try:
                if step_function():
                    logger.info(f"✅ {step_name} - PASSED")
                    passed_tests += 1
                else:
                    logger.error(f"❌ {step_name} - FAILED")
            except Exception as e:
                logger.error(f"❌ {step_name} - ERROR: {e}")
        
        # Generate reports
        logger.info("📊 Generating reports...")
        results_file = self.save_results()
        visual_report_dir = self.generate_visual_report()
        
        # Print summary
        self.print_summary_report()
        
        # Final status
        success_rate = passed_tests / total_tests
        if success_rate >= 0.8:
            logger.info(f"🎉 VALIDATION SUCCESSFUL: {passed_tests}/{total_tests} tests passed")
        elif success_rate >= 0.6:
            logger.warning(f"⚠️  VALIDATION PARTIAL: {passed_tests}/{total_tests} tests passed")
        else:
            logger.error(f"💥 VALIDATION FAILED: {passed_tests}/{total_tests} tests passed")
        
        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results_file": results_file,
            "visual_report": visual_report_dir,
            "results": self.results
        }

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="IEMOCAP Validation Test Script")
    parser.add_argument("--backend-url", default="http://localhost:5001", 
                       help="Backend URL (default: http://localhost:5001)")
    parser.add_argument("--dataset-path", 
                       help="Path to IEMOCAP validation data JSON file")
    parser.add_argument("--algorithm-tests", type=int, default=100,
                       help="Number of algorithm performance tests (default: 100)")
    parser.add_argument("--output-dir", default="validation_results",
                       help="Output directory for results (default: validation_results)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize tester
    tester = IEMOCAPValidationTester(
        backend_url=args.backend_url,
        dataset_path=args.dataset_path
    )
    
    # Update test configuration
    tester.test_config["algorithm_tests"] = args.algorithm_tests
    
    try:
        # Run validation
        results = tester.run_full_validation()
        
        # Move results to output directory
        if results["results_file"]:
            import shutil
            shutil.move(results["results_file"], 
                       os.path.join(args.output_dir, os.path.basename(results["results_file"])))
        
        if results["visual_report"]:
            if results["visual_report"] != args.output_dir:
                shutil.move(results["visual_report"], args.output_dir)
        
        print(f"\n📁 All results saved to: {args.output_dir}")
        
        # Exit with appropriate code
        sys.exit(0 if results["success_rate"] >= 0.8 else 1)
        
    except KeyboardInterrupt:
        logger.info("❌ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
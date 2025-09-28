#!/usr/bin/env python3
"""
Comprehensive Demo Agent Testing Script for All Omnizon Tasks

This script tests the Demo Agent on all 10 Omnizon tasks to evaluate
its performance on e-commerce scenarios similar to Amazon.

Tasks tested:
- omnizon-1 through omnizon-10 (Easy, Medium, Hard difficulty levels)
- Various e-commerce scenarios: search, browse, purchase, compare products
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import agisdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agisdk import REAL
    from agisdk.REAL.demo_agent.basic_agent import DemoAgent, DemoAgentArgs
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and agisdk is installed")
    sys.exit(1)

class DemoAgentOmnizonTestSuite:
    """Test suite for running Demo Agent on all Omnizon tasks."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # All Omnizon tasks with their details
        self.omnizon_tasks = {
            "webclones.omnizon-1": {
                "goal": "Search for 'laptop' and display first result",
                "difficulty": "easy",
                "type": "action"
            },
            "webclones.omnizon-2": {
                "goal": "Search smartphones, add first two to cart, buy third",
                "difficulty": "medium", 
                "type": "action"
            },
            "webclones.omnizon-3": {
                "goal": "Browse Headphones category and retrieve listings",
                "difficulty": "easy",
                "type": "retrieval"
            },
            "webclones.omnizon-4": {
                "goal": "Add Marshall speaker + Michael Kors watch, checkout",
                "difficulty": "hard",
                "type": "action"
            },
            "webclones.omnizon-5": {
                "goal": "Search KTC Gaming Monitor and display specs",
                "difficulty": "hard",
                "type": "action"
            },
            "webclones.omnizon-6": {
                "goal": "Compare Samsung phones, buy better value",
                "difficulty": "hard",
                "type": "retrieval-action"
            },
            "webclones.omnizon-7": {
                "goal": "Find most expensive product in Gaming category",
                "difficulty": "medium",
                "type": "action"
            },
            "webclones.omnizon-8": {
                "goal": "Search Espresso Machine, buy cheapest with quantity 5",
                "difficulty": "easy",
                "type": "retrieval-action"
            },
            "webclones.omnizon-9": {
                "goal": "Buy PlayStation DualSense with custom payment method",
                "difficulty": "hard",
                "type": "action"
            },
            "webclones.omnizon-10": {
                "goal": "Buy any product with max quantity and latest delivery",
                "difficulty": "hard",
                "type": "action"
            }
        }

    def run_single_omnizon_task(self, task_name: str) -> Dict[str, Any]:
        """Run a single Omnizon task and return results."""
        print(f"\n🚀 Running {task_name}")
        print(f"   Goal: {self.omnizon_tasks[task_name]['goal']}")
        print(f"   Difficulty: {self.omnizon_tasks[task_name]['difficulty'].upper()}")
        
        task_start = time.time()
        
        try:
            # Create Demo Agent args with proper configuration (similar to harness)
            agent_args = DemoAgentArgs(
                model_name="gpt-4o",
                chat_mode=False,
                demo_mode="default",
                use_html=False,
                use_axtree=True,
                use_screenshot=True,  # Enable screenshots like the harness does
                system_message_handling="separate"
            )
            
            # Create harness for single task
            harness = REAL.harness(
                agentargs=agent_args,
                headless=True,
                task_name=task_name,
                sample_tasks=1,
                max_steps=25  # Allow more steps for complex tasks
            )
            
            # Run the task
            results = harness.run()
            
            task_duration = time.time() - task_start
            
            # Extract key metrics from results
            if results and len(results) > 0:
                # harness.run() returns a dict indexed by task name
                result = results[task_name]
                # Determine success based on cum_reward
                score = result.get('cum_reward', 0.0)
                success = score == 1.0
                steps_taken = result.get('n_steps', 0)
                
                # Try to extract actions from experiment directory
                actions_extracted = 0
                exp_dir = result.get('exp_dir', '')
                if exp_dir and os.path.exists(exp_dir):
                    # Count step files to determine actions taken
                    step_files = [f for f in os.listdir(exp_dir) if f.startswith('step_') and f.endswith('.pkl.gz')]
                    actions_extracted = len(step_files)
                
                return {
                    'task_name': task_name,
                    'goal': self.omnizon_tasks[task_name]['goal'],
                    'difficulty': self.omnizon_tasks[task_name]['difficulty'],
                    'success': success,
                    'score': score,
                    'steps_taken': steps_taken,
                    'actions_extracted': actions_extracted,
                    'duration': task_duration,
                    'error_msg': None,
                    'timestamp': datetime.now().isoformat(),
                    'exp_dir': exp_dir
                }
            else:
                return {
                    'task_name': task_name,
                    'goal': self.omnizon_tasks[task_name]['goal'],
                    'difficulty': self.omnizon_tasks[task_name]['difficulty'],
                    'success': False,
                    'score': 0.0,
                    'steps_taken': 0,
                    'actions_extracted': 0,
                    'duration': task_duration,
                    'error_msg': "No results returned from harness",
                    'timestamp': datetime.now().isoformat(),
                    'exp_dir': ''
                }
                
        except Exception as e:
            task_duration = time.time() - task_start
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            
            return {
                'task_name': task_name,
                'goal': self.omnizon_tasks[task_name]['goal'],
                'difficulty': self.omnizon_tasks[task_name]['difficulty'],
                'success': False,
                'score': 0.0,
                'steps_taken': 0,
                'actions_extracted': 0,
                'duration': task_duration,
                'error_msg': error_msg,
                'timestamp': datetime.now().isoformat(),
                'exp_dir': ''
            }

    def run_all_tasks(self) -> List[Dict[str, Any]]:
        """Run all Omnizon tasks and return comprehensive results."""
        print("🎯 Demo Agent - Complete Omnizon Test Suite")
        print("=" * 60)
        print(f"Testing {len(self.omnizon_tasks)} Omnizon tasks")
        print(f"Agent: Demo Agent (gpt-4o)")
        print(f"Configuration: Screenshots=True, AXTree=True, Demo Mode=default")
        print("=" * 60)
        
        self.start_time = time.time()
        
        for i, task_name in enumerate(self.omnizon_tasks.keys(), 1):
            print(f"\n📋 Task {i}/{len(self.omnizon_tasks)}: {task_name}")
            result = self.run_single_omnizon_task(task_name)
            self.results.append(result)
            
            # Print immediate result
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"   {status} - Score: {result['score']:.2f}, Steps: {result['steps_taken']}, Duration: {result['duration']:.1f}s")
            
            # Small delay between tasks to avoid rate limiting
            if i < len(self.omnizon_tasks):
                print("   ⏳ Waiting 3 seconds before next task...")
                time.sleep(3)
        
        self.end_time = time.time()
        return self.results

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze and summarize the test results."""
        if not self.results:
            return {}
        
        total_tasks = len(self.results)
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        successful_tasks = len(successful_results)
        
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        avg_duration = sum(r['duration'] for r in self.results) / len(self.results)
        
        # Analyze by difficulty
        difficulty_stats = {}
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_results = [r for r in self.results if r['difficulty'] == difficulty]
            if difficulty_results:
                difficulty_successful = len([r for r in difficulty_results if r['success']])
                difficulty_stats[difficulty] = {
                    'total': len(difficulty_results),
                    'successful': difficulty_successful,
                    'success_rate': (difficulty_successful / len(difficulty_results)) * 100,
                    'avg_duration': sum(r['duration'] for r in difficulty_results) / len(difficulty_results)
                }
        
        return {
            'agent': 'Demo Agent (gpt-4o)',
            'test_completed': datetime.now().isoformat(),
            'summary': {
                'total_tasks': total_tasks,
                'successful_tasks': successful_tasks,
                'failed_tasks': total_tasks - successful_tasks,
                'success_rate': round(success_rate, 2),
                'total_duration': round(total_duration, 2),
                'avg_duration_per_task': round(avg_duration, 2)
            },
            'difficulty_breakdown': difficulty_stats,
            'successful_tasks': [r['task_name'] for r in successful_results],
            'failed_tasks': [r['task_name'] for r in failed_results],
            'detailed_results': self.results
        }

    def save_results(self, analysis: Dict[str, Any]):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_agent_all_omnizon_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

    def print_final_summary(self, analysis: Dict[str, Any]):
        """Print a comprehensive final summary."""
        print("\n" + "=" * 80)
        print("🏁 DEMO AGENT - FINAL OMNIZON TEST RESULTS")
        print("=" * 80)
        
        summary = analysis['summary']
        print(f"📊 Overall Performance:")
        print(f"   • Total Tasks: {summary['total_tasks']}")
        print(f"   • Successful: {summary['successful_tasks']}")
        print(f"   • Failed: {summary['failed_tasks']}")
        print(f"   • Success Rate: {summary['success_rate']}%")
        print(f"   • Total Duration: {summary['total_duration']:.1f} seconds")
        print(f"   • Average per Task: {summary['avg_duration_per_task']:.1f} seconds")
        
        print(f"\n📈 Performance by Difficulty:")
        for difficulty, stats in analysis['difficulty_breakdown'].items():
            print(f"   • {difficulty.upper()}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        if analysis['successful_tasks']:
            print(f"\n✅ Successful Tasks ({len(analysis['successful_tasks'])}):")
            for task in analysis['successful_tasks']:
                print(f"   • {task}")
        
        if analysis['failed_tasks']:
            print(f"\n❌ Failed Tasks ({len(analysis['failed_tasks'])}):")
            for task in analysis['failed_tasks']:
                print(f"   • {task}")
        
        print("=" * 80)

def main():
    """Main function to run the comprehensive test suite."""
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("🔑 API key found - proceeding with tests")
    
    # Create and run test suite
    test_suite = DemoAgentOmnizonTestSuite()
    
    try:
        # Run all tasks
        results = test_suite.run_all_tasks()
        
        # Analyze results
        analysis = test_suite.analyze_results()
        
        # Save results
        filename = test_suite.save_results(analysis)
        
        # Print final summary
        test_suite.print_final_summary(analysis)
        
        print(f"\n🎉 Testing complete! Results saved to {filename}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        if test_suite.results:
            analysis = test_suite.analyze_results()
            filename = test_suite.save_results(analysis)
            print(f"Partial results saved to {filename}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        if test_suite.results:
            analysis = test_suite.analyze_results()
            filename = test_suite.save_results(analysis)
            print(f"Partial results saved to {filename}")

if __name__ == "__main__":
    main()
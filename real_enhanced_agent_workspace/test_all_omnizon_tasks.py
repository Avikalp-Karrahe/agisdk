#!/usr/bin/env python3
"""
Comprehensive Omnizon Task Testing Script for RealEnhancedAgent

This script tests the RealEnhancedAgent on all 10 Omnizon tasks to evaluate
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
    from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and agisdk is installed")
    sys.exit(1)

class OmnizonTestSuite:
    """Test suite for running RealEnhancedAgent on all Omnizon tasks."""
    
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
            # Create RealEnhancedAgent args
            agent_args = RealEnhancedAgentArgs(
                model_name="claude-3-5-sonnet-20241022",
                enhanced_selection=True,
                timeout_ms=45000,  # 45 seconds for complex tasks
                retry_attempts=3
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
                result = results[0]
                success = result.get('success', False)
                score = result.get('reward', 0.0)
                steps_taken = result.get('n_steps', 0)
                error_msg = result.get('err_msg', '')
            else:
                success = False
                score = 0.0
                steps_taken = 0
                error_msg = "No results returned"
            
            task_result = {
                'task_name': task_name,
                'goal': self.omnizon_tasks[task_name]['goal'],
                'difficulty': self.omnizon_tasks[task_name]['difficulty'],
                'success': success,
                'score': score,
                'steps_taken': steps_taken,
                'duration': round(task_duration, 2),
                'error_msg': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            
            # Print immediate results
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   Result: {status}")
            print(f"   Score: {score}")
            print(f"   Steps: {steps_taken}")
            print(f"   Duration: {task_duration:.2f}s")
            if error_msg:
                print(f"   Error: {error_msg[:100]}...")
            
            return task_result
            
        except Exception as e:
            task_duration = time.time() - task_start
            error_result = {
                'task_name': task_name,
                'goal': self.omnizon_tasks[task_name]['goal'],
                'difficulty': self.omnizon_tasks[task_name]['difficulty'],
                'success': False,
                'score': 0.0,
                'steps_taken': 0,
                'duration': round(task_duration, 2),
                'error_msg': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   Result: ❌ EXCEPTION")
            print(f"   Error: {str(e)[:100]}...")
            print(f"   Duration: {task_duration:.2f}s")
            
            return error_result
    
    def run_all_tasks(self) -> List[Dict[str, Any]]:
        """Run all Omnizon tasks and return comprehensive results."""
        print("🎯 RealEnhancedAgent - Complete Omnizon Test Suite")
        print("=" * 60)
        print(f"Testing {len(self.omnizon_tasks)} Omnizon tasks")
        print(f"Agent: RealEnhancedAgent with enhanced features")
        print(f"Model: claude-3-5-sonnet-20241022")
        print("=" * 60)
        
        self.start_time = time.time()
        
        for i, task_name in enumerate(self.omnizon_tasks.keys(), 1):
            print(f"\n📋 Task {i}/{len(self.omnizon_tasks)}: {task_name}")
            result = self.run_single_omnizon_task(task_name)
            self.results.append(result)
            
            # Small delay between tasks to avoid rate limiting
            if i < len(self.omnizon_tasks):
                print("   ⏳ Waiting 3 seconds before next task...")
                time.sleep(3)
        
        self.end_time = time.time()
        return self.results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze and summarize test results."""
        if not self.results:
            return {}
        
        total_tasks = len(self.results)
        successful_tasks = sum(1 for r in self.results if r['success'])
        success_rate = (successful_tasks / total_tasks) * 100
        
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        avg_duration = sum(r['duration'] for r in self.results) / total_tasks
        
        # Analyze by difficulty
        difficulty_stats = {}
        for difficulty in ['easy', 'medium', 'hard']:
            diff_tasks = [r for r in self.results if r['difficulty'] == difficulty]
            if diff_tasks:
                diff_success = sum(1 for r in diff_tasks if r['success'])
                difficulty_stats[difficulty] = {
                    'total': len(diff_tasks),
                    'successful': diff_success,
                    'success_rate': (diff_success / len(diff_tasks)) * 100,
                    'avg_duration': sum(r['duration'] for r in diff_tasks) / len(diff_tasks)
                }
        
        # Find best and worst performing tasks
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        analysis = {
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
        
        return analysis
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print a comprehensive summary of test results."""
        print("\n" + "=" * 60)
        print("📊 OMNIZON TEST RESULTS SUMMARY")
        print("=" * 60)
        
        summary = analysis['summary']
        print(f"🎯 Overall Performance:")
        print(f"   Total Tasks: {summary['total_tasks']}")
        print(f"   Successful: {summary['successful_tasks']} ✅")
        print(f"   Failed: {summary['failed_tasks']} ❌")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Total Duration: {summary['total_duration']:.2f}s")
        print(f"   Avg Duration/Task: {summary['avg_duration_per_task']:.2f}s")
        
        print(f"\n📈 Performance by Difficulty:")
        for difficulty, stats in analysis['difficulty_breakdown'].items():
            print(f"   {difficulty.upper()}: {stats['successful']}/{stats['total']} "
                  f"({stats['success_rate']:.1f}%) - "
                  f"Avg: {stats['avg_duration']:.2f}s")
        
        if analysis['successful_tasks']:
            print(f"\n✅ Successful Tasks ({len(analysis['successful_tasks'])}):")
            for task in analysis['successful_tasks']:
                task_info = next(r for r in self.results if r['task_name'] == task)
                print(f"   • {task} ({task_info['difficulty']}) - {task_info['duration']:.2f}s")
        
        if analysis['failed_tasks']:
            print(f"\n❌ Failed Tasks ({len(analysis['failed_tasks'])}):")
            for task in analysis['failed_tasks']:
                task_info = next(r for r in self.results if r['task_name'] == task)
                error_preview = task_info['error_msg'][:50] + "..." if len(task_info['error_msg']) > 50 else task_info['error_msg']
                print(f"   • {task} ({task_info['difficulty']}) - {error_preview}")
        
        print("\n" + "=" * 60)
    
    def save_results(self, filename: Optional[str] = None):
        """Save detailed results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"omnizon_test_results_{timestamp}.json"
        
        analysis = self.analyze_results()
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
        return filename

def main():
    """Main function to run the complete Omnizon test suite."""
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Initialize and run test suite
    test_suite = OmnizonTestSuite()
    
    try:
        # Run all tasks
        results = test_suite.run_all_tasks()
        
        # Analyze and display results
        analysis = test_suite.analyze_results()
        test_suite.print_summary(analysis)
        
        # Save results
        results_file = test_suite.save_results()
        
        # Final status
        success_rate = analysis['summary']['success_rate']
        if success_rate == 100:
            print(f"\n🎉 PERFECT SCORE! RealEnhancedAgent achieved 100% success rate!")
        elif success_rate >= 80:
            print(f"\n🌟 EXCELLENT! RealEnhancedAgent achieved {success_rate}% success rate!")
        elif success_rate >= 60:
            print(f"\n👍 GOOD! RealEnhancedAgent achieved {success_rate}% success rate!")
        else:
            print(f"\n⚠️  RealEnhancedAgent achieved {success_rate}% success rate - room for improvement")
        
        return analysis
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        if test_suite.results:
            print("Partial results available:")
            analysis = test_suite.analyze_results()
            test_suite.print_summary(analysis)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return None

if __name__ == "__main__":
    main()
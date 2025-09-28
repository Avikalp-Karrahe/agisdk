#!/usr/bin/env python3
"""
Test script to run specific Omnizon tasks with GUI enabled for debugging
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agisdk import REAL
    from agisdk.REAL.demo_agent.basic_agent import DemoAgent, DemoAgentArgs
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and agisdk is installed")
    sys.exit(1)

class SpecificOmnizonTestSuite:
    """Test suite for running specific Omnizon tasks with GUI enabled"""
    
    def __init__(self):
        self.omnizon_tasks = {
            'webclones.omnizon-6': {
                'goal': 'Compare SAMSUNG Galaxy S24 Ultra and SAMSUNG Galaxy Z Fold 6, buy the better one',
                'difficulty': 'HARD'
            },
            'webclones.omnizon-9': {
                'goal': 'Buy PlayStation DualSense with custom payment method',
                'difficulty': 'HARD'
            }
        }

    def run_single_omnizon_task(self, task_name: str) -> Dict[str, Any]:
        """Run a single Omnizon task with GUI enabled"""
        print(f"\n🚀 Running {task_name}")
        print(f"   Goal: {self.omnizon_tasks[task_name]['goal']}")
        print(f"   Difficulty: {self.omnizon_tasks[task_name]['difficulty']}")
        
        task_start = time.time()
        
        try:
            # Create demo agent with GUI enabled (headless=False)
            harness = REAL.harness(
                agentargs=DemoAgentArgs(),
                task_name=task_name,
                headless=False,  # Enable GUI for debugging
                use_cache=False,  # Force fresh run
                force_refresh=True,  # Force refresh
                max_steps=30  # Allow more steps for complex tasks
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
                    'error_msg': 'No results returned from harness',
                    'timestamp': datetime.now().isoformat(),
                    'exp_dir': ''
                }
                
        except Exception as e:
            task_duration = time.time() - task_start
            error_msg = f"Exception during task execution: {str(e)}"
            print(f"❌ Error in {task_name}: {error_msg}")
            
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

    def run_specific_tasks(self) -> List[Dict[str, Any]]:
        """Run the specific tasks with GUI enabled"""
        print("🎯 Starting Specific Omnizon Tasks Test Suite with GUI")
        print("=" * 60)
        
        results = []
        task_names = ['webclones.omnizon-6', 'webclones.omnizon-9']
        
        for i, task_name in enumerate(task_names, 1):
            print(f"\n📋 Task {i}/{len(task_names)}: {task_name}")
            
            result = self.run_single_omnizon_task(task_name)
            results.append(result)
            
            # Print immediate result
            if result['success']:
                print(f"   ✅ SUCCESS - Score: {result['score']:.2f}, Steps: {result['steps_taken']}, Duration: {result['duration']:.1f}s")
            else:
                print(f"   ❌ FAILED - Score: {result['score']:.2f}, Duration: {result['duration']:.1f}s")
                if result['error_msg']:
                    print(f"   Error: {result['error_msg']}")
            
            # Wait between tasks
            if i < len(task_names):
                print("   ⏳ Waiting 5 seconds before next task...")
                time.sleep(5)
        
        return results

    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the test results"""
        if not results:
            return {'error': 'No results to analyze'}
        
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r['success'])
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Calculate timing statistics
        durations = [r['duration'] for r in results]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Analyze by difficulty
        difficulty_stats = {}
        for result in results:
            difficulty = result['difficulty']
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {'total': 0, 'success': 0}
            
            difficulty_stats[difficulty]['total'] += 1
            if result['success']:
                difficulty_stats[difficulty]['success'] += 1
        
        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': success_rate,
            'average_duration': avg_duration,
            'difficulty_breakdown': {
                difficulty: {
                    'success_rate': (stats['success'] / stats['total']) * 100,
                    'tasks': f"{stats['success']}/{stats['total']}"
                }
                for difficulty, stats in difficulty_stats.items()
            }
        }

    def save_results(self, results: List[Dict[str, Any]], analysis: Dict[str, Any]):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"specific_omnizon_gui_results_{timestamp}.json"
        
        output_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'specific_omnizon_gui_test',
                'tasks_tested': ['webclones.omnizon-6', 'webclones.omnizon-9'],
                'gui_enabled': True
            },
            'analysis': analysis,
            'detailed_results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

    def print_final_summary(self, analysis: Dict[str, Any]):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("🎯 SPECIFIC OMNIZON TASKS TEST SUMMARY (GUI ENABLED)")
        print("=" * 60)
        
        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return
        
        print(f"📊 Overall Results:")
        print(f"   • Total Tasks: {analysis['total_tasks']}")
        print(f"   • Successful: {analysis['successful_tasks']}")
        print(f"   • Success Rate: {analysis['success_rate']:.1f}%")
        print(f"   • Average Duration: {analysis['average_duration']:.1f}s")
        
        print(f"\n📈 Results by Difficulty:")
        for difficulty, stats in analysis['difficulty_breakdown'].items():
            print(f"   • {difficulty}: {stats['tasks']} ({stats['success_rate']:.1f}%)")

def main():
    """Main function to run the specific tasks test"""
    print("🎯 Specific Omnizon Tasks Test Suite (GUI Enabled)")
    print("Testing: webclones.omnizon-6 and webclones.omnizon-9")
    
    test_suite = SpecificOmnizonTestSuite()
    
    # Run the specific tasks
    results = test_suite.run_specific_tasks()
    
    # Analyze results
    analysis = test_suite.analyze_results(results)
    
    # Save results
    test_suite.save_results(results, analysis)
    
    # Print final summary
    test_suite.print_final_summary(analysis)

if __name__ == "__main__":
    main()
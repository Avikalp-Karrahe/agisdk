#!/usr/bin/env python3
"""
Test GPT-4o RealEnhancedAgent on all Omnizon tasks.
Optimized configuration for GPT-4o model performance.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import REAL framework and agent
from agisdk import REAL
from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs

class GPT4OOmnizonTester:
    """Test runner for GPT-4o on Omnizon tasks."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.omnizon_tasks = [
            "webclones.omnizon-1",   # Easy: Search laptop, display first result
            "webclones.omnizon-2",   # Medium: Search smartphones, add first two to cart, buy third
            "webclones.omnizon-3",   # Easy: Browse Headphones category, retrieve listings
            "webclones.omnizon-4",   # Hard: Add Marshall speaker + Michael Kors watch, checkout
            "webclones.omnizon-5",   # Hard: Search KTC Gaming Monitor, display specs
            "webclones.omnizon-6",   # Hard: Compare Samsung phones, buy better value
            "webclones.omnizon-7",   # Medium: Find most expensive product in Gaming category
            "webclones.omnizon-8",   # Easy: Search Espresso Machine, buy cheapest with quantity 5
            "webclones.omnizon-9",   # Hard: Buy PlayStation DualSense with custom payment method
            "webclones.omnizon-10"   # Hard: Buy any product with max quantity and latest delivery
        ]
        
        # Task difficulty mapping
        self.task_difficulty = {
            "webclones.omnizon-1": "easy",
            "webclones.omnizon-2": "medium", 
            "webclones.omnizon-3": "easy",
            "webclones.omnizon-4": "hard",
            "webclones.omnizon-5": "hard",
            "webclones.omnizon-6": "hard",
            "webclones.omnizon-7": "medium",
            "webclones.omnizon-8": "easy",
            "webclones.omnizon-9": "hard",
            "webclones.omnizon-10": "hard"
        }
    
    def run_single_omnizon_task(self, task_name: str) -> Dict[str, Any]:
        """Run a single Omnizon task with GPT-4o."""
        print(f"\n🚀 Running {task_name} with GPT-4o...")
        
        try:
            # Create GPT-4o optimized agent args
            agent_args = RealEnhancedAgentArgs(
                model_name="gpt-4o",
                enhanced_selection=True,
                timeout_ms=45000,  # Increased timeout for GPT-4o
                retry_attempts=3,
                max_steps=30,      # More steps for complex tasks
                use_html=True,
                use_axtree=True,
                use_screenshot=True
            )
            
            # Initialize harness
            harness = REAL.harness(
                agentargs=agent_args,
                task_name=task_name,
                headless=True
            )
            
            # Run the task
            task_start = time.time()
            result = harness.run()
            task_duration = time.time() - task_start
            
            # Extract results
            success = result.get('success', False)
            score = result.get('score', 0.0)
            steps_taken = result.get('n_steps', 0)
            error_msg = result.get('err_msg', '')
            
            task_result = {
                'task_name': task_name,
                'difficulty': self.task_difficulty.get(task_name, 'unknown'),
                'model': 'gpt-4o',
                'success': success,
                'score': score,
                'steps_taken': steps_taken,
                'duration_seconds': round(task_duration, 2),
                'error_message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            
            # Print immediate result
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status} - {task_name} (Score: {score}, Steps: {steps_taken}, Time: {task_duration:.1f}s)")
            if error_msg:
                print(f"   Error: {error_msg}")
            
            return task_result
            
        except Exception as e:
            error_result = {
                'task_name': task_name,
                'difficulty': self.task_difficulty.get(task_name, 'unknown'),
                'model': 'gpt-4o',
                'success': False,
                'score': 0.0,
                'steps_taken': 0,
                'duration_seconds': 0,
                'error_message': f"EXCEPTION: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ EXCEPTION - {task_name}: {str(e)}")
            return error_result
    
    def run_all_omnizon_tasks(self):
        """Run all Omnizon tasks with GPT-4o."""
        print("🎯 Starting GPT-4o RealEnhancedAgent testing on all Omnizon tasks...")
        print(f"📊 Total tasks to test: {len(self.omnizon_tasks)}")
        print(f"🤖 Model: GPT-4o")
        print(f"⚡ Enhanced features: Memory, Self-Critique, Planning, Advanced Retry")
        
        self.start_time = time.time()
        
        for i, task_name in enumerate(self.omnizon_tasks, 1):
            print(f"\n{'='*60}")
            print(f"📋 Task {i}/{len(self.omnizon_tasks)}: {task_name}")
            print(f"🎚️ Difficulty: {self.task_difficulty.get(task_name, 'unknown').upper()}")
            
            result = self.run_single_omnizon_task(task_name)
            self.results.append(result)
            
            # Print running statistics
            self.print_running_stats()
        
        # Final summary
        self.print_final_summary()
        self.save_results()
    
    def print_running_stats(self):
        """Print current running statistics."""
        if not self.results:
            return
            
        total_tasks = len(self.results)
        successful_tasks = sum(1 for r in self.results if r['success'])
        success_rate = (successful_tasks / total_tasks) * 100
        
        print(f"\n📈 Running Stats: {successful_tasks}/{total_tasks} successful ({success_rate:.1f}%)")
    
    def print_final_summary(self):
        """Print comprehensive final summary."""
        if not self.results:
            return
        
        total_time = time.time() - self.start_time
        total_tasks = len(self.results)
        successful_tasks = sum(1 for r in self.results if r['success'])
        success_rate = (successful_tasks / total_tasks) * 100
        
        # Analyze by difficulty
        difficulty_stats = {}
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_results = [r for r in self.results if r['difficulty'] == difficulty]
            if difficulty_results:
                successful = sum(1 for r in difficulty_results if r['success'])
                total = len(difficulty_results)
                rate = (successful / total) * 100
                difficulty_stats[difficulty] = {
                    'successful': successful,
                    'total': total,
                    'rate': rate
                }
        
        print(f"\n{'='*80}")
        print("🎉 GPT-4o OMNIZON TESTING COMPLETE!")
        print(f"{'='*80}")
        print(f"🤖 Model: GPT-4o")
        print(f"⏱️ Total Time: {total_time:.1f} seconds")
        print(f"📊 Overall Success Rate: {successful_tasks}/{total_tasks} ({success_rate:.1f}%)")
        
        print(f"\n📈 Results by Difficulty:")
        for difficulty, stats in difficulty_stats.items():
            print(f"   {difficulty.upper()}: {stats['successful']}/{stats['total']} ({stats['rate']:.1f}%)")
        
        # Show failed tasks
        failed_tasks = [r for r in self.results if not r['success']]
        if failed_tasks:
            print(f"\n❌ Failed Tasks ({len(failed_tasks)}):")
            for task in failed_tasks:
                print(f"   • {task['task_name']} ({task['difficulty']}) - {task['error_message'][:100]}...")
        
        # Show successful tasks
        successful_task_list = [r for r in self.results if r['success']]
        if successful_task_list:
            print(f"\n✅ Successful Tasks ({len(successful_task_list)}):")
            for task in successful_task_list:
                print(f"   • {task['task_name']} ({task['difficulty']}) - Score: {task['score']}")
    
    def save_results(self):
        """Save detailed results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gpt4o_omnizon_results_{timestamp}.json"
        
        summary_data = {
            'test_info': {
                'model': 'gpt-4o',
                'agent': 'RealEnhancedAgent',
                'test_date': datetime.now().isoformat(),
                'total_tasks': len(self.results),
                'successful_tasks': sum(1 for r in self.results if r['success']),
                'success_rate': (sum(1 for r in self.results if r['success']) / len(self.results)) * 100 if self.results else 0
            },
            'difficulty_breakdown': {},
            'detailed_results': self.results
        }
        
        # Add difficulty breakdown
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_results = [r for r in self.results if r['difficulty'] == difficulty]
            if difficulty_results:
                successful = sum(1 for r in difficulty_results if r['success'])
                total = len(difficulty_results)
                summary_data['difficulty_breakdown'][difficulty] = {
                    'total': total,
                    'successful': successful,
                    'success_rate': (successful / total) * 100
                }
        
        with open(filename, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function to run GPT-4o Omnizon testing."""
    tester = GPT4OOmnizonTester()
    tester.run_all_omnizon_tasks()

if __name__ == "__main__":
    main()
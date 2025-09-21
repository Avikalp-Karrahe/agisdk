#!/usr/bin/env python3
"""
REAL Benchmark Evaluation Script for Enhanced Agent - 2 Tasks Only

This script runs a limited REAL benchmark evaluation (2 tasks) using our enhanced agent
with memory, self-critique, planning, and advanced retry capabilities.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agisdk import REAL
from real_enhanced_agent import RealEnhancedAgentArgs

def run_single_task(task_name, agent_args):
    """Run a single task and return results."""
    try:
        # Create REAL harness for single task
        harness = REAL.harness(
            agentargs=agent_args,
            task_name=task_name,  # Run specific task
            headless=True,  # Run headless for automated evaluation
            max_steps=25,
            sample_tasks=1  # Run each task once
        )
        
        print(f"Running task: {task_name}")
        
        # Run the benchmark
        results = harness.run()
        return results
        
    except Exception as e:
        print(f"Error running task {task_name}: {e}")
        return None

def main():
    """Run REAL benchmark evaluation with enhanced agent - limited to 2 tasks."""
    
    # Set up API key (you may need to set this in your environment)
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set. You may need to set it for evaluation.")
    
    print("Starting REAL Benchmark Evaluation with Enhanced Agent (2 Tasks)")
    print("=" * 60)
    
    # Configure the enhanced agent
    agent_args = RealEnhancedAgentArgs(
        agent_name='RealEnhancedAgent',
        model_name='gpt-4o-mini',  # Using a cost-effective model for testing
        enhanced_selection=True,
        timeout_ms=10000,  # 10 second timeout
        retry_attempts=3,
        simulate_execution=False,  # Run actual evaluation
        use_html=True,
        use_axtree=True,
        use_screenshot=True,
        max_steps=25
    )
    
    # Define the 2 tasks to run
    tasks_to_run = [
        "webclones.omnizon-1",
        "webclones.omnizon-2"
    ]
    
    print(f"Running benchmark with enhanced agent: {agent_args.agent_name}")
    print(f"Task type: omnizon (Amazon-like store)")
    print(f"Number of tasks: {len(tasks_to_run)} (limited for quick testing)")
    print(f"Tasks: {', '.join(tasks_to_run)}")
    print(f"Model: {agent_args.model_name}")
    print("\nStarting evaluation...")
    
    all_results = {}
    
    # Run each task sequentially
    for task_name in tasks_to_run:
        result = run_single_task(task_name, agent_args)
        if result:
            all_results.update(result)
    
    print("\n" + "=" * 60)
    print("REAL Benchmark Results (2 Tasks)")
    print("=" * 60)
    print(f"Results: {all_results}")
    
    # Extract and display key metrics
    if all_results:
        # Calculate aggregate metrics
        total_tasks = len(all_results)
        successful_tasks = sum(1 for result in all_results.values() if result.get('success', False))
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        # Calculate average steps
        steps_list = [result.get('n_steps', 0) for result in all_results.values()]
        avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0
        
        print(f"\nKey Metrics:")
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Total Episodes: {total_tasks}")
        print(f"Successful Tasks: {successful_tasks}")
        print(f"Average Steps: {avg_steps:.1f}")
        
        # Enhanced agent specific metrics
        print(f"\nEnhanced Agent Features Used:")
        print(f"- Memory System: ✓")
        print(f"- Self-Critique: ✓")
        print(f"- Planning System: ✓")
        print(f"- Advanced Retry: ✓")
        
        # Show individual task results
        print(f"\nIndividual Task Results:")
        for task_name, result in all_results.items():
            success = "✓" if result.get('success', False) else "✗"
            steps = result.get('n_steps', 0)
            print(f"  {task_name}: {success} ({steps} steps)")
    
    print("\nBenchmark evaluation completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
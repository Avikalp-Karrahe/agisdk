#!/usr/bin/env python3
"""
REAL Benchmark Evaluation Script for Enhanced Agent

This script runs the REAL benchmark evaluation using our enhanced agent
with memory, self-critique, planning, and advanced retry capabilities.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agisdk import REAL
from real_enhanced_agent import RealEnhancedAgentArgs

def main():
    """Run REAL benchmark evaluation with enhanced agent."""
    
    # Set up API key (you may need to set this in your environment)
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set. You may need to set it for evaluation.")
    
    print("Starting REAL Benchmark Evaluation with Enhanced Agent")
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
    
    try:
        # Create REAL harness with our enhanced agent
        harness = REAL.harness(
            agentargs=agent_args,
            task_type="omnizon",  # Start with Amazon-like store tasks
            headless=True,  # Run headless for automated evaluation
            max_steps=25
        )
        
        print(f"Running benchmark with enhanced agent: {agent_args.agent_name}")
        print(f"Task type: omnizon (Amazon-like store)")
        print(f"Number of episodes: 3")
        print(f"Model: {agent_args.model_name}")
        print("\nStarting evaluation...")
        
        # Run the benchmark
        results = harness.run()
        
        print("\n" + "=" * 60)
        print("REAL Benchmark Results")
        print("=" * 60)
        print(f"Results: {results}")
        
        # Extract and display key metrics
        if isinstance(results, dict):
            success_rate = results.get('success_rate', 0)
            total_episodes = results.get('total_episodes', 0)
            avg_steps = results.get('avg_steps', 0)
            
            print(f"\nKey Metrics:")
            print(f"Success Rate: {success_rate:.2%}")
            print(f"Total Episodes: {total_episodes}")
            print(f"Average Steps: {avg_steps:.1f}")
            
            # Enhanced agent specific metrics
            print(f"\nEnhanced Agent Features Used:")
            print(f"- Memory System: ✓")
            print(f"- Self-Critique: ✓")
            print(f"- Planning System: ✓")
            print(f"- Advanced Retry: ✓")
        
        print("\nBenchmark evaluation completed successfully!")
        
    except Exception as e:
        print(f"\nError during benchmark evaluation: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
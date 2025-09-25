#!/usr/bin/env python3
"""
Test script to run a single Omnizon task with detailed debug output
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import agisdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agisdk import REAL
from real_enhanced_agent import RealEnhancedAgent

def test_single_task():
    """Test a single Omnizon task with debug output"""
    
    # Test configuration
    task_name = "webclones.omnizon-1"  # Start with an easy task
    model = "gpt-4o"
    
    print(f"🧪 Testing {task_name} with {model}")
    print("=" * 60)
    
    try:
        # Initialize the agent
        from real_enhanced_agent import RealEnhancedAgentArgs
        args = RealEnhancedAgentArgs(model_name=model)
        
        # Initialize REAL harness
        harness = REAL.harness(
            agentargs=args,
            task_name=task_name,
            headless=True
        )
        
        print(f"🚀 Starting test run...")
        
        # Run the test
        results = harness.run()
        
        print(f"✅ Test completed!")
        print(f"Results: {results}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = test_single_task()
    
    if results:
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        for result in results:
            print(f"Task: {result.get('task', 'Unknown')}")
            print(f"Success: {result.get('success', False)}")
            print(f"Score: {result.get('score', 0.0)}")
            print(f"Steps: {result.get('steps_taken', 0)}")
            print(f"Duration: {result.get('duration_seconds', 0.0):.2f}s")
            if result.get('error_message'):
                print(f"Error: {result['error_message']}")
    else:
        print("❌ No results to display")
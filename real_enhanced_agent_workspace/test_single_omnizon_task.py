#!/usr/bin/env python3
"""
Single Omnizon Task Test for RealEnhancedAgent

This script tests the RealEnhancedAgent on a single Omnizon task to debug
issues and verify the agent works correctly.
"""

import os
import sys
import time
from datetime import datetime

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

def test_single_omnizon_task(task_name="webclones.omnizon-1"):
    """Test RealEnhancedAgent on a single Omnizon task."""
    print(f"🎯 Testing RealEnhancedAgent on {task_name}")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    start_time = time.time()
    
    try:
        # Create RealEnhancedAgent args with correct parameters
        agent_args = RealEnhancedAgentArgs(
            model_name="claude-3-5-sonnet-20241022",
            enhanced_selection=True,
            timeout_ms=30000,  # 30 seconds
            retry_attempts=2,
            max_steps=15
        )
        
        print(f"📋 Agent Configuration:")
        print(f"   Model: {agent_args.model_name}")
        print(f"   Enhanced Selection: {agent_args.enhanced_selection}")
        print(f"   Timeout: {agent_args.timeout_ms}ms")
        print(f"   Max Steps: {agent_args.max_steps}")
        print(f"   Retry Attempts: {agent_args.retry_attempts}")
        
        # Create harness for single task
        harness = REAL.harness(
            agentargs=agent_args,
            headless=False,  # Set to False to see browser for debugging
            task_name=task_name,
            sample_tasks=1,
            max_steps=agent_args.max_steps
        )
        
        print(f"\n🚀 Running task: {task_name}")
        print("   This may take 30-60 seconds...")
        
        # Run the task
        results = harness.run()
        
        duration = time.time() - start_time
        
        # Analyze results
        if results and len(results) > 0:
            result = results[0]
            success = result.get('success', False)
            reward = result.get('reward', 0.0)
            steps = result.get('n_steps', 0)
            error_msg = result.get('err_msg', '')
            
            print(f"\n📊 RESULTS:")
            print(f"   Task: {task_name}")
            print(f"   Success: {'✅ YES' if success else '❌ NO'}")
            print(f"   Reward: {reward}")
            print(f"   Steps Taken: {steps}")
            print(f"   Duration: {duration:.2f}s")
            
            if error_msg:
                print(f"   Error: {error_msg}")
            
            if success:
                print(f"\n🎉 SUCCESS! RealEnhancedAgent completed {task_name}")
            else:
                print(f"\n⚠️ Task failed. Check error details above.")
                
            return {
                'success': success,
                'reward': reward,
                'steps': steps,
                'duration': duration,
                'error': error_msg
            }
        else:
            print(f"\n❌ No results returned from harness")
            return None
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Exception occurred: {e}")
        print(f"   Duration: {duration:.2f}s")
        return None

def main():
    """Main function to test a single Omnizon task."""
    print("🔧 RealEnhancedAgent - Single Task Test")
    print("=" * 60)
    
    # Test the easiest task first
    result = test_single_omnizon_task("webclones.omnizon-1")
    
    if result:
        if result['success']:
            print(f"\n✨ Ready to test more tasks!")
        else:
            print(f"\n🔍 Debug needed - check agent implementation")
    else:
        print(f"\n🚨 Critical error - check setup and configuration")

if __name__ == "__main__":
    main()
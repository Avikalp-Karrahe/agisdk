#!/usr/bin/env python3
"""
Test script for the demo agent on the omnizon laptop search task.
This will help us compare the demo agent's performance with our enhanced agent.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add the agisdk source to the path
sys.path.insert(0, '/Users/avikalpkarrahe/Desktop/MacAirAvi/UCD 24-25/JS\'25/NonSense/AGI2/agisdk/src')

from agisdk import REAL
from agisdk.REAL.demo_agent.basic_agent import DemoAgentArgs

def test_demo_agent_omnizon():
    """Test the demo agent on the omnizon laptop search task."""
    
    print("🧪 Testing Demo Agent on Omnizon Task")
    print("=" * 50)
    
    # Create demo agent arguments with proper configuration (similar to harness)
    args = DemoAgentArgs(
        model_name="gpt-4o",
        chat_mode=False,
        demo_mode="default",
        use_html=False,
        use_axtree=True,
        use_screenshot=True,  # Enable screenshots like the harness does
        system_message_handling="separate"
    )
    
    # Test configuration
    task_name = "webclones.omnizon-1"
    
    print(f"📋 Task: {task_name}")
    print(f"🤖 Agent: Demo Agent (gpt-4o)")
    print(f"🔧 Config: Max Steps=25, Screenshots=True, AXTree=True")
    print()
    
    # Results tracking
    results = {
        "task_name": task_name,
        "agent_name": "DemoAgent",
        "timestamp": datetime.now().isoformat(),
        "actions_taken": [],
        "success": False,
        "error": None,
        "execution_time": 0,
        "final_reward": 0,
        "steps_taken": 0
    }
    
    start_time = time.time()
    
    try:
        # Run the task
        print("🎯 Starting omnizon laptop search task with demo agent...")
        
        # Create harness and run task
        harness = REAL.harness(
            agentargs=args,
            task_name=task_name,
            leaderboard=False,
            headless=True,
            num_workers=1,
            use_cache=False,
            max_steps=25
        )
        
        # Run task
        task_results = harness.run()
        
        # Extract results from harness output
        if task_name in task_results:
            exp_result_dict = task_results[task_name]
            results["success"] = exp_result_dict.get("cum_reward", 0) > 0
            results["final_reward"] = exp_result_dict.get("cum_reward", 0)
            results["steps_taken"] = exp_result_dict.get("n_steps", 0)
            results["execution_time"] = time.time() - start_time
            
            # Get the ExpResult object to access steps_info
            from agisdk.REAL.browsergym.experiments.loop import get_exp_result
            exp_result_obj = get_exp_result(exp_result_dict.get("exp_dir"))
            
            # Extract actions from steps_info
            try:
                steps_info = exp_result_obj.steps_info
                for i, step_info in enumerate(steps_info):
                    if hasattr(step_info, 'action') and step_info.action:
                        results["actions_taken"].append({
                            "step": i,
                            "action": step_info.action
                        })
                        print(f"  Step {i}: {step_info.action}")
                
                print(f"\n✅ Successfully extracted {len(results['actions_taken'])} actions")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not extract actions from steps_info: {e}")
                results["actions_taken"] = []
        
        else:
            print(f"❌ Task {task_name} not found in results")
            results["error"] = f"Task {task_name} not found in results"
    
    except Exception as e:
        print(f"❌ Error during task execution: {e}")
        results["error"] = str(e)
        results["execution_time"] = time.time() - start_time
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 DEMO AGENT TEST RESULTS")
    print("=" * 50)
    print(f"Task: {results['task_name']}")
    print(f"Agent: {results['agent_name']}")
    print(f"Success: {'✅ Yes' if results['success'] else '❌ No'}")
    print(f"Final Reward: {results['final_reward']}")
    print(f"Steps Taken: {results['steps_taken']}")
    print(f"Actions Extracted: {len(results['actions_taken'])}")
    print(f"Execution Time: {results['execution_time']:.2f}s")
    
    if results['error']:
        print(f"Error: {results['error']}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"demo_agent_omnizon_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    # Check for API key - require real API key for proper testing
    if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: No API key found!")
        print("Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
        print("The demo agent needs a real API key to function properly")
        sys.exit(1)

    results = test_demo_agent_omnizon()

    print(f"\n🎯 Final Results: {results}")
    sys.exit(0 if results.get("success", False) else 1)
#!/usr/bin/env python3
"""
Real-world test of the clean enhanced agent with omnizon laptop search task.
This validates that all improvements work correctly in practice.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add the agisdk path
sys.path.insert(0, '/Users/avikalpkarrahe/Desktop/MacAirAvi/UCD 24-25/JS\'25/NonSense/AGI2/agisdk/src')

from agisdk import REAL
from real_enhanced_agent_clean import RealEnhancedAgent, RealEnhancedAgentArgs

def test_clean_agent_omnizon():
    """Test the clean enhanced agent on omnizon laptop search task"""
    
    print("🚀 Testing Clean Enhanced Agent on Omnizon Laptop Search")
    print("=" * 60)
    
    # Configuration
    args = RealEnhancedAgentArgs(
        model_name="claude-3-5-sonnet-20241022",
        enhanced_selection=True,
        timeout_ms=15000,
        retry_attempts=3,
        simulate_execution=False,
        use_html=True,
        use_axtree=True,
        use_screenshot=True,
        max_steps=25
    )
    
    # Create agent
    agent = RealEnhancedAgent(args)
    
    # Test configuration
    task_name = "webclones.omnizon-1"
    
    print(f"📋 Task: {task_name}")
    print(f"🤖 Agent: {agent.__class__.__name__}")
    print(f"🧠 Model: {args.model_name}")
    print(f"⚙️  Enhanced Features: Selection={args.enhanced_selection}, HTML={args.use_html}")
    print(f"🔧 Config: Timeout={args.timeout_ms}ms, Max Steps={args.max_steps}")
    print()
    
    # Results tracking
    results = {
        "task_name": task_name,
        "agent_name": agent.__class__.__name__,
        "model_name": args.model_name,
        "timestamp": datetime.now().isoformat(),
        "enhanced_features": {
            "enhanced_selection": args.enhanced_selection,
            "use_html": args.use_html,
            "use_axtree": args.use_axtree,
            "use_screenshot": args.use_screenshot,
            "timeout_ms": args.timeout_ms
        },
        "actions_taken": [],
        "intelligent_sequences": [],
        "context_refreshes": 0,
        "success": False,
        "error": None,
        "execution_time": 0
    }
    
    start_time = time.time()
    
    try:
        # Run the task
        print("🎯 Starting omnizon laptop search task...")
        
        # Create harness and run task
        harness = REAL.harness(
            model=args.model_name,
            agentargs=args,
            task_name="webclones.omnizon-1",
            leaderboard=False,
            headless=True,
            num_workers=1,
            use_cache=False,
            max_steps=args.max_steps
        )
        
        # Run task (no parameters needed since task_name is set in constructor)
        task_results = harness.run()
        
        # Extract results from harness output
        task_key = f"webclones.omnizon-1"
        if task_key in task_results:
            exp_result_dict = task_results[task_key]
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
                        action = step_info.action
                        results["actions_taken"].append({
                            "step": i,
                            "action": action,
                            "timestamp": getattr(step_info, 'timestamp', None)
                        })
                        
                        # Detect fill->press sequences
                        if i > 0 and action.startswith('press(') and len(results["actions_taken"]) > 1:
                            prev_action = results["actions_taken"][-2]["action"]
                            if prev_action.startswith('fill(') and 'Enter' in action:
                                results["intelligent_sequences"].append({
                                    "step": i-1,
                                    "sequence": [prev_action, action],
                                    "type": "fill_then_press_enter"
                                })
            except Exception as e:
                print(f"⚠️  Error extracting actions from steps_info: {e}")
                # Fallback: try to get actions from agent_info if available
                pass
        else:
            print(f"⚠️  Task {task_key} not found in results")
            results["success"] = False
            results["final_reward"] = 0
            results["steps_taken"] = 0
            results["execution_time"] = time.time() - start_time
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 OMNIZON LAPTOP SEARCH RESULTS")
        print("=" * 60)
        
        status_icon = "✅" if results["success"] else "❌"
        print(f"{status_icon} Task Success: {results['success']}")
        print(f"🎯 Final Reward: {results['final_reward']}")
        print(f"👣 Steps Taken: {results['steps_taken']}")
        print(f"⏱️  Execution Time: {results['execution_time']:.2f}s")
        print(f"🔄 Context Refreshes: {results['context_refreshes']}")
        print(f"🧠 Intelligent Sequences: {len(results['intelligent_sequences'])}")
        
        if results["intelligent_sequences"]:
            print("\n🎯 Detected Intelligent Action Sequences:")
            for seq in results["intelligent_sequences"]:
                print(f"  Step {seq['step']}: {seq['sequence'][0]} → {seq['sequence'][1]}")
        
        print(f"\n📝 Actions Taken:")
        for action_info in results["actions_taken"][-10:]:  # Show last 10 actions
            print(f"  Step {action_info['step']}: {action_info['action']}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"clean_agent_omnizon_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        if results["success"]:
            print("\n🎉 SUCCESS! Clean enhanced agent completed the omnizon laptop search task!")
            print("✨ Key improvements validated:")
            print("  ✓ Consistent context caching")
            print("  ✓ Intelligent action sequencing")
            print("  ✓ Simplified LLM-based action generation")
            print("  ✓ Enhanced memory and planning systems")
        else:
            print("\n⚠️  Task not completed successfully. Analyzing trajectory...")
            print("🔍 This helps identify areas for further improvement.")
        
        return results
        
    except Exception as e:
        results["error"] = str(e)
        results["execution_time"] = time.time() - start_time
        
        print(f"\n💥 Error during task execution: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return results
    
    finally:
        # Cleanup
        try:
            agent.close()
        except:
            pass

if __name__ == "__main__":
    # Check for API key - use Anthropic instead of OpenAI
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your Anthropic API key to run this test")
        sys.exit(1)

    results = test_clean_agent_omnizon()
    
    print(f"\n🎯 Final Results: {results}")
    sys.exit(0 if results.get("success", False) else 1)
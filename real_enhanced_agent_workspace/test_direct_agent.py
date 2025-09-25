#!/usr/bin/env python3
"""
Test the agent directly without the REAL framework to verify it works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agisdk.REAL.browsergym.core.env import BrowserEnv
from agisdk.REAL.browsergym.webclones.base import AbstractWebCloneTask
from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs

def test_direct_agent():
    """Test the agent directly with manual observation processing."""
    
    # Create environment
    env = BrowserEnv(
        task_entrypoint=AbstractWebCloneTask, 
        task_kwargs={"task_id": "omnizon-1"},
        headless=True
    )
    
    # Create agent
    agent_args = RealEnhancedAgentArgs(
        model_name="claude-3-5-sonnet-20241022",
        enhanced_selection=True,
        timeout_ms=15000,
        max_steps=5
    )
    agent = RealEnhancedAgent(agent_args)
    
    try:
        # Reset environment
        obs, info = env.reset()
        print(f"🎯 Goal: {obs.get('goal', 'Unknown goal')}")
        
        step = 0
        max_steps = 5
        
        while step < max_steps:
            step += 1
            print(f"\n=== STEP {step} ===")
            
            # Get action from agent
            action, metadata = agent.get_action(obs)
            print(f"Action: {action}")
            print(f"Metadata: {metadata}")
            
            # Check if it's a noop
            if action.startswith('noop'):
                print("Agent generated noop - continuing...")
            elif action.startswith('fill'):
                print("✅ Agent generated fill action - SUCCESS!")
                break
            else:
                print(f"Agent generated action: {action}")
            
            # Execute action in environment
            try:
                obs, reward, done, truncated, info = env.step(action)
                print(f"Reward: {reward}, Done: {done}")
                
                if done:
                    print("Task completed!")
                    break
                    
            except Exception as e:
                print(f"Error executing action: {e}")
                break
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Steps taken: {step}")
        print(f"Final action: {action}")
        
        return action.startswith('fill')
        
    finally:
        env.close()
        agent.close()

if __name__ == "__main__":
    success = test_direct_agent()
    if success:
        print("✅ Direct agent test PASSED")
    else:
        print("❌ Direct agent test FAILED")
#!/usr/bin/env python3
"""
Debug script to trace observation flow through the agent.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agisdk.REAL.browsergym.experiments import ExpArgs
from agisdk.REAL.browsergym.core.env import BrowserEnv
from agisdk.REAL.browsergym.webclones.base import AbstractWebCloneTask
from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs

def debug_obs_flow():
    """Debug the observation flow through the agent."""
    
    # Create environment
    env = BrowserEnv(
        task_entrypoint=AbstractWebCloneTask, 
        task_kwargs={"task_id": "omnizon-1"},
        headless=True
    )
    
    # Create agent
    agent_args = RealEnhancedAgentArgs()
    agent = RealEnhancedAgent(agent_args)
    
    try:
        # Reset environment to get initial observation
        obs, info = env.reset()
        print(f"=== RAW OBSERVATION ===")
        print(f"Keys: {list(obs.keys())}")
        print(f"Has DOM object: {'dom_object' in obs and obs['dom_object'] is not None}")
        print(f"Has AXTree object: {'axtree_object' in obs and obs['axtree_object'] is not None}")
        
        # Test obs_preprocessor directly
        print(f"\n=== TESTING OBS_PREPROCESSOR ===")
        processed_obs = agent.obs_preprocessor(obs)
        print(f"Processed obs keys: {list(processed_obs.keys())}")
        print(f"Has pruned_html: {'pruned_html' in processed_obs}")
        print(f"Has axtree_txt: {'axtree_txt' in processed_obs}")
        
        if 'pruned_html' in processed_obs:
            print(f"pruned_html length: {len(processed_obs['pruned_html'])}")
            print(f"pruned_html preview: {processed_obs['pruned_html'][:200]}")
        
        if 'axtree_txt' in processed_obs:
            print(f"axtree_txt length: {len(processed_obs['axtree_txt'])}")
            print(f"axtree_txt preview: {processed_obs['axtree_txt'][:200]}")
        
        # Test _generate_enhanced_action directly
        print(f"\n=== TESTING _generate_enhanced_action ===")
        action = agent._generate_enhanced_action(processed_obs, None)
        print(f"Generated action: {action}")
        
        # Test full get_action flow
        print(f"\n=== TESTING FULL get_action FLOW ===")
        action, metadata = agent.get_action(obs)
        print(f"Full flow action: {action}")
        print(f"Metadata: {metadata}")
        
    finally:
        env.close()
        agent.close()

if __name__ == "__main__":
    debug_obs_flow()
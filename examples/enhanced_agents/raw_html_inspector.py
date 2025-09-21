#!/usr/bin/env python3

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class RawHtmlInspectorArgs(AbstractAgentArgs):
    """Arguments for the raw HTML inspector agent."""
    agent_name: str = "RawHtmlInspector"
    
    def make_agent(self):
        """Create the agent instance."""
        return RawHtmlInspector(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class RawHtmlInspector(Agent):
    """Agent that prints raw HTML and observation data to understand page structure."""
    
    def __init__(self, action_set: HighLevelActionSet, args: RawHtmlInspectorArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        
    def obs_preprocessor(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess observation."""
        return obs
        
    def close(self):
        """Clean up resources."""
        pass
        
    def get_action(self, obs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Get the next action to take."""
        self.step_count += 1
        
        # Extract information from observation
        url = obs.get('url', 'Unknown')
        goal = obs.get('goal', 'No goal specified')
        
        print(f"\n{'='*80}")
        print(f"STEP {self.step_count}: RAW HTML INSPECTION")
        print(f"{'='*80}")
        print(f"URL: {url}")
        print(f"Goal: {goal}")
        
        # Print all observation keys
        print(f"\nObservation keys: {list(obs.keys())}")
        
        # Print DOM-related information
        if 'dom_txt' in obs:
            dom_txt = obs['dom_txt']
            print(f"\nDOM_TXT (first 2000 chars):")
            print("-" * 40)
            print(dom_txt[:2000])
            print("-" * 40)
            
        if 'dom_object' in obs:
            dom_obj = obs['dom_object']
            print(f"\nDOM_OBJECT type: {type(dom_obj)}")
            if isinstance(dom_obj, dict):
                print(f"DOM_OBJECT keys: {list(dom_obj.keys())}")
                
        # Print accessibility tree
        if 'axtree_txt' in obs:
            axtree_txt = obs['axtree_txt']
            print(f"\nAXTREE_TXT (first 1000 chars):")
            print("-" * 40)
            print(axtree_txt[:1000])
            print("-" * 40)
            
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            print(f"\nAXTREE_OBJECT type: {type(axtree_obj)}")
            if isinstance(axtree_obj, dict):
                print(f"AXTREE_OBJECT keys: {list(axtree_obj.keys())}")
        
        # Look for any HTML content
        html_content = None
        for key, value in obs.items():
            if isinstance(value, str) and ('<html' in value.lower() or '<body' in value.lower() or 'bid=' in value.lower()):
                html_content = value
                print(f"\nFound HTML content in key '{key}' (first 3000 chars):")
                print("-" * 40)
                print(value[:3000])
                print("-" * 40)
                break
                
        # Search for bid attributes in any string values
        bid_count = 0
        for key, value in obs.items():
            if isinstance(value, str):
                bids = re.findall(r'bid="([^"]*)"', value, re.IGNORECASE)
                if bids:
                    bid_count += len(bids)
                    print(f"\nFound {len(bids)} BID attributes in '{key}':")
                    for i, bid in enumerate(bids[:10]):  # Show first 10
                        print(f"  {i+1}. bid=\"{bid}\"")
                    if len(bids) > 10:
                        print(f"  ... and {len(bids) - 10} more")
                        
        print(f"\nTotal BID attributes found: {bid_count}")
        
        # Search for input elements
        input_count = 0
        for key, value in obs.items():
            if isinstance(value, str):
                inputs = re.findall(r'<input[^>]*>', value, re.IGNORECASE)
                if inputs:
                    input_count += len(inputs)
                    print(f"\nFound {len(inputs)} input elements in '{key}':")
                    for i, inp in enumerate(inputs[:5]):  # Show first 5
                        print(f"  {i+1}. {inp}")
                    if len(inputs) > 5:
                        print(f"  ... and {len(inputs) - 5} more")
                        
        print(f"\nTotal input elements found: {input_count}")
        
        # Try simple actions based on step
        if self.step_count <= 3:
            print(f"\nTaking scroll action for step {self.step_count}")
            return 'scroll(0, 3)', {}
        else:
            print(f"\nEnding inspection after {self.step_count} steps")
            return 'send_msg_to_user("HTML inspection complete")', {}


def test_raw_html_inspector():
    """Test the raw HTML inspector agent."""
    
    # Set up experiment arguments
    agent_args = RawHtmlInspectorArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=5)
    
    exp_args = ExpArgs(
        agent_args=agent_args,
        env_args=env_args,
    )
    
    # Run the experiment
    exp_args.prepare("./results")
    exp_args.run()
    
    # Get results
    exp_result = get_exp_result(exp_args.exp_dir)
    exp_record = exp_result.get_exp_record()
    
    print(f"\nTask: {exp_record.get('task_name', 'Unknown')}")
    print(f"  Reward: {exp_record.get('cum_reward', 0)}")
    print(f"  Success: {exp_record.get('cum_reward', 0) > 0}")
    print(f"  Steps: {exp_record.get('n_steps', 0)}")
    
    return exp_record.get('cum_reward', 0) > 0


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Raw HTML Inspector Agent")
    print("=" * 50)
    
    try:
        success = test_raw_html_inspector()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running raw HTML inspector: {e}")
        import traceback
        traceback.print_exc()
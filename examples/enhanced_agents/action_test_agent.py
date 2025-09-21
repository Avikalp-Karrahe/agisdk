#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class ActionTestAgentArgs(AbstractAgentArgs):
    """Arguments for the action test agent."""
    agent_name: str = "ActionTestAgent"
    
    def make_agent(self):
        """Create the agent instance."""
        return ActionTestAgent(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class ActionTestAgent(Agent):
    """Agent that tests different action formats to find what works."""
    
    def __init__(self, action_set: HighLevelActionSet, args: ActionTestAgentArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        self.test_actions = [
            # Different ways to type in a textbox
            ('type(bid="163", text="laptop")', {}),
            ('type("163", "laptop")', {}),
            ('fill(bid="163", text="laptop")', {}),
            ('input(bid="163", text="laptop")', {}),
            
            # Different ways to click a button
            ('click(bid="167")', {}),
            ('click("167")', {}),
            ('press(bid="167")', {}),
            ('button_click(bid="167")', {}),
            
            # Try with different BID formats
            ('type(163, "laptop")', {}),
            ('click(167)', {}),
        ]
        
    def obs_preprocessor(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess observation."""
        return obs
        
    def close(self):
        """Clean up resources."""
        pass
        
    def extract_role(self, role_dict):
        """Extract role string from role dictionary."""
        if isinstance(role_dict, dict):
            return role_dict.get('value', role_dict.get('type', str(role_dict)))
        return str(role_dict)
    
    def extract_name(self, name_dict):
        """Extract name string from name dictionary."""
        if isinstance(name_dict, dict):
            return name_dict.get('value', name_dict.get('name', str(name_dict)))
        return str(name_dict)
        
    def get_action(self, obs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Get the next action to take."""
        self.step_count += 1
        
        print(f"\n{'='*60}")
        print(f"STEP {self.step_count}: ACTION FORMAT TESTING")
        print(f"{'='*60}")
        
        # Check for any action errors from previous step
        if 'last_action_error' in obs and obs['last_action_error']:
            print(f"Previous action error: {obs['last_action_error']}")
        
        if 'last_action' in obs and obs['last_action']:
            print(f"Previous action: {obs['last_action']}")
        
        # Find available elements first
        textbox_bid = None
        button_bid = None
        
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            
            if isinstance(axtree_obj, dict) and 'nodes' in axtree_obj:
                nodes = axtree_obj['nodes']
                
                for node in nodes:
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {})).lower()
                        name_str = self.extract_name(node.get('name', {})).lower()
                        
                        # Get BID
                        bid = None
                        for bid_field in ['browsergym_id', 'bid', 'backendDOMNodeId', 'nodeId']:
                            if bid_field in node:
                                bid = str(node[bid_field])
                                break
                        
                        if bid:
                            if role_str == 'textbox' and not textbox_bid:
                                textbox_bid = bid
                                print(f"Found textbox with BID: {bid}")
                            elif role_str == 'button' and 'search' in name_str and not button_bid:
                                button_bid = bid
                                print(f"Found search button with BID: {bid}")
        
        # Test different action formats
        if self.step_count <= len(self.test_actions):
            action_str, action_dict = self.test_actions[self.step_count - 1]
            
            # Replace placeholder BIDs with actual ones if found
            if textbox_bid:
                action_str = action_str.replace('163', textbox_bid)
            if button_bid:
                action_str = action_str.replace('167', button_bid)
            
            print(f"Testing action {self.step_count}: {action_str}")
            return action_str, action_dict
        
        # After testing all actions, try to click the search button if we found one
        elif button_bid and self.step_count == len(self.test_actions) + 1:
            print(f"Final attempt: clicking search button with BID {button_bid}")
            return f'click(bid="{button_bid}")', {}
        
        else:
            print(f"All action tests completed. Ending after {self.step_count} steps.")
            return 'send_msg_to_user("Action format testing complete")', {}


def test_action_formats():
    """Test different action formats."""
    
    # Set up experiment arguments
    agent_args = ActionTestAgentArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=15)
    
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
    
    print(f"\nFinal Results:")
    print(f"Task: {exp_record.get('task_name', 'Unknown')}")
    print(f"  Reward: {exp_record.get('cum_reward', 0)}")
    print(f"  Success: {exp_record.get('cum_reward', 0) > 0}")
    print(f"  Steps: {exp_record.get('n_steps', 0)}")
    
    return exp_record.get('cum_reward', 0) > 0


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Different Action Formats")
    print("=" * 50)
    
    try:
        success = test_action_formats()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running action test agent: {e}")
        import traceback
        traceback.print_exc()
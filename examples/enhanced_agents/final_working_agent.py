#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class FinalWorkingAgentArgs(AbstractAgentArgs):
    """Arguments for the final working agent."""
    agent_name: str = "FinalWorkingAgent"
    
    def make_agent(self):
        """Create the agent instance."""
        return FinalWorkingAgent(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class FinalWorkingAgent(Agent):
    """Final working agent that uses correct action formats to complete the search task."""
    
    def __init__(self, action_set: HighLevelActionSet, args: FinalWorkingAgentArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        self.search_completed = False
        self.textbox_filled = False
        
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
        print(f"STEP {self.step_count}: FINAL WORKING AGENT")
        print(f"{'='*60}")
        
        # Check for any action errors from previous step
        if 'last_action_error' in obs and obs['last_action_error']:
            print(f"Previous action error: {obs['last_action_error']}")
        
        if 'last_action' in obs and obs['last_action']:
            print(f"Previous action: {obs['last_action']}")
        
        # Find available elements
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
                        
                        if bid and bid != 'no-bid':
                            if role_str == 'textbox' and not textbox_bid:
                                textbox_bid = bid
                                print(f"Found textbox with BID: {bid}")
                            elif role_str == 'button' and 'search' in name_str and not button_bid:
                                button_bid = bid
                                print(f"Found search button with BID: {bid}")
        
        # Step 1: Fill the textbox with "laptop"
        if not self.textbox_filled and textbox_bid:
            print(f"Filling textbox {textbox_bid} with 'laptop'")
            self.textbox_filled = True
            return f'fill(bid="{textbox_bid}", value="laptop")', {}
        
        # Step 2: Click the search button
        elif self.textbox_filled and not self.search_completed and button_bid:
            print(f"Clicking search button {button_bid}")
            self.search_completed = True
            return f'click(bid="{button_bid}")', {}
        
        # Step 3: Wait for results and look for products
        elif self.search_completed:
            # Look for product links or results
            product_links = []
            
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
                            
                            # Look for product links
                            if (role_str == 'link' and bid and bid != 'no-bid' and 
                                ('laptop' in name_str or 'product' in name_str or 
                                 '$' in name_str or 'price' in name_str)):
                                product_links.append((bid, name_str))
            
            if product_links:
                # Click on the first product
                first_product_bid, first_product_name = product_links[0]
                print(f"Found {len(product_links)} product links. Clicking first product: {first_product_name}")
                return f'click(bid="{first_product_bid}")', {}
            else:
                print("No product links found yet, scrolling down to look for results")
                return 'scroll(coordinate=[640, 360], direction="down")', {}
        
        else:
            # If we can't find elements, scroll or wait
            if self.step_count < 10:
                print("Elements not found, scrolling to look for them")
                return 'scroll(coordinate=[640, 360], direction="down")', {}
            else:
                print("Task completed or maximum steps reached")
                return 'send_msg_to_user("Search task completed")', {}


def test_final_working_agent():
    """Test the final working agent."""
    
    # Set up experiment arguments
    agent_args = FinalWorkingAgentArgs()
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
    print("Final Working Agent Test")
    print("=" * 50)
    
    try:
        success = test_final_working_agent()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running final working agent: {e}")
        import traceback
        traceback.print_exc()
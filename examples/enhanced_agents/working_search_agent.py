#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class WorkingSearchAgentArgs(AbstractAgentArgs):
    """Arguments for the working search agent."""
    agent_name: str = "WorkingSearchAgent"
    
    def make_agent(self):
        """Create the agent instance."""
        return WorkingSearchAgent(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class WorkingSearchAgent(Agent):
    """Agent that properly extracts BIDs and uses them to interact with search elements."""
    
    def __init__(self, action_set: HighLevelActionSet, args: WorkingSearchAgentArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        self.search_attempted = False
        
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
        print(f"STEP {self.step_count}: WORKING SEARCH AGENT")
        print(f"{'='*60}")
        
        # Extract accessibility tree data
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            
            if isinstance(axtree_obj, dict) and 'nodes' in axtree_obj:
                nodes = axtree_obj['nodes']
                print(f"Total nodes: {len(nodes)}")
                
                # Find interactive elements with proper BID extraction
                interactive_elements = []
                search_elements = []
                textbox_elements = []
                button_elements = []
                
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {})).lower()
                        name_str = self.extract_name(node.get('name', {})).lower()
                        
                        # Get the actual BID - try different possible field names
                        bid = None
                        for bid_field in ['browsergym_id', 'bid', 'backendDOMNodeId', 'nodeId']:
                            if bid_field in node:
                                bid = str(node[bid_field])
                                break
                        
                        if not bid:
                            continue
                            
                        # Categorize elements
                        if role_str == 'textbox':
                            textbox_elements.append((i, node, role_str, name_str, bid))
                            if any(keyword in name_str for keyword in ['search', 'find', 'query']):
                                search_elements.append((i, node, role_str, name_str, bid))
                        elif role_str == 'button':
                            button_elements.append((i, node, role_str, name_str, bid))
                            if any(keyword in name_str for keyword in ['search', 'find', 'submit']):
                                search_elements.append((i, node, role_str, name_str, bid))
                        elif role_str in ['link', 'searchbox', 'combobox']:
                            interactive_elements.append((i, node, role_str, name_str, bid))
                
                print(f"Found {len(textbox_elements)} textbox elements")
                print(f"Found {len(button_elements)} button elements")
                print(f"Found {len(search_elements)} search-related elements")
                
                # Show what we found
                if textbox_elements:
                    print(f"\nTextbox elements:")
                    for i, (node_idx, node, role, name, bid) in enumerate(textbox_elements[:3]):
                        print(f"  {i+1}. Node {node_idx}: name='{name}', bid='{bid}'")
                
                if button_elements:
                    print(f"\nButton elements:")
                    for i, (node_idx, node, role, name, bid) in enumerate(button_elements[:3]):
                        print(f"  {i+1}. Node {node_idx}: name='{name}', bid='{bid}'")
                
                if search_elements:
                    print(f"\nSearch-related elements:")
                    for i, (node_idx, node, role, name, bid) in enumerate(search_elements):
                        print(f"  {i+1}. Node {node_idx}: role='{role}', name='{name}', bid='{bid}'")
                
                # Try to perform search action
                if not self.search_attempted:
                    # Look for a search textbox first
                    search_textbox = None
                    for node_idx, node, role, name, bid in textbox_elements:
                        if any(keyword in name.lower() for keyword in ['search', 'find', 'query']):
                            search_textbox = (node_idx, node, role, name, bid)
                            break
                    
                    # If no explicit search textbox, try any textbox
                    if not search_textbox and textbox_elements:
                        search_textbox = textbox_elements[0]
                    
                    if search_textbox:
                        node_idx, node, role, name, bid = search_textbox
                        print(f"\nAttempting to type 'laptop' in textbox: {name} (bid: {bid})")
                        self.search_attempted = True
                        return f'type(bid="{bid}", text="laptop")', {}
                    
                    # If no textbox, try clicking a search button
                    search_button = None
                    for node_idx, node, role, name, bid in button_elements:
                        if any(keyword in name.lower() for keyword in ['search', 'find', 'submit']):
                            search_button = (node_idx, node, role, name, bid)
                            break
                    
                    if search_button:
                        node_idx, node, role, name, bid = search_button
                        print(f"\nAttempting to click search button: {name} (bid: {bid})")
                        self.search_attempted = True
                        return f'click(bid="{bid}")', {}
                    
                    # If no specific search elements, try any button
                    if button_elements:
                        node_idx, node, role, name, bid = button_elements[0]
                        print(f"\nAttempting to click first button: {name} (bid: {bid})")
                        self.search_attempted = True
                        return f'click(bid="{bid}")', {}
                
                # If we've already attempted search, scroll to see more content
                if self.step_count <= 5:
                    print(f"\nScrolling to see more content (step {self.step_count})")
                    return 'scroll(0, 3)', {}
                else:
                    print(f"\nCompleting search attempt after {self.step_count} steps")
                    return 'send_msg_to_user("Search attempt completed")', {}
        
        # Fallback action
        print(f"\nNo accessibility tree found, scrolling")
        return 'scroll(0, 3)', {}


def test_working_search_agent():
    """Test the working search agent."""
    
    # Set up experiment arguments
    agent_args = WorkingSearchAgentArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=8)
    
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
    print("Testing Working Search Agent")
    print("=" * 50)
    
    try:
        success = test_working_search_agent()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running working search agent: {e}")
        import traceback
        traceback.print_exc()
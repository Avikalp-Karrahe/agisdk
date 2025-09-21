#!/usr/bin/env python3

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class FinalInspectorArgs(AbstractAgentArgs):
    """Arguments for the final inspector agent."""
    agent_name: str = "FinalInspector"
    
    def make_agent(self):
        """Create the agent instance."""
        return FinalInspector(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class FinalInspector(Agent):
    """Agent that properly extracts role and name from accessibility tree nodes."""
    
    def __init__(self, action_set: HighLevelActionSet, args: FinalInspectorArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        
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
        
        print(f"\n{'='*80}")
        print(f"STEP {self.step_count}: FINAL INSPECTION WITH PROPER EXTRACTION")
        print(f"{'='*80}")
        
        # Extract accessibility tree data
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            
            if isinstance(axtree_obj, dict) and 'nodes' in axtree_obj:
                nodes = axtree_obj['nodes']
                print(f"Total nodes: {len(nodes)}")
                
                # Examine first few nodes to understand structure
                print(f"\nExamining first 3 nodes to understand structure:")
                for i, node in enumerate(nodes[:3]):
                    if isinstance(node, dict):
                        print(f"\n--- Node {i} ---")
                        role = node.get('role', {})
                        name = node.get('name', {})
                        print(f"Role dict: {role}")
                        print(f"Name dict: {name}")
                        print(f"Extracted role: '{self.extract_role(role)}'")
                        print(f"Extracted name: '{self.extract_name(name)}'")
                
                # Now find interactive elements properly
                interactive_elements = []
                search_elements = []
                
                interactive_roles = ['textbox', 'button', 'link', 'searchbox', 'combobox', 'menuitem', 'tab']
                search_keywords = ['search', 'find', 'query']
                
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {})).lower()
                        name_str = self.extract_name(node.get('name', {})).lower()
                        
                        # Check if interactive
                        if role_str in interactive_roles:
                            interactive_elements.append((i, node, role_str, name_str))
                            
                            # Check if search-related
                            if any(keyword in name_str for keyword in search_keywords):
                                search_elements.append((i, node, role_str, name_str))
                
                print(f"\nFound {len(interactive_elements)} interactive elements:")
                for i, (node_idx, node, role, name) in enumerate(interactive_elements[:10]):
                    bid = node.get('browsergym_id', 'no-bid')
                    print(f"  {i+1}. Node {node_idx}: role='{role}', name='{name}', bid='{bid}'")
                
                print(f"\nFound {len(search_elements)} search-related elements:")
                for i, (node_idx, node, role, name) in enumerate(search_elements):
                    bid = node.get('browsergym_id', 'no-bid')
                    print(f"  {i+1}. Node {node_idx}: role='{role}', name='{name}', bid='{bid}'")
                
                # Also look for any elements with "search" in their name regardless of role
                all_search_elements = []
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {})).lower()
                        name_str = self.extract_name(node.get('name', {})).lower()
                        
                        if any(keyword in name_str for keyword in search_keywords):
                            all_search_elements.append((i, node, role_str, name_str))
                
                print(f"\nAll elements with 'search' in name (any role): {len(all_search_elements)}")
                for i, (node_idx, node, role, name) in enumerate(all_search_elements[:5]):
                    bid = node.get('browsergym_id', 'no-bid')
                    print(f"  {i+1}. Node {node_idx}: role='{role}', name='{name}', bid='{bid}'")
                
                # Look for any textbox elements specifically
                textbox_elements = []
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {})).lower()
                        name_str = self.extract_name(node.get('name', {})).lower()
                        
                        if 'textbox' in role_str or 'input' in role_str:
                            textbox_elements.append((i, node, role_str, name_str))
                
                print(f"\nAll textbox/input elements: {len(textbox_elements)}")
                for i, (node_idx, node, role, name) in enumerate(textbox_elements):
                    bid = node.get('browsergym_id', 'no-bid')
                    print(f"  {i+1}. Node {node_idx}: role='{role}', name='{name}', bid='{bid}'")
                
                # Show role distribution
                role_counts = {}
                for node in nodes:
                    if isinstance(node, dict):
                        role_str = self.extract_role(node.get('role', {}))
                        role_counts[role_str] = role_counts.get(role_str, 0) + 1
                
                print(f"\nRole distribution (top 10):")
                sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
                for role, count in sorted_roles[:10]:
                    print(f"  {role}: {count}")
        
        # End after first step
        print(f"\nEnding final inspection after step {self.step_count}")
        return 'send_msg_to_user("Final inspection complete")', {}


def test_final_inspector():
    """Test the final inspector agent."""
    
    # Set up experiment arguments
    agent_args = FinalInspectorArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=1)
    
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
    print("Testing Final Inspector Agent")
    print("=" * 50)
    
    try:
        success = test_final_inspector()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running final inspector: {e}")
        import traceback
        traceback.print_exc()
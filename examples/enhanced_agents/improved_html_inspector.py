#!/usr/bin/env python3

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class ImprovedHtmlInspectorArgs(AbstractAgentArgs):
    """Arguments for the improved HTML inspector agent."""
    agent_name: str = "ImprovedHtmlInspector"
    
    def make_agent(self):
        """Create the agent instance."""
        return ImprovedHtmlInspector(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class ImprovedHtmlInspector(Agent):
    """Agent that properly extracts and prints DOM and accessibility tree data."""
    
    def __init__(self, action_set: HighLevelActionSet, args: ImprovedHtmlInspectorArgs):
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
        print(f"STEP {self.step_count}: IMPROVED HTML INSPECTION")
        print(f"{'='*80}")
        print(f"URL: {url}")
        print(f"Goal: {goal}")
        
        # Print all observation keys
        print(f"\nObservation keys: {list(obs.keys())}")
        
        # Extract DOM object data
        if 'dom_object' in obs:
            dom_obj = obs['dom_object']
            print(f"\nDOM_OBJECT structure:")
            print(f"  Type: {type(dom_obj)}")
            print(f"  Keys: {list(dom_obj.keys()) if isinstance(dom_obj, dict) else 'Not a dict'}")
            
            if isinstance(dom_obj, dict):
                # Check documents
                if 'documents' in dom_obj:
                    documents = dom_obj['documents']
                    print(f"  Documents type: {type(documents)}")
                    if isinstance(documents, list) and documents:
                        print(f"  Number of documents: {len(documents)}")
                        doc = documents[0]
                        print(f"  First document type: {type(doc)}")
                        if isinstance(doc, dict):
                            print(f"  First document keys: {list(doc.keys())}")
                            # Look for HTML content
                            for key, value in doc.items():
                                if isinstance(value, str) and len(value) > 100:
                                    print(f"  Document['{key}'] (first 1000 chars):")
                                    print("-" * 40)
                                    print(value[:1000])
                                    print("-" * 40)
                                    
                                    # Count BID attributes in this content
                                    bids = re.findall(r'bid="([^"]*)"', value, re.IGNORECASE)
                                    if bids:
                                        print(f"  Found {len(bids)} BID attributes in document['{key}']:")
                                        for i, bid in enumerate(bids[:10]):
                                            print(f"    {i+1}. bid=\"{bid}\"")
                                        if len(bids) > 10:
                                            print(f"    ... and {len(bids) - 10} more")
                
                # Check strings
                if 'strings' in dom_obj:
                    strings = dom_obj['strings']
                    print(f"  Strings type: {type(strings)}")
                    if isinstance(strings, list):
                        print(f"  Number of strings: {len(strings)}")
                        for i, s in enumerate(strings[:5]):
                            if isinstance(s, str) and len(s) > 50:
                                print(f"  String {i} (first 200 chars): {s[:200]}")
        
        # Extract accessibility tree data
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            print(f"\nAXTREE_OBJECT structure:")
            print(f"  Type: {type(axtree_obj)}")
            print(f"  Keys: {list(axtree_obj.keys()) if isinstance(axtree_obj, dict) else 'Not a dict'}")
            
            if isinstance(axtree_obj, dict) and 'nodes' in axtree_obj:
                nodes = axtree_obj['nodes']
                print(f"  Nodes type: {type(nodes)}")
                if isinstance(nodes, list):
                    print(f"  Number of nodes: {len(nodes)}")
                    
                    # Look for interactive elements
                    interactive_count = 0
                    search_related = 0
                    
                    for i, node in enumerate(nodes[:20]):  # Check first 20 nodes
                        if isinstance(node, dict):
                            role = node.get('role', '')
                            name = node.get('name', '')
                            value = node.get('value', '')
                            
                            # Check if it's interactive
                            if role in ['textbox', 'button', 'link', 'searchbox', 'combobox']:
                                interactive_count += 1
                                print(f"  Interactive node {i}: role='{role}', name='{name}', value='{value}'")
                                
                                # Check if search-related
                                if any(term in (name + value).lower() for term in ['search', 'find', 'query']):
                                    search_related += 1
                                    print(f"    ^ This is SEARCH-RELATED!")
                    
                    print(f"  Total interactive elements found: {interactive_count}")
                    print(f"  Total search-related elements found: {search_related}")
                    
                    # Print all node roles for debugging
                    roles = [node.get('role', 'no-role') for node in nodes if isinstance(node, dict)]
                    role_counts = {}
                    for role in roles:
                        role_counts[role] = role_counts.get(role, 0) + 1
                    print(f"  Node roles summary: {dict(sorted(role_counts.items()))}")
        
        # Check extra element properties
        if 'extra_element_properties' in obs:
            extra_props = obs['extra_element_properties']
            print(f"\nEXTRA_ELEMENT_PROPERTIES:")
            print(f"  Type: {type(extra_props)}")
            if isinstance(extra_props, dict):
                print(f"  Keys: {list(extra_props.keys())}")
                print(f"  Number of elements with extra properties: {len(extra_props)}")
        
        # Try simple actions based on step
        if self.step_count <= 2:
            print(f"\nTaking scroll action for step {self.step_count}")
            return 'scroll(0, 3)', {}
        else:
            print(f"\nEnding inspection after {self.step_count} steps")
            return 'send_msg_to_user("Improved HTML inspection complete")', {}


def test_improved_html_inspector():
    """Test the improved HTML inspector agent."""
    
    # Set up experiment arguments
    agent_args = ImprovedHtmlInspectorArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=3)
    
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
    print("Testing Improved HTML Inspector Agent")
    print("=" * 50)
    
    try:
        success = test_improved_html_inspector()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running improved HTML inspector: {e}")
        import traceback
        traceback.print_exc()
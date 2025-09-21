#!/usr/bin/env python3

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class DetailedNodeInspectorArgs(AbstractAgentArgs):
    """Arguments for the detailed node inspector agent."""
    agent_name: str = "DetailedNodeInspector"
    
    def make_agent(self):
        """Create the agent instance."""
        return DetailedNodeInspector(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class DetailedNodeInspector(Agent):
    """Agent that examines the detailed structure of accessibility tree nodes."""
    
    def __init__(self, action_set: HighLevelActionSet, args: DetailedNodeInspectorArgs):
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
        
        print(f"\n{'='*80}")
        print(f"STEP {self.step_count}: DETAILED NODE INSPECTION")
        print(f"{'='*80}")
        
        # Extract accessibility tree data
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            
            if isinstance(axtree_obj, dict) and 'nodes' in axtree_obj:
                nodes = axtree_obj['nodes']
                print(f"Total nodes: {len(nodes)}")
                
                # Examine first 10 nodes in detail
                print(f"\nDetailed examination of first 10 nodes:")
                for i, node in enumerate(nodes[:10]):
                    print(f"\n--- Node {i} ---")
                    if isinstance(node, dict):
                        print(f"Keys: {list(node.keys())}")
                        for key, value in node.items():
                            if isinstance(value, str) and len(value) < 100:
                                print(f"  {key}: '{value}'")
                            elif isinstance(value, (int, float, bool)):
                                print(f"  {key}: {value}")
                            elif isinstance(value, list) and len(value) < 10:
                                print(f"  {key}: {value}")
                            else:
                                print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                    else:
                        print(f"Node is not a dict: {type(node)}")
                
                # Look for nodes with specific attributes that might indicate interactivity
                print(f"\nSearching for potentially interactive nodes...")
                interactive_indicators = ['role', 'name', 'value', 'description', 'clickable', 'focusable', 'editable']
                
                interactive_nodes = []
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        # Check if node has any interactive indicators
                        has_indicators = any(key in node for key in interactive_indicators)
                        if has_indicators:
                            interactive_nodes.append((i, node))
                
                print(f"Found {len(interactive_nodes)} nodes with interactive indicators")
                
                # Show first 5 interactive nodes
                for i, (node_idx, node) in enumerate(interactive_nodes[:5]):
                    print(f"\n--- Interactive Node {node_idx} ---")
                    for key in interactive_indicators:
                        if key in node:
                            value = node[key]
                            if isinstance(value, str) and len(value) < 200:
                                print(f"  {key}: '{value}'")
                            else:
                                print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                
                # Look for nodes that might be search-related
                print(f"\nSearching for search-related nodes...")
                search_terms = ['search', 'find', 'query', 'input', 'textbox', 'searchbox']
                search_nodes = []
                
                for i, node in enumerate(nodes):
                    if isinstance(node, dict):
                        # Check all string values in the node
                        node_text = ' '.join([str(v).lower() for v in node.values() if isinstance(v, str)])
                        if any(term in node_text for term in search_terms):
                            search_nodes.append((i, node))
                
                print(f"Found {len(search_nodes)} potentially search-related nodes")
                
                # Show first 3 search-related nodes
                for i, (node_idx, node) in enumerate(search_nodes[:3]):
                    print(f"\n--- Search Node {node_idx} ---")
                    print(f"Full node: {json.dumps(node, indent=2)[:500]}...")
        
        # Also check DOM object for BID attributes
        if 'dom_object' in obs:
            dom_obj = obs['dom_object']
            if isinstance(dom_obj, dict) and 'documents' in dom_obj:
                documents = dom_obj['documents']
                if isinstance(documents, list) and documents:
                    doc = documents[0]
                    if isinstance(doc, dict) and 'nodes' in doc:
                        dom_nodes = doc['nodes']
                        print(f"\nDOM nodes: {len(dom_nodes)}")
                        
                        # Look for nodes with bid attributes
                        bid_nodes = []
                        for i, node in enumerate(dom_nodes[:100]):  # Check first 100
                            if isinstance(node, dict) and 'attributes' in node:
                                attrs = node['attributes']
                                if isinstance(attrs, list):
                                    # Attributes are stored as [name1, value1, name2, value2, ...]
                                    for j in range(0, len(attrs), 2):
                                        if j + 1 < len(attrs) and attrs[j] == 'bid':
                                            bid_nodes.append((i, node, attrs[j + 1]))
                        
                        print(f"Found {len(bid_nodes)} DOM nodes with BID attributes")
                        for i, (node_idx, node, bid) in enumerate(bid_nodes[:5]):
                            print(f"  Node {node_idx}: bid='{bid}', nodeName='{node.get('nodeName', 'unknown')}'")
        
        # End after first step
        print(f"\nEnding detailed inspection after step {self.step_count}")
        return 'send_msg_to_user("Detailed node inspection complete")', {}


def test_detailed_node_inspector():
    """Test the detailed node inspector agent."""
    
    # Set up experiment arguments
    agent_args = DetailedNodeInspectorArgs()
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
    print("Testing Detailed Node Inspector Agent")
    print("=" * 50)
    
    try:
        success = test_detailed_node_inspector()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running detailed node inspector: {e}")
        import traceback
        traceback.print_exc()
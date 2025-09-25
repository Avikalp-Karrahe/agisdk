#!/usr/bin/env python3
"""
Debug script to examine DOM structure and understand bid attribute issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agisdk.REAL.browsergym.experiments import ExpArgs
from agisdk.REAL.browsergym.core.env import BrowserEnv
from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str
from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs
import re

def debug_dom_structure():
    """Debug the DOM structure to understand bid attribute issues."""
    
    # Create environment using the correct pattern
    from agisdk.REAL.browsergym.webclones.base import AbstractWebCloneTask
    
    env = BrowserEnv(
        task_entrypoint=AbstractWebCloneTask, 
        task_kwargs={"task_id": "omnizon-1"},
        headless=True
    )
    
    try:
        # Reset environment to get initial observation
        obs, info = env.reset()
        print(f"Initial observation keys: {list(obs.keys())}")
        
        # Check DOM and AXTree objects
        if "dom_object" in obs and obs["dom_object"] is not None:
            dom_text = flatten_dom_to_str(obs["dom_object"], extra_properties=obs.get("extra_element_properties", {}))
            print(f"\n=== DOM TEXT STRUCTURE ===")
            print(f"DOM text length: {len(dom_text)}")
            print(f"First 2000 characters:")
            print(dom_text[:2000])
            print(f"\n=== SEARCHING FOR BID ATTRIBUTES ===")
            
            # Search for bid attributes
            bid_pattern = r'bid="([^"]+)"'
            bids = re.findall(bid_pattern, dom_text)
            print(f"Found {len(bids)} bid attributes: {bids[:10]}")
            
            # Search for input elements
            input_pattern = r'<input[^>]*>'
            inputs = re.findall(input_pattern, dom_text)
            print(f"\nFound {len(inputs)} input elements:")
            for i, inp in enumerate(inputs[:5]):
                print(f"  {i+1}: {inp}")
            
            # Search for search-related elements
            search_patterns = [
                r'search',
                r'textbox',
                r'input.*type="text"',
                r'input.*placeholder',
            ]
            
            for pattern in search_patterns:
                matches = re.findall(pattern, dom_text, re.IGNORECASE)
                print(f"\nPattern '{pattern}' found {len(matches)} matches: {matches[:3]}")
        
        if "axtree_object" in obs and obs["axtree_object"] is not None:
            axtree_text = flatten_axtree_to_str(obs["axtree_object"], extra_properties=obs.get("extra_element_properties", {}))
            print(f"\n=== AXTREE TEXT STRUCTURE ===")
            print(f"AXTree text length: {len(axtree_text)}")
            print(f"First 1000 characters:")
            print(axtree_text[:1000])
            
            # Look for textbox elements in AXTree
            textbox_pattern = r'textbox'
            textboxes = re.findall(textbox_pattern, axtree_text, re.IGNORECASE)
            print(f"\nFound {len(textboxes)} textbox references in AXTree")
            
            # Look for numbered elements
            numbered_pattern = r'\[(\d+)\]'
            numbers = re.findall(numbered_pattern, axtree_text)
            print(f"Found {len(numbers)} numbered elements: {numbers[:10]}")
        
    finally:
        env.close()

if __name__ == "__main__":
    debug_dom_structure()
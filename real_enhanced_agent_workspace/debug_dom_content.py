#!/usr/bin/env python3
"""
Debug script to examine DOM content extraction in RealEnhancedAgent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agisdk.REAL.browsergym.utils.obs import flatten_dom_to_str, flatten_axtree_to_str
from agisdk.REAL.browsergym.core.env import BrowserEnv
from agisdk.REAL.browsergym.webclones.base import AbstractWebCloneTask
import re

def debug_dom_content():
    """Debug DOM content extraction"""
    print("🔍 Debugging DOM content extraction...")
    
    # Create a simple browser environment using the webclones task
    env = BrowserEnv(task_entrypoint=AbstractWebCloneTask, task_kwargs={"task_id": "omnizon-1"})
    
    try:
        # Reset environment to get initial observation
        obs, info = env.reset()  # env.reset() returns a tuple (obs, info)
        print(f"✅ Environment reset successful")
        print(f"📋 Available observation keys: {list(obs.keys())}")
        
        # Check DOM object
        if 'dom_object' in obs:
            dom_obj = obs['dom_object']
            extra_props = obs.get('extra_element_properties', {})
            print(f"🌐 DOM object type: {type(dom_obj)}")
            
            # Convert to string with bid filtering
            dom_text = flatten_dom_to_str(dom_obj, extra_properties=extra_props, filter_with_bid_only=True)
            print(f"📝 DOM text length (with bids only): {len(dom_text)}")
            print(f"📄 DOM text preview (first 1000 chars):\n{dom_text[:1000]}")
            
            # Convert to string without filtering
            dom_text_full = flatten_dom_to_str(dom_obj, extra_properties=extra_props)
            print(f"📝 DOM text length (full): {len(dom_text_full)}")
            
            # Look for bid attributes
            bid_pattern = r'bid="([^"]+)"'
            bids = re.findall(bid_pattern, dom_text_full)
            print(f"🎯 Found {len(bids)} bid attributes: {bids[:10]}...")  # Show first 10
            
        # Check AXTree object
        if 'axtree_object' in obs:
            axtree_obj = obs['axtree_object']
            extra_props = obs.get('extra_element_properties', {})
            print(f"🌳 AXTree object type: {type(axtree_obj)}")
            
            # Convert to string with bid filtering
            axtree_text = flatten_axtree_to_str(axtree_obj, extra_properties=extra_props, filter_with_bid_only=True)
            print(f"📝 AXTree text length (with bids only): {len(axtree_text)}")
            print(f"📄 AXTree text preview (first 1000 chars):\n{axtree_text[:1000]}")
            
            # Convert to string without filtering
            axtree_text_full = flatten_axtree_to_str(axtree_obj, extra_properties=extra_props)
            print(f"📝 AXTree text length (full): {len(axtree_text_full)}")
            
            # Look for bid attributes in AXTree
            bid_pattern = r'bid="([^"]+)"'
            bids_ax = re.findall(bid_pattern, axtree_text_full)
            print(f"🎯 Found {len(bids_ax)} bid attributes in AXTree: {bids_ax[:10]}...")  # Show first 10
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    finally:
        env.close()

if __name__ == "__main__":
    debug_dom_content()
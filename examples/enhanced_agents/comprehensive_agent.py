#!/usr/bin/env python3

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.experiments import EnvArgs, ExpArgs, get_exp_result, AbstractAgentArgs
from agisdk.REAL.browsergym.experiments.loop import ExpResult, yield_all_exp_results
from agisdk.REAL.browsergym.experiments.agent import Agent


@dataclass
class ComprehensiveAgentArgs(AbstractAgentArgs):
    """Arguments for the comprehensive agent."""
    agent_name: str = "ComprehensiveAgent"
    
    def make_agent(self):
        """Create the agent instance."""
        return ComprehensiveAgent(
            action_set=HighLevelActionSet(
                subsets=["chat", "bid"],
                strict=False,
                multiaction=True,
            ),
            args=self,
        )


class ComprehensiveAgent(Agent):
    """Agent that comprehensively analyzes page elements."""
    
    def __init__(self, action_set: HighLevelActionSet, args: ComprehensiveAgentArgs):
        self.action_set = action_set
        self.args = args
        self.step_count = 0
        
    def obs_preprocessor(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess observation."""
        return obs
        
    def close(self):
        """Clean up resources."""
        pass
        
    def extract_all_elements(self, html: str) -> List[Dict[str, str]]:
        """Extract all interactive elements from HTML."""
        elements = []
        
        # Find all elements with bid attributes
        bid_pattern = r'bid="([^"]*)"[^>]*>([^<]*)'
        bid_matches = re.findall(bid_pattern, html, re.IGNORECASE)
        
        for bid, text in bid_matches:
            if bid and (text.strip() or 'input' in html[html.find(f'bid="{bid}"'):html.find(f'bid="{bid}"')+200].lower()):
                elements.append({
                    'bid': bid,
                    'text': text.strip(),
                    'type': 'bid_element'
                })
        
        # Find input elements
        input_pattern = r'<input[^>]*bid="([^"]*)"[^>]*(?:placeholder="([^"]*)")?[^>]*>'
        input_matches = re.findall(input_pattern, html, re.IGNORECASE)
        
        for bid, placeholder in input_matches:
            elements.append({
                'bid': bid,
                'text': placeholder or 'input',
                'type': 'input'
            })
            
        # Find button elements
        button_pattern = r'<button[^>]*bid="([^"]*)"[^>]*>([^<]*)</button>'
        button_matches = re.findall(button_pattern, html, re.IGNORECASE)
        
        for bid, text in button_matches:
            elements.append({
                'bid': bid,
                'text': text.strip(),
                'type': 'button'
            })
            
        # Find clickable elements (a, div with onclick, etc.)
        clickable_pattern = r'<(?:a|div|span)[^>]*bid="([^"]*)"[^>]*(?:onclick|href)[^>]*>([^<]*)'
        clickable_matches = re.findall(clickable_pattern, html, re.IGNORECASE)
        
        for bid, text in clickable_matches:
            elements.append({
                'bid': bid,
                'text': text.strip(),
                'type': 'clickable'
            })
            
        return elements
        
    def get_action(self, obs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Get the next action to take."""
        self.step_count += 1
        
        # Extract information from observation
        url = obs.get('url', 'Unknown')
        goal = obs.get('goal', 'No goal specified')
        html = obs.get('dom_txt', '')
        
        print(f"\nStep {self.step_count}: URL = {url}")
        print(f"Goal: {goal}")
        
        # Extract all elements
        elements = self.extract_all_elements(html)
        
        print(f"\nFound {len(elements)} interactive elements:")
        for i, elem in enumerate(elements[:20]):  # Show first 20 elements
            print(f"  {i+1}. BID: {elem['bid']}, Type: {elem['type']}, Text: '{elem['text']}'")
            
        if len(elements) > 20:
            print(f"  ... and {len(elements) - 20} more elements")
        
        # Look for search-related elements
        search_elements = [elem for elem in elements if 
                          'search' in elem['text'].lower() or 
                          'search' in elem['bid'].lower() or
                          elem['type'] == 'input']
        
        print(f"\nSearch-related elements ({len(search_elements)}):")
        for elem in search_elements:
            print(f"  - BID: {elem['bid']}, Type: {elem['type']}, Text: '{elem['text']}'")
        
        # Try different actions based on step
        if self.step_count == 1:
            # First, try to find and click on a search input
            for elem in search_elements:
                if elem['type'] == 'input':
                    print(f"Attempting to fill search input: {elem['bid']}")
                    return f'fill("{elem["bid"]}", "laptop")', {}
                    
        elif self.step_count == 2:
            # Try to find a search button or submit
            for elem in elements:
                if ('search' in elem['text'].lower() or 
                    'submit' in elem['text'].lower() or
                    elem['type'] == 'button'):
                    print(f"Attempting to click search button: {elem['bid']}")
                    return f'click("{elem["bid"]}")', {}
                    
        elif self.step_count == 3:
            # Try pressing Enter on any input field
            for elem in search_elements:
                if elem['type'] == 'input':
                    print(f"Attempting to press Enter on input: {elem['bid']}")
                    return f'key("Enter")', {}
                    
        elif self.step_count == 4:
            # Try clicking on any clickable element
            for elem in elements:
                if elem['type'] in ['clickable', 'button'] and elem['text']:
                    print(f"Attempting to click element: {elem['bid']}")
                    return f'click("{elem["bid"]}")', {}
                    
        else:
            # Default action - scroll or wait
            print("No more actions to try, scrolling down")
            return 'scroll(0, 3)', {}
            
        # If no specific action found, scroll
        print("No suitable elements found, scrolling")
        return 'scroll(0, 3)', {}


def test_comprehensive_agent():
    """Test the comprehensive agent."""
    
    # Set up experiment arguments
    agent_args = ComprehensiveAgentArgs()
    env_args = EnvArgs(task_name="webclones.omnizon-1", max_steps=10)
    
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
    
    print(f"Task: {exp_record.get('task_name', 'Unknown')}")
    print(f"  Reward: {exp_record.get('cum_reward', 0)}")
    print(f"  Success: {exp_record.get('cum_reward', 0) > 0}")
    print(f"  Steps: {exp_record.get('n_steps', 0)}")
    
    return exp_record.get('cum_reward', 0) > 0


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Comprehensive Agent")
    print("=" * 50)
    
    try:
        success = test_comprehensive_agent()
        print(f"Agent completed with success: {success}")
    except Exception as e:
        print(f"Error running comprehensive agent: {e}")
        import traceback
        traceback.print_exc()
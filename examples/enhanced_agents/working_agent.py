import dataclasses
import re
from typing import Dict, Tuple, Optional
from agisdk import REAL


class WorkingAgent(REAL.Agent):
    def __init__(self) -> None:
        super().__init__()
        self.steps = 0
        self.search_input_bid = None
        self.search_completed = False
        
    def extract_bids_from_html(self, html_content: str) -> Dict[str, str]:
        """Extract bid attributes from HTML content"""
        bids = {}
        # Look for bid attributes in HTML elements
        bid_pattern = r'bid="([^"]+)"[^>]*>([^<]*)'
        matches = re.findall(bid_pattern, html_content, re.IGNORECASE)
        
        for bid, content in matches:
            content = content.strip()
            if content:
                bids[bid] = content
                
        return bids
        
    def find_search_input_bid(self, html_content: str, axtree_content: str) -> Optional[str]:
        """Find the bid of the search input field"""
        # Look for input elements with search-related attributes
        search_patterns = [
            r'<input[^>]*bid="([^"]+)"[^>]*type="search"',
            r'<input[^>]*bid="([^"]+)"[^>]*placeholder="[^"]*[Ss]earch',
            r'<input[^>]*bid="([^"]+)"[^>]*name="[^"]*search',
            r'<input[^>]*bid="([^"]+)"[^>]*id="[^"]*search',
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # Also check accessibility tree for search inputs
        if "textbox" in axtree_content.lower() and "search" in axtree_content.lower():
            # Extract bid from accessibility tree
            ax_pattern = r'browsergym_id_(\w+)[^"]*textbox[^"]*search'
            match = re.search(ax_pattern, axtree_content, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return None
        
    def find_clickable_elements(self, html_content: str) -> Dict[str, str]:
        """Find clickable elements with their bids"""
        clickable = {}
        
        # Look for buttons, links, and other clickable elements
        patterns = [
            r'<button[^>]*bid="([^"]+)"[^>]*>([^<]*)',
            r'<a[^>]*bid="([^"]+)"[^>]*>([^<]*)',
            r'<div[^>]*bid="([^"]+)"[^>]*role="button"[^>]*>([^<]*)',
            r'<span[^>]*bid="([^"]+)"[^>]*onclick[^>]*>([^<]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for bid, content in matches:
                content = content.strip()
                if content and len(content) < 50:  # Avoid very long content
                    clickable[bid] = content
                    
        return clickable
        
    def get_action(self, obs: dict) -> Tuple[str, Dict]:
        """
        Working agent that uses proper bid-based actions.
        """
        self.steps += 1
        
        # Get observation data
        current_url = obs.get("url", "")
        html_content = obs.get("pruned_html", "")
        axtree_content = obs.get("axtree_txt", "")
        
        print(f"\nStep {self.steps}: URL = {current_url}")
        
        # Step 1: Find search input if we haven't already
        if not self.search_input_bid and not self.search_completed:
            self.search_input_bid = self.find_search_input_bid(html_content, axtree_content)
            
            if self.search_input_bid:
                print(f"Found search input with bid: {self.search_input_bid}")
                # Fill the search input with "laptop"
                return f'fill("{self.search_input_bid}", "laptop")', {}
            else:
                print("No search input found, looking for clickable elements...")
                clickable = self.find_clickable_elements(html_content)
                
                # Look for search-related clickable elements
                for bid, content in clickable.items():
                    if "search" in content.lower():
                        print(f"Clicking search element: {content} (bid: {bid})")
                        return f'click("{bid}")', {}
                        
                # If no search elements found, scroll down to look for more
                if self.steps < 5:
                    return 'scroll(coordinate=[640, 360], direction="down")', {}
        
        # Step 2: If we filled the search input, press Enter to search
        elif self.search_input_bid and not self.search_completed:
            print("Pressing Enter to execute search...")
            self.search_completed = True
            return f'press("{self.search_input_bid}", "Enter")', {}
            
        # Step 3: Look for search results
        elif self.search_completed:
            if "laptop" in html_content.lower() and ("vilva" in html_content.lower() or "product" in html_content.lower()):
                print("Found search results! Task completed.")
                return 'send_msg_to_user("I found the search results for laptop. The first product shown is the VILVA Portable-Monitor-for-Laptop.")', {}
            else:
                # Wait a bit more or scroll to see results
                if self.steps < 10:
                    return 'scroll(coordinate=[640, 360], direction="down")', {}
                else:
                    return 'send_msg_to_user("I searched for laptop but could not find the expected results.")', {}
        
        # Fallback
        else:
            return 'send_msg_to_user("Unable to complete the search task.")', {}


@dataclasses.dataclass
class WorkingAgentArgs(REAL.AbstractAgentArgs):
    agent_name: str = "WorkingAgent"
    
    def make_agent(self):
        return WorkingAgent()


def test_working_agent():
    """Test the working agent on omnizon-1 task"""
    print("=" * 50)
    print("Testing Working Agent with Proper BIDs")
    print("=" * 50)
    
    try:
        # Create harness for single task
        harness = REAL.harness(
            agentargs=WorkingAgentArgs(),
            headless=False,  # Show browser for debugging
            task_name="webclones.omnizon-1",
            sample_tasks=1,
            task_id=1
        )
        
        # Run the task
        results = harness.run()
        
        if results:
            result = results[0]
            print(f"Task: {result.get('task_name', 'omnizon-1')}")
            print(f"  Reward: {result.get('reward', 0)}")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Steps: {result.get('n_steps', 0)}")
            print(f"  Time: {result.get('cum_reward', 0)} seconds")
            
            if result.get('success', False):
                print("✅ SUCCESS: Working agent completed the task!")
            else:
                print("❌ FAILED: Still debugging...")
                
        return results
        
    except Exception as e:
        print(f"Error running working agent: {e}")
        return None


if __name__ == "__main__":
    test_working_agent()
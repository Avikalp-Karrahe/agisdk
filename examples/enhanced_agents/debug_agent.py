import dataclasses
from typing import Dict, Tuple, Optional
from agisdk import REAL


class DebugAgent(REAL.Agent):
    def __init__(self) -> None:
        super().__init__()
        self.steps = 0
        
    def get_action(self, obs: dict) -> Tuple[str, Dict]:
        """
        Debug agent that prints all observation details.
        """
        self.steps += 1
        
        print(f"\n{'='*60}")
        print(f"STEP {self.steps} - DEBUG OBSERVATION")
        print(f"{'='*60}")
        
        # Print basic info
        print(f"URL: {obs.get('url', 'N/A')}")
        print(f"Goal: {obs.get('goal_object', 'N/A')}")
        print(f"Last Action: {obs.get('last_action', 'N/A')}")
        print(f"Last Action Error: {obs.get('last_action_error', 'N/A')}")
        
        # Print HTML content (first 1000 chars)
        html_content = obs.get("pruned_html", "")
        print(f"\nHTML Content (first 1000 chars):")
        print("-" * 40)
        print(html_content[:1000])
        if len(html_content) > 1000:
            print("... (truncated)")
        
        # Print accessibility tree (first 1000 chars)
        axtree_content = obs.get("axtree_txt", "")
        print(f"\nAccessibility Tree (first 1000 chars):")
        print("-" * 40)
        print(axtree_content[:1000])
        if len(axtree_content) > 1000:
            print("... (truncated)")
        
        # Look for search-related elements
        search_elements = []
        if "search" in html_content.lower():
            search_elements.append("Found 'search' in HTML")
        if "input" in html_content.lower():
            search_elements.append("Found 'input' in HTML")
        if 'type="search"' in html_content:
            search_elements.append("Found search input type")
        if 'placeholder=' in html_content and 'search' in html_content.lower():
            search_elements.append("Found search placeholder")
            
        print(f"\nSearch Elements Found:")
        print("-" * 40)
        for element in search_elements:
            print(f"  - {element}")
        if not search_elements:
            print("  - No obvious search elements found")
        
        print(f"\n{'='*60}")
        
        # Simple action progression
        if self.steps == 1:
            return 'click("search")', {}
        elif self.steps == 2:
            return 'type(text="laptop")', {}
        elif self.steps == 3:
            return 'key("Enter")', {}
        elif self.steps < 8:
            return 'scroll(coordinate=[640, 360], direction="down")', {}
        else:
            return 'send_msg_to_user("Debug complete - examined page structure")', {}


@dataclasses.dataclass
class DebugAgentArgs(REAL.AbstractAgentArgs):
    agent_name: str = "DebugAgent"
    
    def make_agent(self):
        return DebugAgent()


def test_debug_agent():
    """Test the debug agent on omnizon-1 task"""
    print("=" * 50)
    print("Testing Debug Agent")
    print("=" * 50)
    
    try:
        # Create harness for single task
        harness = REAL.harness(
            agentargs=DebugAgentArgs(),
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
                
        return results
        
    except Exception as e:
        print(f"Error running debug agent: {e}")
        return None


if __name__ == "__main__":
    test_debug_agent()
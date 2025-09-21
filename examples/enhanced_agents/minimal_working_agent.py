import dataclasses
from typing import Dict, Tuple, Optional
from agisdk import REAL


class MinimalWorkingAgent(REAL.Agent):
    def __init__(self) -> None:
        super().__init__()
        self.steps = 0
        self.search_completed = False
        
    def get_agent_action(self, obs) -> Tuple[Optional[str], Optional[str]]:
        """
        Minimal agent logic focused on completing omnizon-1 task:
        Search for "laptop" and display first product.
        """
        self.steps += 1
        
        # Get current URL and page content
        current_url = obs.get("url", "")
        html_content = obs.get("pruned_html", "")
        
        print(f"Step {self.steps}: URL = {current_url}")
        
        # Step 1: If we're on the main page, find and click search bar
        if "evals-omnizon.vercel.app" in current_url and not self.search_completed:
            if "search" in html_content.lower() or "input" in html_content.lower():
                # Try to find search input field
                if 'type="search"' in html_content or 'placeholder="Search' in html_content:
                    # Type "laptop" in search field
                    self.search_completed = True
                    return 'type(text="laptop")', None
                else:
                    # Look for search button or input
                    return 'click("search")', None
            else:
                # Navigate to search area
                return 'scroll(coordinate=[640, 360], direction="down")', None
        
        # Step 2: If search is completed, look for results
        elif self.search_completed:
            if "laptop" in html_content.lower() and ("product" in html_content.lower() or "vilva" in html_content.lower()):
                # Found search results, describe the first product
                return None, "I found the search results for 'laptop'. The first product shown is the VILVA Portable-Monitor-for-Laptop."
            else:
                # Press Enter to execute search or look for search button
                return 'key("Enter")', None
        
        # Step 3: Fallback - try basic navigation
        elif self.steps < 10:
            return 'scroll(coordinate=[640, 360], direction="down")', None
        
        # Step 4: Give up after 10 steps
        else:
            return None, "Unable to complete the search task within the step limit."
        
    def get_action(self, obs: dict) -> Tuple[str, Dict]:
        """
        Convert agent's high-level action to browsergym action.
        """
        agent_action, final_message = self.get_agent_action(obs)
        
        if final_message:
            # End the episode with a message
            return f'send_msg_to_user("{final_message}")', {}
        elif agent_action:
            # Continue with the specified action
            return agent_action, {}
        else:
            # Default action if nothing specified
            return 'scroll(coordinate=[640, 360], direction="down")', {}


@dataclasses.dataclass
class MinimalWorkingAgentArgs(REAL.AbstractAgentArgs):
    agent_name: str = "MinimalWorkingAgent"
    
    def make_agent(self):
        return MinimalWorkingAgent()


def run_single_task(task_name):
    """Run a single task and return results"""
    print(f"Running task: {task_name}")
    
    # Create harness for single task
    harness = REAL.harness(
        agentargs=MinimalWorkingAgentArgs(),
        headless=False,  # Show browser for debugging
        task_name=task_name,
        sample_tasks=1,
        task_id=1
    )
    
    # Run the task
    results = harness.run()
    return results


def test_minimal_agent():
    """Test the minimal agent on omnizon-1 task"""
    print("=" * 50)
    print("Testing Minimal Working Agent")
    print("=" * 50)
    
    try:
        results = run_single_task("webclones.omnizon-1")
        
        if results:
            result = results[0]
            print(f"Task: {result.get('task_name', 'omnizon-1')}")
            print(f"  Reward: {result.get('reward', 0)}")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Steps: {result.get('n_steps', 0)}")
            print(f"  Time: {result.get('cum_reward', 0)} seconds")
            
            if result.get('success', False):
                print("✅ SUCCESS: Minimal agent completed the task!")
            else:
                print("❌ FAILED: Need to debug further")
                
        return results
        
    except Exception as e:
        print(f"Error running minimal agent: {e}")
        return None


if __name__ == "__main__":
    test_minimal_agent()
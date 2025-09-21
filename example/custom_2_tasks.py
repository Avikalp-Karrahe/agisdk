import dataclasses
from typing import Dict, Tuple, Optional

from agisdk import REAL


class MyCustomAgent(REAL.Agent):
    def __init__(self) -> None:
        super().__init__()
        self.steps = 0
        
    def get_agent_action(self, obs) -> Tuple[Optional[str], Optional[str]]:
        """
        Core agent logic - analyze observation and decide on action.
        
        Returns:
            Tuple of (action, final_message)
            - If action is None, episode ends with final_message
            - If action is not None, the agent takes the action and continues
        """
        self.steps += 1
        
        # Example of simple decision making based on URL
        current_url = obs.get("url", "")
        
        # Simple logic: just end after a few steps
        if self.steps >= 25:
            return None, "Task completed after 25 steps"
        
        # Basic navigation action
        return "click(\"body\")", None
        
    def get_action(self, obs: dict) -> Tuple[str, Dict]:
        """
        Convert agent's high-level action to browsergym action.
        This method is required by the browsergym interface.
        """
        agent_action, final_message = self.get_agent_action(obs)
        
        if final_message:
            # End the episode with a message
            return f"send_msg_to_user(\"{final_message}\")", {}
        else:
            # Continue with the specified action
            return agent_action, {}

@dataclasses.dataclass
class MyCustomAgentArgs(REAL.AbstractAgentArgs):
    agent_name: str = "MyCustomAgent"
    
    def make_agent(self):
        return MyCustomAgent()


def run_single_task(task_name):
    """Run a single task and return results"""
    print(f"Running task: {task_name}")
    
    # Create harness for single task
    harness = REAL.harness(
        agentargs=MyCustomAgentArgs(),
        headless=True,
        task_name=task_name,
        sample_tasks=1,
        task_id=1
    )
    
    # Run the task
    results = harness.run()
    return results

def run_2_tasks():
    """Run exactly 2 tasks for comparison with enhanced agent"""
    print("=" * 50)
    print("REAL Benchmark Results (Custom Agent - 2 Tasks)")
    print("=" * 50)
    
    tasks = ["webclones.omnizon-1", "webclones.omnizon-2"]
    all_results = []
    
    for task_name in tasks:
        try:
            results = run_single_task(task_name)
            all_results.extend(results)
            
            # Print individual task result
            if results:
                result = results[0]
                print(f"Task: {result.get('task_name', task_name)}")
                print(f"  Reward: {result.get('reward', 0)}")
                print(f"  Success: {result.get('success', False)}")
                print(f"  Steps: {result.get('n_steps', 0)}")
                print()
        except Exception as e:
            print(f"Error running task {task_name}: {e}")
    
    # Calculate and display summary statistics
    if all_results:
        total_tasks = len(all_results)
        successful_tasks = sum(1 for r in all_results if r.get('success', False))
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        avg_steps = sum(r.get('n_steps', 0) for r in all_results) / total_tasks if total_tasks > 0 else 0
        
        print("=" * 50)
        print("SUMMARY STATISTICS")
        print("=" * 50)
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Total Episodes: {total_tasks}")
        print(f"Average Steps: {avg_steps:.1f}")
        print(f"Successful Tasks: {successful_tasks}/{total_tasks}")
    
    return all_results

if __name__ == "__main__":
    results = run_2_tasks()
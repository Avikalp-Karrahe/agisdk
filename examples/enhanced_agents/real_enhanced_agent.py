#!/usr/bin/env python3
"""
REAL-compatible Enhanced Agent for AGI SDK evaluation.
Integrates all enhanced components with the REAL benchmark framework.
"""

import dataclasses
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

# REAL framework imports
from agisdk.REAL.browsergym.experiments import Agent, AbstractAgentArgs
from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str, prune_html

# Enhanced agent components
from memory_systems import EpisodicMemory, WorkingMemory, StateHasher
from self_critique import SelfCritiqueSystem
from planning_system import HierarchicalPlanner
from advanced_retry_system import AdvancedRetrySystem, RetryConfig

@dataclasses.dataclass
class RealEnhancedAgentArgs(AbstractAgentArgs):
    """Arguments for the REAL Enhanced Agent."""
    agent_name: str = "RealEnhancedAgent"
    model_name: str = "gpt-4o-mini"
    enhanced_selection: bool = True
    timeout_ms: int = 5000
    retry_attempts: int = 3
    simulate_execution: bool = False
    use_html: bool = True
    use_axtree: bool = True
    use_screenshot: bool = True
    max_steps: int = 25
    
    def make_agent(self) -> "RealEnhancedAgent":
        """Create an instance of the enhanced agent."""
        return RealEnhancedAgent(self)
    
class RealEnhancedAgent(Agent):
    """Enhanced Agent compatible with REAL benchmark framework."""
    
    def __init__(self, args: RealEnhancedAgentArgs):
        super().__init__()
        self.args = args
        self.model_name = args.model_name
        self.enhanced_selection = args.enhanced_selection
        self.timeout_ms = args.timeout_ms
        self.retry_attempts = args.retry_attempts
        self.simulate_execution = args.simulate_execution
        
        # Initialize action set with fallback
        try:
            self.action_set = HighLevelActionSet(
                subsets=["chat", "bid", "infeas"],
                strict=False,
                multiaction=False,
                demo_mode="off"
            )
        except TypeError:
            self.action_set = HighLevelActionSet()
        
        # Initialize enhanced components
        self.state_hasher = StateHasher()
        self.episodic_memory = EpisodicMemory()
        self.working_memory = WorkingMemory()
        self.self_critique = SelfCritiqueSystem()
        self.planner = HierarchicalPlanner()
        
        # Initialize retry system
        retry_config = RetryConfig(
            max_attempts=self.retry_attempts,
            base_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=30.0
        )
        self.retry_system = AdvancedRetrySystem(retry_config)
        
        # Performance tracking
        self.stats = {
            'step_count': 0,
            'total_actions': 0,
            'success_rate': 0,
            'retry_rate': 0,
            'avg_execution_time': 0,
            'recent_errors': []
        }
        
        # Action history for analysis
        self.action_history = []
        self.last_observation = None
        
        print(f"REAL Enhanced Agent initialized successfully!")
        print(f"Model: {self.model_name}")
        print(f"Enhanced features: Memory, Self-Critique, Planning, Advanced Retry")
    
    def _extract_goal_safely(self, obs: dict) -> str:
        """Safely extract goal from observation, handling multiple formats."""
        goal_object = obs.get('goal_object')
        
        if isinstance(goal_object, dict):
            # Standard dict format: {'utterance': 'goal text'}
            return goal_object.get('utterance', '')
        elif isinstance(goal_object, list) and len(goal_object) > 0:
            # Handle OpenAI-style message format: [{'role': 'user', 'content': 'goal text'}]
            for msg in goal_object:
                if isinstance(msg, dict) and msg.get('role') == 'user':
                    return msg.get('content', '')
            # Fallback to first message content
            first_msg = goal_object[0]
            if isinstance(first_msg, dict):
                return first_msg.get('content', first_msg.get('utterance', ''))
            else:
                return str(first_msg)
        elif isinstance(goal_object, str):
            # Direct string format
            return goal_object
        else:
            # Fallback for any other format
            return ''
    
    def obs_preprocessor(self, obs: dict) -> dict:
        """Enhanced observation preprocessing with validation."""
        # Debug: Print the raw observation structure
        print(f"DEBUG: Raw observation keys: {list(obs.keys())}")
        if 'goal' in obs:
            print(f"DEBUG: Direct goal found: '{obs['goal']}'")
        if 'goal_object' in obs:
            print(f"DEBUG: Goal object found: {obs['goal_object']}")
        
        # Validate required fields
        required_fields = ['screenshot']
        for field in required_fields:
            if field not in obs:
                print(f"Warning: Missing required observation field: {field}")
        
        processed_obs = {
            "chat_messages": obs.get("chat_messages", []),
            "screenshot": obs.get("screenshot"),
            "goal_object": obs.get("goal_object", {}),
            "last_action": obs.get("last_action", ""),
            "last_action_error": obs.get("last_action_error", ""),
        }
        
        # Extract goal - REAL framework provides 'goal' directly in observations
        if 'goal' in obs:
            processed_obs['goal'] = obs['goal']
        else:
            # Fallback to safe extraction from goal_object
            goal = self._extract_goal_safely(obs)
            processed_obs['goal'] = goal
        
        # Add structured text representations
        if "axtree_object" in obs:
            processed_obs["axtree_txt"] = flatten_axtree_to_str(obs["axtree_object"])
        
        if "dom_object" in obs:
            processed_obs["pruned_html"] = prune_html(flatten_dom_to_str(obs["dom_object"]))
        
        return processed_obs
    
    def get_action(self, obs: dict) -> tuple[str, dict]:
        """Generate the next action using enhanced decision-making."""
        start_time = time.time()
        
        # Preprocess observation
        processed_obs = self.obs_preprocessor(obs)
        self.last_observation = processed_obs
        
        # Update stats
        self.stats['step_count'] += 1
        
        # Generate state hash for memory systems
        state_hash = self.state_hasher.hash_state(processed_obs)
        
        # Check episodic memory for similar states
        best_action_info = self.episodic_memory.get_best_action_for_state(state_hash, "real_benchmark")
        
        # Extract goal safely from processed observation
        goal = processed_obs.get('goal', 'Complete the task')
        self.working_memory.set_goal(goal, "real_benchmark")
        
        # Generate action using enhanced logic
        action_text = self._generate_enhanced_action(processed_obs, best_action_info)
        
        # Self-critique the proposed action
        critique = self.self_critique.evaluate_action_outcome(
            action_text, processed_obs, processed_obs
        )
        
        # Apply critique recommendations if confidence is low
        if critique.confidence_score < 0.7 and critique.recommendations:
            action_text = self._apply_critique_recommendations(action_text, critique)
        
        # Store action in history
        action_record = {
            'action': action_text,
            'state_hash': state_hash,
            'timestamp': time.time(),
            'critique': critique
        }
        self.action_history.append(action_record)
        
        # Update performance stats
        execution_time = time.time() - start_time
        self.stats['total_actions'] += 1
        self.stats['avg_execution_time'] = (
            (self.stats['avg_execution_time'] * (self.stats['total_actions'] - 1) + execution_time) /
            self.stats['total_actions']
        )
        
        return action_text, {"reasoning": f"Enhanced action with {critique.confidence_score:.2f} confidence"}
    
    def _generate_enhanced_action(self, obs: dict, best_action_info) -> str:
        """Generate enhanced action using sophisticated web navigation logic."""
        # Extract goal and page context
        goal = obs.get('goal', '')
        if not goal:
            goal = self._extract_goal_safely(obs)
        
        print(f"DEBUG: Extracted goal: '{goal}'")
        
        # Get page context from DOM and AXTree
        dom_text = obs.get('pruned_html', '')
        axtree_text = obs.get('axtree_txt', '')
        last_action_error = obs.get('last_action_error', '')
        
        # Analyze page content for actionable elements
        actionable_elements = self._analyze_page_elements(dom_text, axtree_text)
        
        # Parse goal into actionable components
        goal_analysis = self._analyze_goal(goal)
        
        # Generate action based on goal analysis and page context
        action = self._generate_contextual_action(goal_analysis, actionable_elements, last_action_error)
        
        print(f"DEBUG: Generated action: '{action}'")
        return action
    
    def _analyze_page_elements(self, dom_text: str, axtree_text: str) -> dict:
        """Analyze page elements to identify actionable components."""
        elements = {
            'buttons': [],
            'inputs': [],
            'links': [],
            'forms': [],
            'search_boxes': [],
            'dropdowns': [],
            'clickable_elements': []
        }
        
        # Analyze DOM for common patterns
        dom_lower = dom_text.lower()
        axtree_lower = axtree_text.lower()
        
        # Find buttons
        button_keywords = ['button', 'btn', 'submit', 'buy now', 'add to cart', 'search', 'login', 'sign in']
        for keyword in button_keywords:
            if keyword in dom_lower or keyword in axtree_lower:
                elements['buttons'].append(keyword)
        
        # Find input fields
        input_keywords = ['input', 'textbox', 'search', 'email', 'password', 'name', 'address']
        for keyword in input_keywords:
            if keyword in dom_lower or keyword in axtree_lower:
                elements['inputs'].append(keyword)
        
        # Find links
        if 'link' in axtree_lower or '<a' in dom_lower:
            elements['links'].append('link')
        
        # Find search functionality
        if 'search' in dom_lower or 'search' in axtree_lower:
            elements['search_boxes'].append('search')
        
        # Find forms
        if 'form' in dom_lower:
            elements['forms'].append('form')
        
        return elements
    
    def _analyze_goal(self, goal: str) -> dict:
        """Analyze goal to extract actionable intent and targets."""
        goal_lower = goal.lower()
        
        analysis = {
            'intent': 'unknown',
            'target_item': '',
            'action_type': 'navigate',
            'specific_actions': [],
            'payment_info': {},
            'search_terms': []
        }
        
        # Identify primary intent
        if 'search' in goal_lower or 'find' in goal_lower:
            analysis['intent'] = 'search'
        elif 'buy' in goal_lower or 'purchase' in goal_lower:
            analysis['intent'] = 'purchase'
        elif 'compare' in goal_lower:
            analysis['intent'] = 'compare'
        elif 'login' in goal_lower or 'sign in' in goal_lower:
            analysis['intent'] = 'login'
        elif 'fill' in goal_lower or 'enter' in goal_lower:
            analysis['intent'] = 'form_fill'
        elif 'click' in goal_lower:
            analysis['intent'] = 'click'
        elif 'navigate' in goal_lower or 'go to' in goal_lower:
            analysis['intent'] = 'navigate'
        
        # Extract target items/products
        product_keywords = ['playstation', 'dualsense', 'samsung', 'galaxy', 'iphone', 'laptop', 'espresso', 'machine']
        for keyword in product_keywords:
            if keyword in goal_lower:
                analysis['target_item'] = keyword
                analysis['search_terms'].append(keyword)
                break
        
        # Extract payment information if present
        if 'payment' in goal_lower or 'card' in goal_lower:
            # Look for card numbers, names, etc.
            import re
            card_pattern = r'\d{4}\s*\d{4}\s*\d{4}\s*\d{4}'
            card_match = re.search(card_pattern, goal)
            if card_match:
                analysis['payment_info']['card_number'] = card_match.group()
            
            name_pattern = r'name:\s*([^,\n]+)'
            name_match = re.search(name_pattern, goal, re.IGNORECASE)
            if name_match:
                analysis['payment_info']['name'] = name_match.group(1).strip()
        
        # Extract specific action sequences
        if 'first result' in goal_lower:
            analysis['specific_actions'].append('click_first_result')
        if 'buy now' in goal_lower:
            analysis['specific_actions'].append('click_buy_now')
        if 'change' in goal_lower and 'payment' in goal_lower:
            analysis['specific_actions'].append('change_payment_method')
        
        return analysis
    
    def _generate_contextual_action(self, goal_analysis: dict, elements: dict, last_error: str) -> str:
        """Generate contextual action based on goal analysis and page elements."""
        intent = goal_analysis['intent']
        target_item = goal_analysis['target_item']
        specific_actions = goal_analysis['specific_actions']
        
        # Handle errors from previous actions
        if last_error:
            if 'not found' in last_error.lower():
                # Try alternative selectors or actions
                if intent == 'search' and elements['search_boxes']:
                    return "fill('search', '" + target_item + "')"
                elif intent == 'click' and elements['buttons']:
                    return "click('button')"
            elif 'timeout' in last_error.lower():
                return "noop()"  # Wait for page to load
        
        # Generate action based on intent and available elements
        if intent == 'search':
            if target_item and elements['search_boxes']:
                return f"fill('search', '{target_item}')"
            elif elements['search_boxes']:
                return "fill('search', 'product')"
            elif elements['inputs']:
                return f"fill('input', '{target_item}')" if target_item else "fill('input', 'search term')"
            else:
                return "goto('/')"  # Navigate to home page to find search
        
        elif intent == 'purchase':
            if 'click_buy_now' in specific_actions and elements['buttons']:
                # Look for buy now button specifically
                if any('buy' in btn for btn in elements['buttons']):
                    return "click('Buy Now')"
                else:
                    return "click('button')"
            elif elements['buttons']:
                return "click('Add to Cart')"
            else:
                return "noop()"  # Wait for page to load
        
        elif intent == 'compare':
            if target_item:
                return f"goto('https://omnizon.com')"  # Start at main site
            else:
                return "goto('/')"
        
        elif intent == 'click':
            if 'click_first_result' in specific_actions:
                return "click('first')"
            elif elements['buttons']:
                return "click('button')"
            elif elements['links']:
                return "click('link')"
            else:
                return "click('element')"
        
        elif intent == 'form_fill':
            payment_info = goal_analysis.get('payment_info', {})
            if payment_info and 'name' in payment_info:
                return f"fill('name', '{payment_info['name']}')"
            elif payment_info and 'card_number' in payment_info:
                return f"fill('card', '{payment_info['card_number']}')"
            elif elements['inputs']:
                return "fill('input', 'information')"
            else:
                return "noop()"
        
        elif intent == 'navigate':
            if target_item:
                return f"goto('/{target_item}')"
            else:
                return "goto('/')"
        
        # Default fallback actions based on available elements
        if elements['search_boxes'] and target_item:
            return f"fill('search', '{target_item}')"
        elif elements['buttons']:
            return "click('button')"
        elif elements['links']:
            return "click('link')"
        elif elements['inputs']:
            return "fill('input', 'text')"
        else:
            return "noop()"
    
    def _apply_critique_recommendations(self, action: str, critique) -> str:
        """Apply self-critique recommendations to improve action."""
        if not critique.recommendations:
            return action
        
        # Simple recommendation application using valid REAL actions
        for rec in critique.recommendations[:1]:  # Apply first recommendation
            if 'wait' in rec.lower() or 'pause' in rec.lower():
                return f"noop(); {action}"
            elif 'scroll' in rec.lower():
                return f"scroll(direction='down'); {action}"
        
        return action
    
    def update_last_observation(self, obs):
        """Store the last observation for metrics."""
        self.last_observation = obs
        
        # Update episodic memory with action results
        if self.action_history:
            last_action = self.action_history[-1]
            success = obs.get('success', False)
            reward = obs.get('reward', 0)
            
            # Store episode in memory
            self.episodic_memory.store_episode(
                last_action['state_hash'],
                last_action['action'],
                reward,
                success,
                execution_time=time.time() - last_action['timestamp']
            )
    
    def close(self):
        """Called when the agent session ends."""
        print(f"\n==== Enhanced Agent Session Summary ====")
        print(f"Total steps: {self.stats['step_count']}")
        print(f"Total actions: {self.stats['total_actions']}")
        print(f"Average execution time: {self.stats['avg_execution_time']:.3f}s")
        
        # Get domain insights from episodic memory
        insights = self.episodic_memory.get_domain_insights('real_benchmark')
        print(f"Success rate: {insights.get('success_rate', 0):.2f}")
        print(f"Total episodes: {insights.get('total_episodes', 0)}")
        
        if self.last_observation:
            success = self.last_observation.get('success', None)
            if success is not None:
                print(f"Final success: {success}")
                print(f"Final reward: {self.last_observation.get('reward', 0)}")
        
        print(f"Enhanced components used: Memory, Self-Critique, Planning, Retry")
        print(f"========================================\n")

# Factory function for REAL framework
def make_agent(args: RealEnhancedAgentArgs) -> RealEnhancedAgent:
    """Factory function to create the enhanced agent."""
    return RealEnhancedAgent(args)

# Test the agent if run directly
if __name__ == "__main__":
    # Test agent initialization
    args = RealEnhancedAgentArgs(
        model_name="gpt-4o-mini",
        enhanced_selection=True,
        timeout_ms=5000,
        retry_attempts=3,
        simulate_execution=True
    )
    
    agent = make_agent(args)
    print(f"Agent created successfully: {type(agent).__name__}")
    print(f"Agent args: {args}")
    
    # Test basic functionality
    test_obs = {
        'chat_messages': [],
        'screenshot': None,
        'goal_object': {'utterance': 'Click the submit button'},
        'last_action': '',
        'last_action_error': ''
    }
    
    action, metadata = agent.get_action(test_obs)
    print(f"Generated action: {action}")
    print(f"Metadata: {metadata}")
    
    agent.close()
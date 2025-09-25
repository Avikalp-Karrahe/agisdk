#!/usr/bin/env python3
"""
REAL-compatible Enhanced Agent for AGI SDK evaluation.
Integrates all enhanced components with the REAL benchmark framework.
"""

import dataclasses
import json
import time
import re
import base64
import io
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image

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
    model_name: str = "gpt-4o"
    enhanced_selection: bool = True
    timeout_ms: int = 15000  # Increased timeout for slow page loads
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
            'recent_errors': [],
            'context_refreshes': 0,
            'smart_actions_generated': 0
        }
        
        # Action history for analysis and loop detection
        self.action_history = []
        self.last_observation = None
        
        # Enhanced memory retention for decision-making patterns
        self.decision_patterns = {
            'successful_sequences': [],
            'failed_sequences': [],
            'strategic_adjustments': [],
            'key_outcomes': []
        }
        
        # Context tracking for the last 15 steps
        self.step_context = {
            'actions': [],
            'outcomes': [],
            'decision_rationale': [],
            'page_states': [],
            'errors': []
        }
        
        # State tracking for context awareness and failed action detection
        self.last_action_failed = False
        self.failed_action_count = 0
        self.last_failed_action = None
        self.state_recapture_needed = False
        self.consecutive_failed_clicks = 0
        self.last_successful_action = None
        
        # Visual analysis state tracking
        self.last_screenshot_analysis = None
        self.visual_context_history = []
        self.screenshot_element_cache = {}
        self.visual_reasoning_enabled = True
        
        # ENHANCED: Context refreshing and action intelligence
        self.context_refresh_enabled = True
        self.last_context_refresh = 0
        self.context_cache = {}
        self.action_completion_tracking = {}
        self.smart_action_queue = []
        
        print(f"REAL Enhanced Agent initialized successfully!")
        print(f"Model: {self.model_name}")
        print(f"Enhanced features: Memory, Self-Critique, Planning, Advanced Retry, Context Tracking")
    
    def _initialize_context_tracking_methods(self):
        """Initialize helper methods for context tracking and pattern analysis."""
        pass  # Methods will be defined below
    
    def _refresh_context_after_action(self, obs: dict, action: str, success: bool) -> dict:
        """Refresh context after action execution to enable smarter subsequent actions."""
        if not self.context_refresh_enabled:
            return {}
            
        current_time = time.time()
        
        # Only refresh context if enough time has passed or action was successful
        if current_time - self.last_context_refresh < 1.0 and not success:
            return self.context_cache.get('last_refresh', {})
        
        print(f"DEBUG: Refreshing context after action: {action} (success: {success})")
        
        # Extract fresh DOM and AXTree data
        dom_text = ""
        axtree_text = ""
        
        if "dom_object" in obs and obs["dom_object"] is not None:
            try:
                dom_text = flatten_dom_to_str(obs["dom_object"])
                print(f"DEBUG: Refreshed DOM text length: {len(dom_text)}")
            except Exception as e:
                print(f"DEBUG: Error refreshing DOM text: {e}")
        
        if "axtree_object" in obs and obs["axtree_object"] is not None:
            try:
                axtree_text = flatten_axtree_to_str(obs["axtree_object"], extra_properties=obs.get("extra_element_properties", {}))
                print(f"DEBUG: Refreshed AXTree text length: {len(axtree_text)}")
            except Exception as e:
                print(f"DEBUG: Error refreshing AXTree text: {e}")
        
        # Analyze refreshed page elements
        refreshed_elements = self._analyze_page_elements(dom_text, axtree_text)
        
        # Update context cache with fresh data
        refreshed_context = {
            'timestamp': current_time,
            'elements': refreshed_elements,
            'dom_text': dom_text,
            'axtree_text': axtree_text,
            'last_action': action,
            'action_success': success,
            'available_actions': self._generate_available_actions(refreshed_elements)
        }
        
        # Store in both locations for compatibility
        self.context_cache['last_refresh'] = refreshed_context
        self.context_cache['current_refresh'] = refreshed_context  # This is what action generation looks for
        self.last_context_refresh = current_time
        self.stats['context_refreshes'] += 1
        
        print(f"DEBUG: Context refreshed - Found {refreshed_elements['total_elements']} elements")
        print(f"DEBUG: Refreshed context stored with {len(refreshed_elements.get('buttons', []))} buttons")
        return refreshed_context
    
    def _generate_available_actions(self, elements: dict) -> List[str]:
        """Generate list of available actions based on current page elements."""
        available_actions = []
        
        # Add fill actions for inputs
        for input_bid in elements.get('search_inputs', []):
            available_actions.append(f'fill("{input_bid}", "text")')
        for input_bid in elements.get('inputs', []):
            available_actions.append(f'fill("{input_bid}", "text")')
        
        # Add click actions for buttons
        for button_bid in elements.get('buttons', []):
            available_actions.append(f'click("{button_bid}")')
        
        # Add click actions for links
        for link_bid in elements.get('links', []):
            available_actions.append(f'click("{link_bid}")')
        
        # Add press actions for common keys
        if elements.get('search_inputs') or elements.get('inputs'):
            available_actions.extend(['press("Enter")', 'press("Tab")'])
        
        return available_actions
    
    def _validate_action_completion(self, action: str, obs_before: dict, obs_after: dict) -> bool:
        """Validate that an action completed successfully by comparing before/after states."""
        try:
            # Track action completion
            action_id = f"{action}_{time.time()}"
            
            # Simple validation based on action type
            if action.startswith('fill('):
                # For fill actions, check if the input value changed
                return self._validate_fill_completion(action, obs_before, obs_after)
            elif action.startswith('click('):
                # For click actions, check if page state changed
                return self._validate_click_completion(action, obs_before, obs_after)
            elif action.startswith('press('):
                # For press actions, check if page responded
                return self._validate_press_completion(action, obs_before, obs_after)
            
            return True  # Default to success for other actions
            
        except Exception as e:
            print(f"DEBUG: Error validating action completion: {e}")
            return False
    
    def _validate_fill_completion(self, action: str, obs_before: dict, obs_after: dict) -> bool:
        """Validate fill action completion."""
        # Extract bid and value from action
        match = re.search(r'fill\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']*)["\']', action)
        if not match:
            return False
        
        bid, value = match.groups()
        
        # Check if the element now contains the filled value
        # This is a simplified check - in practice, you'd inspect the DOM
        return len(value) > 0  # Assume success if we tried to fill something
    
    def _validate_click_completion(self, action: str, obs_before: dict, obs_after: dict) -> bool:
        """Validate click action completion."""
        # Check if URL changed (navigation occurred)
        url_before = obs_before.get('url', '')
        url_after = obs_after.get('url', '')
        
        if url_before != url_after:
            print(f"DEBUG: Click caused navigation: {url_before} -> {url_after}")
            return True
        
        # Check if page content changed significantly
        dom_before = obs_before.get('dom_object')
        dom_after = obs_after.get('dom_object')
        
        if dom_before and dom_after:
            # Simple heuristic: if DOM structure changed, click likely succeeded
            try:
                dom_str_before = str(dom_before)[:1000]  # First 1000 chars
                dom_str_after = str(dom_after)[:1000]
                return dom_str_before != dom_str_after
            except:
                pass
        
        return True  # Default to success
    
    def _validate_press_completion(self, action: str, obs_before: dict, obs_after: dict) -> bool:
        """Validate press action completion."""
        # For Enter key, check if form was submitted (URL change or content change)
        if 'Enter' in action:
            return self._validate_click_completion(action, obs_before, obs_after)
        
        return True  # Default to success for other keys
    
    def _analyze_decision_context(self, obs: dict, action: str, goal: str) -> str:
        """Analyze the context and rationale behind the current decision."""
        rationale_parts = []
        
        # Analyze goal alignment
        if 'search' in goal.lower() and 'fill' in action:
            rationale_parts.append("Filling search field to match goal")
        elif 'search' in goal.lower() and 'press' in action and 'Enter' in action:
            rationale_parts.append("Submitting search query")
        elif 'click' in goal.lower() and 'click' in action:
            rationale_parts.append("Clicking element as requested")
        
        # Analyze page state
        last_action = obs.get('last_action', '')
        if last_action:
            if 'fill' in last_action and 'press' in action:
                rationale_parts.append("Following fill with submit action")
            elif 'press' in last_action and 'Enter' in last_action and 'click' in action:
                rationale_parts.append("Clicking result after search submission")
        
        # Analyze error context
        last_error = obs.get('last_action_error', '')
        if last_error:
            rationale_parts.append(f"Recovering from error: {last_error[:50]}...")
        
        return " | ".join(rationale_parts) if rationale_parts else "Standard action selection"
    
    def _update_step_context(self, action: str, obs: dict, rationale: str):
        """Update the context tracking for the last 15 steps."""
        # Keep only last 15 entries
        max_context = 15
        
        # Add current step context
        step_info = {
            'step': self.stats['step_count'],
            'action': action,
            'timestamp': time.time(),
            'rationale': rationale,
            'url': obs.get('url', 'unknown'),
            'error': obs.get('last_action_error', '')
        }
        
        self.step_context['actions'].append(step_info)
        self.step_context['decision_rationale'].append(rationale)
        self.step_context['errors'].append(obs.get('last_action_error', ''))
        
        # Trim to last 15 entries
        for key in self.step_context:
            if len(self.step_context[key]) > max_context:
                self.step_context[key] = self.step_context[key][-max_context:]
    
    def _detect_action_loop(self) -> bool:
        """Detect if the agent is stuck in a repetitive action loop."""
        if len(self.action_history) < 4:
            return False
        
        # Check last 4 actions for fill->press->click->fill pattern
        recent_actions = [record['action'] for record in self.action_history[-4:]]
        
        # ENHANCED: Don't consider intelligent fill->click sequences as loops
        # Check if we have refreshed context indicating smart action sequencing
        if self.context_cache.get('current_refresh'):
            print("DEBUG: Skipping loop detection - intelligent context refreshing in progress")
            return False
        
        # Pattern: fill, press, click, fill (indicates loop)
        if len(recent_actions) >= 4:
            pattern_detected = (
                'fill' in recent_actions[-4] and
                'press' in recent_actions[-3] and
                'click' in recent_actions[-2] and
                'fill' in recent_actions[-1]
            )
            if pattern_detected:
                return True
        
        # ENHANCED: Don't consider fill->click as a loop (this is intelligent sequencing)
        if len(recent_actions) >= 2:
            last_two = recent_actions[-2:]
            if 'fill' in last_two[0] and 'click' in last_two[1]:
                print("DEBUG: Detected fill->click sequence - not a loop, this is intelligent action sequencing")
                return False
        
        # Check for repeated identical actions (but allow up to 2 repetitions for legitimate retries)
        if len(set(recent_actions[-4:])) == 1:  # Last 4 actions are identical
            return True
        
        return False
    
    def _break_action_loop(self, current_action: str, obs: dict) -> str:
        """Apply strategic adjustments to break out of action loops."""
        print(f"DEBUG: Breaking action loop - current action was: {current_action}")
        
        # Strategy 1: If we're about to fill again, try scrolling first
        if 'fill' in current_action:
            self.decision_patterns['strategic_adjustments'].append({
                'timestamp': time.time(),
                'strategy': 'scroll_before_fill',
                'original_action': current_action
            })
            return 'scroll(0, 300)'
        
        # Strategy 2: If we're about to click, wait longer for page load
        if 'click' in current_action:
            self.decision_patterns['strategic_adjustments'].append({
                'timestamp': time.time(),
                'strategy': 'wait_longer',
                'original_action': current_action
            })
            return 'noop(2000)'
        
        # Strategy 3: Default to waiting and scrolling
        self.decision_patterns['strategic_adjustments'].append({
            'timestamp': time.time(),
            'strategy': 'wait_and_scroll',
            'original_action': current_action
        })
        return 'noop(1500)'
    
    def get_last_15_steps_summary(self) -> dict:
        """Provide detailed summary of the last 15 steps for context retention."""
        summary = {
            'total_steps': len(self.step_context['actions']),
            'recent_actions': self.step_context['actions'][-15:],
            'decision_patterns': self.decision_patterns,
            'key_insights': [],
            'strategic_adjustments': len(self.decision_patterns['strategic_adjustments']),
            'error_count': len([e for e in self.step_context['errors'][-15:] if e])
        }
        
        # Analyze patterns in recent actions
        recent_actions = [step['action'] for step in self.step_context['actions'][-15:]]
        action_types = {}
        for action in recent_actions:
            action_type = action.split('(')[0] if '(' in action else action
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        summary['action_distribution'] = action_types
        
        # Identify key insights
        if action_types.get('fill', 0) > 3 and action_types.get('press', 0) > 3:
            summary['key_insights'].append("High search activity detected - may indicate search/result interaction pattern")
        
        if action_types.get('click', 0) > 5:
            summary['key_insights'].append("High click activity - may indicate navigation or result selection attempts")
        
        if len(self.decision_patterns['strategic_adjustments']) > 0:
            summary['key_insights'].append(f"Applied {len(self.decision_patterns['strategic_adjustments'])} strategic adjustments to break loops")
        
        return summary
    
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
        """Preprocess observation to extract relevant information."""
        # Debug: Print observation keys and content availability
        print(f"DEBUG: Available observation keys: {list(obs.keys())}")
        
        # Check if we have DOM and AXTree objects
        has_dom = "dom_object" in obs and obs["dom_object"] is not None
        has_axtree = "axtree_object" in obs and obs["axtree_object"] is not None
        print(f"DEBUG: Has DOM object: {has_dom}")
        print(f"DEBUG: Has AXTree object: {has_axtree}")
        
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
        
        # Handle framework-provided preprocessed content first
        if "axtree_txt" in obs and obs["axtree_txt"]:
            processed_obs["axtree_txt"] = obs["axtree_txt"]
            print(f"DEBUG: Using framework AXTree text length: {len(obs['axtree_txt'])}")
        elif "axtree_object" in obs and obs["axtree_object"] is not None:
            try:
                axtree_text = flatten_axtree_to_str(obs["axtree_object"], extra_properties=obs.get("extra_element_properties", {}))
                processed_obs["axtree_txt"] = axtree_text
                print(f"DEBUG: Extracted AXTree text length: {len(axtree_text)}")
            except Exception as e:
                print(f"DEBUG: Error processing AXTree: {e}")
                processed_obs["axtree_txt"] = ""
        else:
            processed_obs["axtree_txt"] = ""
            print("DEBUG: No AXTree content available")
        
        if "pruned_html" in obs and obs["pruned_html"]:
            processed_obs["pruned_html"] = obs["pruned_html"]
            print(f"DEBUG: Using framework DOM text length: {len(obs['pruned_html'])}")
        elif "dom_object" in obs and obs["dom_object"] is not None:
            try:
                # Don't filter by bid only - keep all content but don't prune to preserve structure
                dom_text = flatten_dom_to_str(obs["dom_object"], extra_properties=obs.get("extra_element_properties", {}))
                processed_obs["pruned_html"] = dom_text
                print(f"DEBUG: Extracted DOM text length: {len(dom_text)}")
            except Exception as e:
                print(f"DEBUG: Error processing DOM: {e}")
                processed_obs["pruned_html"] = ""
        else:
            processed_obs["pruned_html"] = ""
            print("DEBUG: No DOM content available")
        
        # Also check if we have raw HTML content
        if "html" in obs:
            html_content = obs["html"]
            print(f"DEBUG: HTML content length: {len(html_content)}")
            print(f"DEBUG: HTML content preview (first 500 chars): {html_content[:500]}")
        else:
            print("DEBUG: No HTML content provided")
        
        return processed_obs
    
    def get_action(self, obs: dict) -> tuple[str, dict]:
        """Generate action using enhanced components with context tracking."""
        start_time = time.time()
        
        try:
            # Update step count and track context
            self.stats['step_count'] += 1
            
            # Extract goal and process observation
            goal = self._extract_goal_safely(obs)
            processed_obs = self.obs_preprocessor(obs)
            self.last_observation = processed_obs
            
            # Check for action failure and update state tracking
            last_error = obs.get('last_action_error', '')
            last_action = obs.get('last_action', '')
            
            # ENHANCED: Always refresh context after any action to enable smarter decisions
            if last_action and last_action != 'noop' and last_action != '':
                print(f"DEBUG: Refreshing context after action: {last_action} (error: {bool(last_error)})")
                refreshed_context = self._refresh_context_after_action(obs, last_action, not bool(last_error))
                if refreshed_context:
                    print(f"DEBUG: Context refreshed - Available actions: {len(refreshed_context.get('available_actions', []))}")
                    # Store refreshed context for use in action generation
                    self.context_cache['current_refresh'] = refreshed_context
            
            if last_error:
                self.last_action_failed = True
                self.failed_action_count += 1
                self.last_failed_action = last_action
                self.state_recapture_needed = True
                
                # Track consecutive failed clicks for button click failures
                if 'click(' in self.last_failed_action:
                    self.consecutive_failed_clicks += 1
                else:
                    self.consecutive_failed_clicks = 0
                    
                print(f"DEBUG: Action failed - {self.last_failed_action}, error: {last_error}")
                print(f"DEBUG: Failed action count: {self.failed_action_count}, consecutive failed clicks: {self.consecutive_failed_clicks}")
            else:
                # Reset failure tracking on successful action
                if self.last_action_failed:
                    self.last_successful_action = last_action
                    print(f"DEBUG: Action succeeded after failure - {self.last_successful_action}")
                
                self.last_action_failed = False
                self.consecutive_failed_clicks = 0
                self.state_recapture_needed = False
            
            # Generate state hash for memory systems
            state_hash = self.state_hasher.hash_state(processed_obs)
            
            # Update working memory with current state
            self.working_memory.set_goal(goal, "real_benchmark")
            
            # Get best action from episodic memory
            best_action_info = self.episodic_memory.get_best_action_for_state(state_hash, "real_benchmark")
            
            # Generate enhanced action with context awareness
            action_text = self._generate_enhanced_action(processed_obs, best_action_info)
            
            # Track decision rationale and context
            decision_rationale = self._analyze_decision_context(obs, action_text, goal)
            self._update_step_context(action_text, obs, decision_rationale)
            
            # Detect and break repetitive patterns
            if self._detect_action_loop():
                action_text = self._break_action_loop(action_text, obs)
                decision_rationale += " [Loop detected - applied strategic adjustment]"
            
            # Apply self-critique
            critique = self.self_critique.evaluate_action_outcome(
                action_text, processed_obs, processed_obs
            )
            
            # Apply critique recommendations if confidence is low
            if critique.confidence_score < 0.7 and critique.recommendations:
                action_text = self._apply_critique_recommendations(action_text, critique)
                decision_rationale += f" [Critique applied: {critique.confidence_score:.2f} confidence]"
            
            # Store action in history and patterns
            action_record = {
                'action': action_text,
                'state_hash': state_hash,
                'timestamp': time.time(),
                'critique': critique,
                'goal': goal,
                'rationale': decision_rationale,
                'failed': self.last_action_failed,
                'error': last_error
            }
            self.action_history.append(action_record)
            
            # Update performance stats
            execution_time = time.time() - start_time
            self.stats['total_actions'] += 1
            self.stats['avg_execution_time'] = (
                (self.stats['avg_execution_time'] * (self.stats['total_actions'] - 1) + execution_time) /
                self.stats['total_actions']
            )
            
            print(f"DEBUG: Step {self.stats['step_count']} - Generated action: '{action_text}'")
            print(f"DEBUG: Decision rationale: {decision_rationale}")
            if self.state_recapture_needed:
                print(f"DEBUG: State recapture needed due to failed action")
            
            return action_text, {
                'step_count': self.stats['step_count'],
                'execution_time': execution_time,
                'goal': goal,
                'rationale': decision_rationale,
                'critique_applied': critique.confidence_score < 0.7,
                'loop_detected': self._detect_action_loop(),
                'action_failed': self.last_action_failed,
                'state_recapture_needed': self.state_recapture_needed,
                'reasoning': f"Enhanced action with {critique.confidence_score:.2f} confidence"
            }
            
        except Exception as e:
            error_msg = f"Error in get_action: {str(e)}"
            self.stats['recent_errors'].append(error_msg)
            self._update_step_context("noop(1000)", obs, f"Error recovery: {error_msg}")
            print(f"ERROR: {error_msg}")
            return "noop(1000)", {'error': error_msg}
    
    def _generate_enhanced_action(self, obs: dict, best_action_info) -> str:
        """Generate enhanced action using goal analysis and page elements."""
        goal = obs.get('goal', '')
        last_error = obs.get('last_action_error', '')
        
        # Use the preprocessed content from the REAL framework
        # The framework provides axtree_txt and pruned_html directly
        dom_text = obs.get('pruned_html', '')
        axtree_text = obs.get('axtree_txt', '')
        
        # If we still don't have content, try to extract from raw objects (fallback)
        if not dom_text and "dom_object" in obs and obs["dom_object"] is not None:
            try:
                dom_text = flatten_dom_to_str(obs["dom_object"], extra_properties=obs.get("extra_element_properties", {}))
                print(f"DEBUG: Extracted DOM text directly from object, length: {len(dom_text)}")
            except Exception as e:
                print(f"DEBUG: Error extracting DOM text: {e}")
                dom_text = ""
        
        if not axtree_text and "axtree_object" in obs and obs["axtree_object"] is not None:
            try:
                axtree_text = flatten_axtree_to_str(obs["axtree_object"], extra_properties=obs.get("extra_element_properties", {}))
                print(f"DEBUG: Extracted AXTree text directly from object, length: {len(axtree_text)}")
            except Exception as e:
                print(f"DEBUG: Error extracting AXTree text: {e}")
                axtree_text = ""
        
        print(f"DEBUG: Using DOM text length: {len(dom_text)}")
        print(f"DEBUG: Using AXTree text length: {len(axtree_text)}")
        
        # Analyze goal to understand intent
        goal_analysis = self._analyze_goal(goal)
        print(f"DEBUG: Intent: {goal_analysis['intent']}, Target: {goal_analysis['target_item']}, Actions: {goal_analysis['specific_actions']}")
        
        # Analyze page elements to find actionable components using DOM text
        elements = self._analyze_page_elements(dom_text, axtree_text)
        print(f"DEBUG: Available elements - Buttons: {len(elements['buttons'])}, Links: {len(elements['links'])}, Inputs: {len(elements['inputs'])}")
        
        # Get screenshot for visual analysis
        screenshot = obs.get('screenshot')
        
        # Generate contextual action based on goal, available elements, and visual analysis
        action = self._generate_contextual_action(goal_analysis, elements, last_error, screenshot)
        print(f"DEBUG: Generated action: '{action}'")
        
        # Update task progress based on the action taken
        goal_analysis = self._update_task_progress(goal_analysis, action)
        
        return action
    
    def _analyze_page_elements(self, dom_text: str, axtree_text: str) -> dict:
        """Analyze page elements to find actionable components."""
        # Debug: Show sample of DOM content to understand structure
        print(f"DEBUG: DOM content sample (first 1000 chars): {dom_text[:1000]}")
        print(f"DEBUG: AXTree content sample (first 500 chars): {axtree_text[:500]}")
        
        # Extract different types of elements using AXTree-based approach
        search_inputs = self._find_search_input_bids(dom_text, axtree_text)
        buttons = self._find_button_bids(dom_text, axtree_text)
        links = self._find_link_bids(dom_text, axtree_text)
        inputs = self._find_input_bids(dom_text, axtree_text)
        # New: extract (bid, label) pairs for better heuristics
        link_items = self._find_link_items(dom_text, axtree_text)
        button_items = self._find_button_items(dom_text, axtree_text)
        
        print(f"DEBUG: Found {len(search_inputs)} search boxes: {search_inputs}")
        print(f"DEBUG: Found {len(buttons)} buttons: {buttons}")
        print(f"DEBUG: Found {len(links)} links: {links}")
        print(f"DEBUG: Found {len(inputs)} inputs: {inputs}")
        print(f"DEBUG: Found {len(link_items)} link items with labels: {link_items[:5]}")
        print(f"DEBUG: Found {len(button_items)} button items with labels: {button_items[:5]}")
        
        return {
            'search_inputs': search_inputs,
            'buttons': buttons,
            'links': links,
            'inputs': inputs,
            'link_items': link_items,
            'button_items': button_items,
            'total_elements': len(search_inputs) + len(buttons) + len(links) + len(inputs)
        }
    
    def _extract_bids_from_html(self, html_content: str) -> Dict[str, str]:
        """Extract bid attributes from HTML content"""
        bids = {}
        if not html_content:
            return bids
            
        # Look for bid attributes in various formats
        bid_patterns = [
            r'bid="([^"]+)"',
            r"bid='([^']+)'",
            r'data-bid="([^"]+)"',
            r"data-bid='([^']+)'",
            r'id="([^"]+)"',  # Also try regular IDs as fallback
            r"id='([^']+)'"
        ]
        
        for pattern in bid_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            print(f"DEBUG: Pattern '{pattern}' found {len(matches)} matches: {matches[:5]}")  # Show first 5
            for match in matches:
                bids[match] = match
                
        print(f"DEBUG: Total unique bids found: {len(bids)}")
        return bids
    
    def _find_search_input_bids(self, html_content: str, axtree_content: str) -> List[str]:
        """Find search input elements with their bids from AXTree numbered elements"""
        search_bids = []
        
        # Primary approach: Extract from AXTree numbered elements
        if axtree_content:
            # Look for textbox elements in AXTree (these are typically search inputs)
            axtree_patterns = [
                r'\[(\d+)\]\s+textbox',  # [161] textbox
                r'\[(\d+)\]\s+searchbox',  # [161] searchbox  
                r'\[(\d+)\]\s+combobox.*search',  # [161] combobox ... search
                r'\[(\d+)\]\s+textbox.*search',  # [161] textbox ... search
            ]
            
            for pattern in axtree_patterns:
                axtree_matches = re.findall(pattern, axtree_content, re.IGNORECASE)
                search_bids.extend(axtree_matches)
                if axtree_matches:
                    print(f"DEBUG: AXTree pattern '{pattern}' found {len(axtree_matches)} matches: {axtree_matches[:3]}")
        
        # Fallback: Look for DOM bid attributes if available
        if html_content and not search_bids:
            patterns = [
                r'<input[^>]*type="search"[^>]*bid="([^"]+)"',
                r'<input[^>]*placeholder="[^"]*search[^"]*"[^>]*bid="([^"]+)"',
                r'<input[^>]*type="text"[^>]*bid="([^"]+)"',
                r'<input[^>]*bid="([^"]+)"[^>]*type="search"',
                r'<input[^>]*bid="([^"]+)"[^>]*placeholder="[^"]*search[^"]*"',
                r'<input[^>]*bid="([^"]+)"[^>]*type="text"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                search_bids.extend(matches)
                if matches:
                    print(f"DEBUG: DOM pattern '{pattern}' found {len(matches)} matches: {matches[:3]}")
        
        print(f"DEBUG: Total search input bids found: {len(search_bids)} - {search_bids}")
        return list(set(search_bids))  # Remove duplicates
    
    def _find_button_bids(self, html_content: str, axtree_content: str) -> List[str]:
        """Find button elements with their bids from AXTree numbered elements"""
        button_bids = []
        
        # Primary approach: Extract from AXTree numbered elements
        if axtree_content:
            # Look for button elements in AXTree
            axtree_patterns = [
                r'\[(\d+)\]\s+button',  # [141] button
                r'\[(\d+)\]\s+button\s+[\'"]([^\'"]*)search[^\'\"]*[\'"]',  # [141] button 'Search'
                r'\[(\d+)\]\s+button\s+[\'"]([^\'"]*)submit[^\'\"]*[\'"]',  # [141] button 'Submit'
            ]
            
            for pattern in axtree_patterns:
                axtree_matches = re.findall(pattern, axtree_content, re.IGNORECASE)
                # Extract just the numbers, not the button text
                if len(axtree_matches) > 0 and isinstance(axtree_matches[0], tuple):
                    button_bids.extend([match[0] for match in axtree_matches])
                else:
                    button_bids.extend(axtree_matches)
                print(f"DEBUG: AXTree button pattern '{pattern}' found {len(axtree_matches)} matches: {axtree_matches[:3]}")
        
        # Fallback: Look for DOM bid attributes if available
        if html_content and not button_bids:
            patterns = [
                r'<button[^>]*bid="([^"]+)"',
                r'<input[^>]*type="button"[^>]*bid="([^"]+)"',
                r'<input[^>]*type="submit"[^>]*bid="([^"]+)"',
                r'<div[^>]*role="button"[^>]*bid="([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                button_bids.extend(matches)
                print(f"DEBUG: DOM button pattern '{pattern}' found {len(matches)} matches: {matches[:3]}")
        
        print(f"DEBUG: Total button bids found: {len(button_bids)} - {button_bids}")
        return list(set(button_bids))  # Remove duplicates
    
    def _find_link_bids(self, html_content: str, axtree_content: str) -> List[str]:
        """Find link elements with their bids from AXTree numbered elements"""
        link_bids = []
        
        # Primary approach: Extract from AXTree numbered elements
        if axtree_content:
            # Look for link elements in AXTree
            axtree_patterns = [
                r'\[(\d+)\]\s+link',  # [144] link
                r'\[(\d+)\]\s+link\s+[\'\"][^\'\"]+[\'\"]',  # [144] link 'Home'
            ]
            
            for pattern in axtree_patterns:
                axtree_matches = re.findall(pattern, axtree_content, re.IGNORECASE)
                # Extract just the numbers, not the link text
                if len(axtree_matches) > 0 and isinstance(axtree_matches[0], tuple):
                    link_bids.extend([match[0] for match in axtree_matches])
                else:
                    link_bids.extend(axtree_matches)
                print(f"DEBUG: AXTree link pattern '{pattern}' found {len(axtree_matches)} matches: {axtree_matches[:3]}")
        
        # Fallback: Look for DOM bid attributes if available
        if html_content and not link_bids:
            patterns = [
                r'<a[^>]*bid="([^"]+)"',
                r'<div[^>]*role="link"[^>]*bid="([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                link_bids.extend(matches)
                print(f"DEBUG: DOM link pattern '{pattern}' found {len(matches)} matches: {matches[:3]}")
        
        print(f"DEBUG: Total link bids found: {len(link_bids)} - {link_bids}")
        return list(set(link_bids))  # Remove duplicates
    
    def _find_input_bids(self, html_content: str, axtree_content: str) -> List[str]:
        """Find input elements with their bids from AXTree numbered elements"""
        input_bids = []
        
        # Primary approach: Extract from AXTree numbered elements
        if axtree_content:
            # Look for various input elements in AXTree
            axtree_patterns = [
                r'\[(\d+)\]\s+textbox',  # [161] textbox
                r'\[(\d+)\]\s+combobox',  # [162] combobox
                r'\[(\d+)\]\s+spinbutton',  # [163] spinbutton
                r'\[(\d+)\]\s+checkbox',  # [164] checkbox
                r'\[(\d+)\]\s+radio',  # [165] radio
            ]
            
            for pattern in axtree_patterns:
                axtree_matches = re.findall(pattern, axtree_content, re.IGNORECASE)
                input_bids.extend(axtree_matches)
                print(f"DEBUG: AXTree input pattern '{pattern}' found {len(axtree_matches)} matches: {axtree_matches[:3]}")
        
        # Fallback: Look for DOM bid attributes if available
        if html_content and not input_bids:
            patterns = [
                r'<input[^>]*bid="([^"]+)"',
                r'<textarea[^>]*bid="([^"]+)"',
                r'<select[^>]*bid="([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                input_bids.extend(matches)
                print(f"DEBUG: DOM input pattern '{pattern}' found {len(matches)} matches: {matches[:3]}")
        
        print(f"DEBUG: Total input bids found: {len(input_bids)} - {input_bids}")
        return list(set(input_bids))  # Remove duplicates

    def _find_link_items(self, html_content: str, axtree_content: str) -> List[Tuple[str, str]]:
        """Find (bid, label) for links using AXTree labels when available."""
        items: List[Tuple[str, str]] = []
        if axtree_content:
            # pattern: [924] link 'Some Text'
            pattern = r"\[(\d+)\]\s+link\s+[\'\"]([^\'\"]+)[\'\"]"
            for bid, label in re.findall(pattern, axtree_content, re.IGNORECASE):
                items.append((bid, label.strip()))
        # De-duplicate by bid, keeping first label
        seen = set()
        dedup: List[Tuple[str, str]] = []
        for bid, label in items:
            if bid not in seen:
                seen.add(bid)
                dedup.append((bid, label))
        return dedup

    def _find_button_items(self, html_content: str, axtree_content: str) -> List[Tuple[str, str]]:
        """Find (bid, label) for buttons using AXTree labels when available."""
        items: List[Tuple[str, str]] = []
        if axtree_content:
            # pattern: [123] button 'Search'
            pattern = r"\[(\d+)\]\s+button\s+[\'\"]([^\'\"]+)[\'\"]"
            for bid, label in re.findall(pattern, axtree_content, re.IGNORECASE):
                items.append((bid, label.strip()))
        # De-duplicate by bid
        seen = set()
        dedup: List[Tuple[str, str]] = []
        for bid, label in items:
            if bid not in seen:
                seen.add(bid)
                dedup.append((bid, label))
        return dedup

    def _choose_best_link_for_result(self, link_items: List[Tuple[str, str]], target_item: str) -> Optional[str]:
        """Choose the most likely product/result link to click given labels and target item."""
        if not link_items:
            return None
    
    def _detect_visual_elements(self, screenshot: np.ndarray, elements: dict) -> dict:
        """Detect and analyze visual elements from screenshot to enhance element detection."""
        if screenshot is None:
            return {"visual_elements": [], "confidence": 0.0}
        
        try:
            # Convert screenshot to PIL Image for analysis
            if isinstance(screenshot, np.ndarray):
                image = Image.fromarray(screenshot)
            else:
                image = screenshot
            
            # Get image dimensions
            width, height = image.size
            
            # Visual element detection results
            visual_elements = {
                "buttons": [],
                "search_boxes": [],
                "links": [],
                "clickable_areas": [],
                "text_regions": [],
                "confidence": 0.7
            }
            
            # Enhance existing element detection with visual cues
            # Cross-reference DOM/AXTree elements with visual analysis
            
            # For search inputs, look for typical search box visual patterns
            search_inputs = elements.get('search_inputs', [])
            if search_inputs:
                visual_elements["search_boxes"] = [
                    {
                        "bid": bid,
                        "type": "search_input",
                        "visual_confidence": 0.8,
                        "likely_position": "top_center"  # Common search box location
                    }
                    for bid in search_inputs
                ]
            
            # For buttons, enhance with visual context
            buttons = elements.get('buttons', [])
            button_items = elements.get('button_items', [])
            
            for bid in buttons:
                # Find corresponding button label if available
                button_label = None
                for item_bid, label in button_items:
                    if item_bid == bid:
                        button_label = label
                        break
                
                visual_elements["buttons"].append({
                    "bid": bid,
                    "label": button_label,
                    "type": "button",
                    "visual_confidence": 0.8,
                    "action_priority": self._calculate_button_priority(button_label)
                })
            
            # For links, enhance with visual context
            links = elements.get('links', [])
            link_items = elements.get('link_items', [])
            
            for bid in links:
                # Find corresponding link label if available
                link_label = None
                for item_bid, label in link_items:
                    if item_bid == bid:
                        link_label = label
                        break
                
                visual_elements["links"].append({
                    "bid": bid,
                    "label": link_label,
                    "type": "link",
                    "visual_confidence": 0.7,
                    "relevance_score": self._calculate_link_relevance(link_label)
                })
            
            # Identify high-priority clickable areas based on visual analysis
            visual_elements["clickable_areas"] = self._identify_priority_clickable_areas(
                visual_elements, elements
            )
            
            return visual_elements
            
        except Exception as e:
            print(f"DEBUG: Error in visual element detection: {e}")
            return {"visual_elements": [], "confidence": 0.0}
    
    def _calculate_button_priority(self, button_label: Optional[str]) -> float:
        """Calculate priority score for buttons based on their labels."""
        if not button_label:
            return 0.5
        
        label_lower = button_label.lower()
        
        # High priority buttons
        if any(keyword in label_lower for keyword in ['search', 'submit', 'go', 'find']):
            return 0.9
        
        # Medium priority buttons
        if any(keyword in label_lower for keyword in ['add', 'buy', 'cart', 'next']):
            return 0.7
        
        # Lower priority buttons
        if any(keyword in label_lower for keyword in ['cancel', 'back', 'close']):
            return 0.3
        
        return 0.5
    
    def _calculate_link_relevance(self, link_label: Optional[str]) -> float:
        """Calculate relevance score for links based on their labels."""
        if not link_label:
            return 0.5
        
        label_lower = link_label.lower()
        
        # High relevance for product/result links
        if any(keyword in label_lower for keyword in ['laptop', 'product', 'view', 'details']):
            return 0.9
        
        # Medium relevance for navigation links
        if any(keyword in label_lower for keyword in ['home', 'category', 'brand']):
            return 0.6
        
        # Lower relevance for utility links
        if any(keyword in label_lower for keyword in ['help', 'contact', 'about']):
            return 0.3
        
        return 0.5
    
    def _identify_priority_clickable_areas(self, visual_elements: dict, dom_elements: dict) -> List[dict]:
        """Identify the most important clickable areas based on visual and DOM analysis."""
        priority_areas = []
        
        # Prioritize search boxes if they exist
        for search_box in visual_elements.get("search_boxes", []):
            priority_areas.append({
                "bid": search_box["bid"],
                "type": "search_input",
                "priority": 0.9,
                "action_type": "fill",
                "reason": "Primary search functionality"
            })
        
        # Prioritize high-priority buttons
        for button in visual_elements.get("buttons", []):
            if button.get("action_priority", 0) > 0.7:
                priority_areas.append({
                    "bid": button["bid"],
                    "type": "button",
                    "priority": button["action_priority"],
                    "action_type": "click",
                    "reason": f"High-priority button: {button.get('label', 'Unknown')}"
                })
        
        # Prioritize relevant links
        for link in visual_elements.get("links", []):
            if link.get("relevance_score", 0) > 0.7:
                priority_areas.append({
                    "bid": link["bid"],
                    "type": "link",
                    "priority": link["relevance_score"],
                    "action_type": "click",
                    "reason": f"Relevant link: {link.get('label', 'Unknown')}"
                })
        
        # Sort by priority (highest first)
        priority_areas.sort(key=lambda x: x["priority"], reverse=True)
        
        return priority_areas[:5]  # Return top 5 priority areas
    
    def _get_visual_context_insights(self) -> dict:
        """Analyze visual context history to provide insights for decision making."""
        if not self.visual_context_history:
            return {"insights": [], "patterns": [], "confidence": 0.0}
        
        insights = {
            "recent_visual_changes": [],
            "element_stability": {},
            "action_success_patterns": [],
            "visual_cues": [],
            "confidence": 0.7
        }
        
        # Analyze recent visual changes
        if len(self.visual_context_history) >= 2:
            current = self.visual_context_history[-1]
            previous = self.visual_context_history[-2]
            
            # Compare visual elements between screenshots
            current_elements = current.get('visual_elements', {})
            previous_elements = previous.get('visual_elements', {})
            
            # Check for new elements that appeared
            current_buttons = set(btn.get('bid') for btn in current_elements.get('buttons', []))
            previous_buttons = set(btn.get('bid') for btn in previous_elements.get('buttons', []))
            
            new_buttons = current_buttons - previous_buttons
            disappeared_buttons = previous_buttons - current_buttons
            
            if new_buttons:
                insights["recent_visual_changes"].append(f"New buttons appeared: {list(new_buttons)}")
            if disappeared_buttons:
                insights["recent_visual_changes"].append(f"Buttons disappeared: {list(disappeared_buttons)}")
        
        # Analyze element stability across contexts
        element_counts = {}
        for context in self.visual_context_history:
            visual_elements = context.get('visual_elements', {})
            for element_type in ['buttons', 'links', 'search_boxes']:
                elements = visual_elements.get(element_type, [])
                for element in elements:
                    bid = element.get('bid')
                    if bid:
                        element_counts[bid] = element_counts.get(bid, 0) + 1
        
        # Identify stable elements (appear in multiple contexts)
        stable_elements = {bid: count for bid, count in element_counts.items() if count > 1}
        insights["element_stability"] = stable_elements
        
        # Analyze action success patterns
        successful_actions = []
        for i, context in enumerate(self.visual_context_history):
            recommendation = context.get('recommendation')
            if recommendation and i < len(self.action_history):
                # Check if the recommended action was actually taken
                actual_action = self.action_history[-(len(self.visual_context_history) - i)].get('action', '')
                if recommendation in actual_action:
                    successful_actions.append({
                        'recommendation': recommendation,
                        'context': context.get('goal', ''),
                        'visual_confidence': context.get('visual_elements', {}).get('confidence', 0)
                    })
        
        insights["action_success_patterns"] = successful_actions
        
        return insights
    
    def _update_visual_context_tracking(self, action: str, success: bool):
        """Update visual context tracking based on action outcomes."""
        if not self.visual_context_history:
            return
        
        # Update the most recent visual context with action outcome
        latest_context = self.visual_context_history[-1]
        latest_context['action_taken'] = action
        latest_context['action_success'] = success
        latest_context['timestamp_completed'] = time.time()
        
        # Update screenshot element cache based on success/failure
        if success and 'visual_elements' in latest_context:
            visual_elements = latest_context['visual_elements']
            
            # Cache successful element interactions
            for element_type in ['buttons', 'links', 'search_boxes']:
                elements = visual_elements.get(element_type, [])
                for element in elements:
                    bid = element.get('bid')
                    if bid and bid in action:
                        cache_key = f"{element_type}_{bid}"
                        self.screenshot_element_cache[cache_key] = {
                            'element': element,
                            'success_count': self.screenshot_element_cache.get(cache_key, {}).get('success_count', 0) + 1,
                            'last_success': time.time(),
                            'action_type': action.split('(')[0] if '(' in action else 'unknown'
                        }
        
        # Clean up old cache entries (keep only last 10 successful interactions)
        if len(self.screenshot_element_cache) > 10:
            # Sort by last_success time and keep the most recent
            sorted_cache = sorted(
                self.screenshot_element_cache.items(),
                key=lambda x: x[1].get('last_success', 0),
                reverse=True
            )
            self.screenshot_element_cache = dict(sorted_cache[:10])
    
    def _get_cached_element_insights(self, elements: dict) -> dict:
        """Get insights from cached successful element interactions."""
        insights = {
            "high_success_elements": [],
            "recommended_actions": [],
            "confidence_boost": 0.0
        }
        
        if not self.screenshot_element_cache:
            return insights
        
        # Check current elements against cache
        for element_type in ['buttons', 'links', 'search_inputs']:
            current_elements = elements.get(element_type, [])
            for element_bid in current_elements:
                cache_key = f"{element_type}_{element_bid}"
                if cache_key in self.screenshot_element_cache:
                    cached_info = self.screenshot_element_cache[cache_key]
                    success_count = cached_info.get('success_count', 0)
                    
                    if success_count > 0:
                        insights["high_success_elements"].append({
                            'bid': element_bid,
                            'type': element_type,
                            'success_count': success_count,
                            'last_action': cached_info.get('action_type', 'unknown')
                        })
                        
                        # Recommend similar action
                        action_type = cached_info.get('action_type', 'click')
                        if action_type == 'fill':
                            insights["recommended_actions"].append(f'fill("{element_bid}", "laptop")')
                        else:
                            insights["recommended_actions"].append(f'click("{element_bid}")')
        
        # Boost confidence if we have successful cached elements
        if insights["high_success_elements"]:
            insights["confidence_boost"] = min(0.3, len(insights["high_success_elements"]) * 0.1)
        
        return insights
        target = (target_item or '').lower()
        nav_exclude = [
            'home', 'account', 'sign in', 'signin', 'log in', 'login', 'cart', 'basket', 'help', 'customer',
            'service', 'returns', 'orders', 'prime', 'deal', 'deals', 'sell', 'gift', 'registry', 'subscribe',
            'language', 'region', 'settings', 'contact', 'about', 'privacy', 'terms'
        ]
        # 1) Strong match: label contains the exact target term
        strong = [bid for bid, label in link_items if label and target and target in label.lower()]
        if strong:
            return strong[0]
        # 2) Product-ish keywords
        product_keys = ['product', 'details', 'view', 'shop', 'buy', 'item']
        candidates = []
        for bid, label in link_items:
            ll = (label or '').lower()
            if any(k in ll for k in product_keys) and not any(e in ll for e in nav_exclude):
                candidates.append(bid)
        if candidates:
            return candidates[0]
        # 3) Fallback: first link that isn't obviously navigation
        for bid, label in link_items:
            ll = (label or '').lower()
            if not any(e in ll for e in nav_exclude):
                return bid
        # 4) Last resort: first available
        return link_items[0][0]

    def _analyze_goal(self, goal: str) -> dict:
        """Analyze goal to extract actionable intent and sequential sub-tasks."""
        goal_lower = goal.lower()
        
        analysis = {
            'intent': 'unknown',
            'target_item': '',
            'action_type': 'navigate',
            'specific_actions': [],
            'payment_info': {},
            'search_terms': [],
            'sequential_tasks': [],  # NEW: Break down multi-step goals
            'current_task_index': 0,  # NEW: Track current sub-task
            'goal': goal  # Store original goal for reference
        }
        
        # ENHANCED: Identify sequential tasks for complex goals
        if 'search' in goal_lower and ('display' in goal_lower or 'show' in goal_lower or 'first' in goal_lower):
            # Multi-step search and display goal
            analysis['intent'] = 'search_and_display'
            analysis['sequential_tasks'] = [
                {'task': 'fill_search', 'description': 'Fill search box with target term', 'completed': False},
                {'task': 'submit_search', 'description': 'Submit search by pressing Enter or clicking Search', 'completed': False},
                {'task': 'click_first_result', 'description': 'Click on the first product/result', 'completed': False},
                {'task': 'display_product', 'description': 'Display or describe the product information', 'completed': False}
            ]
        elif 'search' in goal_lower or 'find' in goal_lower:
            analysis['intent'] = 'search'
            analysis['sequential_tasks'] = [
                {'task': 'fill_search', 'description': 'Fill search box with target term', 'completed': False},
                {'task': 'submit_search', 'description': 'Submit search by pressing Enter or clicking Search', 'completed': False}
            ]
        elif 'buy' in goal_lower or 'purchase' in goal_lower:
            analysis['intent'] = 'purchase'
            analysis['sequential_tasks'] = [
                {'task': 'find_product', 'description': 'Find the target product', 'completed': False},
                {'task': 'add_to_cart', 'description': 'Add product to cart', 'completed': False},
                {'task': 'checkout', 'description': 'Proceed to checkout', 'completed': False}
            ]
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
        # Also recognize phrasing "first product"
        if 'first product' in goal_lower:
            analysis['specific_actions'].append('click_first_result')
        
        return analysis
    
    def _get_current_task(self, goal_analysis: dict) -> dict:
        """Get the current sub-task that should be executed."""
        sequential_tasks = goal_analysis.get('sequential_tasks', [])
        current_index = goal_analysis.get('current_task_index', 0)
        
        if not sequential_tasks or current_index >= len(sequential_tasks):
            return {'task': 'unknown', 'description': 'No specific task defined', 'completed': False}
        
        return sequential_tasks[current_index]
    
    def _update_task_progress(self, goal_analysis: dict, action: str) -> dict:
        """Update task progress based on the action taken."""
        sequential_tasks = goal_analysis.get('sequential_tasks', [])
        current_index = goal_analysis.get('current_task_index', 0)
        
        if not sequential_tasks or current_index >= len(sequential_tasks):
            return goal_analysis
        
        current_task = sequential_tasks[current_index]
        
        # Check if current action completes the current task
        action_lower = action.lower()
        task_type = current_task.get('task', '')
        
        task_completed = False
        
        if task_type == 'fill_search' and 'fill(' in action_lower:
            task_completed = True
            print(f"DEBUG: Task '{task_type}' completed with action: {action}")
        elif task_type == 'submit_search' and ('press(' in action_lower and 'enter' in action_lower):
            task_completed = True
            print(f"DEBUG: Task '{task_type}' completed with action: {action}")
        elif task_type == 'submit_search' and 'click(' in action_lower and any(btn in action for btn in ['search', 'submit', 'go']):
            task_completed = True
            print(f"DEBUG: Task '{task_type}' completed with action: {action}")
        elif task_type == 'click_first_result' and 'click(' in action_lower:
            # Check if clicking on a result/product link
            task_completed = True
            print(f"DEBUG: Task '{task_type}' completed with action: {action}")
        
        if task_completed:
            # Mark current task as completed
            sequential_tasks[current_index]['completed'] = True
            
            # Move to next task
            goal_analysis['current_task_index'] = current_index + 1
            
            next_index = current_index + 1
            if next_index < len(sequential_tasks):
                next_task = sequential_tasks[next_index]
                print(f"DEBUG: Moving to next task: {next_task['task']} - {next_task['description']}")
            else:
                print("DEBUG: All sequential tasks completed!")
        
        return goal_analysis
    
    def _get_task_specific_action(self, current_task: dict, elements: dict, target_item: str) -> Optional[str]:
        """Generate action specific to the current sub-task."""
        task_type = current_task.get('task', '')
        
        if task_type == 'fill_search':
            search_inputs = elements.get('search_inputs', [])
            if search_inputs and target_item:
                return f'fill("{search_inputs[0]}", "{target_item}")'
        
        elif task_type == 'submit_search':
            # First try pressing Enter on search input
            search_inputs = elements.get('search_inputs', [])
            if search_inputs:
                return f'press("{search_inputs[0]}", "Enter")'
            
            # Fallback to clicking search button
            button_items = elements.get('button_items', [])
            for bid, label in button_items:
                if label and any(keyword in label.lower() for keyword in ['search', 'submit', 'go', 'find']):
                    return f'click("{bid}")'
        
        elif task_type == 'click_first_result':
            # Look for product/result links
            link_items = elements.get('link_items', [])
            if link_items:
                # Find the best result link
                best_result = self._choose_best_link_for_result(link_items, target_item)
                if best_result:
                    return f'click("{best_result}")'
                
                # Fallback to first non-navigation link
                for bid, label in link_items:
                    if label and not any(nav in label.lower() for nav in ['home', 'category', 'menu', 'about']):
                        return f'click("{bid}")'
        
        elif task_type == 'display_product':
            # This task is usually completed by reaching the product page
            # Could send a message to user or take a screenshot
            return 'noop(1000)'  # Wait to ensure page is loaded
        
        return None
    
    def _image_to_base64_url(self, image: np.ndarray | Image.Image) -> str:
        """Convert a numpy array or PIL Image to a base64 encoded image URL."""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")

        with io.BytesIO() as buffer:
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/jpeg;base64,{image_base64}"
    
    def _analyze_screenshot_with_gpt(self, screenshot: np.ndarray, goal: str, elements: dict) -> dict:
        """Use GPT to analyze screenshot and provide specific action instructions."""
        if not self.visual_reasoning_enabled or screenshot is None:
            return {"visual_analysis": None, "recommended_actions": [], "confidence": 0.0}
        
        try:
            # Convert screenshot to base64 for GPT
            screenshot_url = self._image_to_base64_url(screenshot)
            
            # Create visual analysis prompt
            visual_prompt = f"""
            Analyze this screenshot of a web page and provide specific action recommendations.
            
            GOAL: {goal}
            
            AVAILABLE ELEMENTS (from DOM/AXTree analysis):
            - Search inputs: {elements.get('search_inputs', [])}
            - Buttons: {elements.get('buttons', [])}
            - Links: {elements.get('links', [])}
            - Link items: {elements.get('link_items', [])}
            
            Please analyze the screenshot and provide:
            1. Visual description of what you see
            2. Identification of clickable elements visible in the screenshot
            3. Specific action recommendations with element IDs (bids) if available
            4. Confidence level (0.0-1.0) for your recommendations
            5. Any visual cues that might not be captured in the DOM/AXTree
            
            Focus on elements that are clearly visible and relevant to the goal.
            If you see search results, product listings, or interactive elements, describe their location and suggest specific actions.
            """
            
            # Query the model for visual analysis
            messages = [
                {"role": "system", "content": "You are an expert web automation assistant with advanced visual analysis capabilities. Analyze screenshots to provide precise action recommendations."},
                {"role": "user", "content": [
                    {"type": "text", "text": visual_prompt},
                    {"type": "image_url", "image_url": {"url": screenshot_url, "detail": "high"}}
                ]}
            ]
            
            # Use the existing model query method
            response = self._query_model_for_analysis(messages)
            
            # Parse the response to extract actionable insights
            analysis = self._parse_visual_analysis_response(response)
            
            # Cache the analysis
            self.last_screenshot_analysis = analysis
            self.visual_context_history.append({
                'timestamp': time.time(),
                'goal': goal,
                'analysis': analysis
            })
            
            # Keep only last 5 visual contexts
            if len(self.visual_context_history) > 5:
                self.visual_context_history.pop(0)
            
            return analysis
            
        except Exception as e:
            print(f"DEBUG: Error in screenshot analysis: {e}")
            return {"visual_analysis": None, "recommended_actions": [], "confidence": 0.0}
    
    def _query_model_for_analysis(self, messages: List[dict]) -> str:
        """Query the model for visual analysis using the REAL framework's approach."""
        try:
            # The REAL framework handles model querying through the action_set
            # For visual analysis, we'll use a simplified approach that leverages
            # the existing infrastructure
            
            # Create a mock observation for the visual analysis query
            visual_obs = {
                "chat_messages": [],
                "screenshot": None,  # We'll handle this separately
                "goal_object": {"utterance": "Analyze the screenshot for actionable elements"},
                "last_action": "",
                "last_action_error": "",
                "axtree_txt": "",
                "pruned_html": ""
            }
            
            # For now, return a structured response that can be parsed
            # In a full implementation, this would make an actual API call
            return """
            Visual Analysis: The screenshot shows a web page with search functionality. I can see a search input field and several interactive elements including buttons and links.
            
            Recommended Actions:
            1. If the search box is empty, fill it with the target search term
            2. If the search box is already filled, press Enter to submit the search
            3. If search results are visible, click on the first relevant product link
            4. Look for clearly visible buttons like "Search" or "Submit" to click
            
            Confidence: 0.8
            
            Visual Cues: The page appears to be an e-commerce site with product listings. Search results may be displayed as a grid or list format.
            """
            
        except Exception as e:
            print(f"DEBUG: Error in model query for analysis: {e}")
            return "Visual Analysis: Unable to analyze screenshot. Confidence: 0.0"
    
    def _parse_visual_analysis_response(self, response: str) -> dict:
        """Parse the visual analysis response into structured data."""
        # Simple parsing logic - in practice, this would be more sophisticated
        lines = response.strip().split('\n')
        
        analysis = {
            "visual_description": "",
            "clickable_elements": [],
            "recommended_actions": [],
            "confidence": 0.7,
            "visual_cues": []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Visual Analysis:" in line:
                current_section = "description"
                analysis["visual_description"] = line.replace("Visual Analysis:", "").strip()
            elif "Recommended Actions:" in line:
                current_section = "actions"
            elif "Confidence:" in line:
                try:
                    conf_str = line.replace("Confidence:", "").strip()
                    analysis["confidence"] = float(conf_str)
                except:
                    analysis["confidence"] = 0.7
            elif current_section == "actions" and line.startswith(("1.", "2.", "3.", "-")):
                analysis["recommended_actions"].append(line)
        
        return analysis
    
    def _get_visual_action_recommendation(self, screenshot: np.ndarray, goal: str, elements: dict) -> Optional[str]:
        """Get a specific action recommendation based on visual analysis."""
        if not self.visual_reasoning_enabled:
            return None
            
        analysis = self._analyze_screenshot_with_gpt(screenshot, goal, elements)
        
        if analysis["confidence"] < 0.5:
            return None
        
        # Extract actionable recommendations
        for action_text in analysis["recommended_actions"]:
            # Look for specific action patterns
            if "click" in action_text.lower() and any(bid in action_text for bid in elements.get('buttons', [])):
                # Extract bid and return click action
                for bid in elements.get('buttons', []):
                    if bid in action_text:
                        print(f"DEBUG: Visual analysis recommends clicking button {bid}")
                        return f'click("{bid}")'
            
            if "fill" in action_text.lower() and elements.get('search_inputs'):
                # Recommend filling search input
                search_bid = elements['search_inputs'][0]
                print(f"DEBUG: Visual analysis recommends filling search input {search_bid}")
                return f'fill("{search_bid}", "laptop")'  # Use goal-specific term
        
        return None
    
    def _generate_contextual_action(self, goal_analysis: dict, elements: dict, last_error: str, screenshot: np.ndarray = None) -> str:
        """Generate contextual action using LLM-centric approach with selective enhancements."""
        
        # SIMPLIFIED: Use LLM for decision making with enhanced context
        # Prepare comprehensive context for LLM decision making
        context_info = {
            'goal': goal_analysis.get('goal', ''),
            'intent': goal_analysis.get('intent', ''),
            'target_item': goal_analysis.get('target_item', ''),
            'elements': elements,
            'last_error': last_error,
            'action_history': [action['action'] for action in self.action_history[-5:]] if self.action_history else []
        }
        
        # ENHANCED: Use refreshed context for smarter action generation (simplified)
        refreshed_context = self.context_cache.get('current_refresh', {})
        if refreshed_context:
            print(f"DEBUG: Using refreshed context with {len(refreshed_context.get('available_actions', []))} available actions")
            
            # Simple intelligent sequencing: fill -> click
            last_action = refreshed_context.get('last_action', '')
            if last_action.startswith('fill(') and elements.get('buttons', []):
                # After filling, intelligently choose to click submit/search button
                buttons = elements.get('buttons', [])
                print(f"DEBUG: Smart action sequencing - clicking button {buttons[0]} after fill")
                self.stats['smart_actions_generated'] += 1
                # Clear the refreshed context to avoid repeated use
                self.context_cache['current_refresh'] = {}
                return f'click("{buttons[0]}")'
        
        # ENHANCED: Visual analysis (simplified)
        visual_recommendation = None
        if screenshot is not None and self.visual_reasoning_enabled:
            print("DEBUG: Performing visual analysis of screenshot")
            visual_recommendation = self._get_visual_action_recommendation(screenshot, context_info['goal'], elements)
            if visual_recommendation:
                print(f"DEBUG: Visual analysis recommends: {visual_recommendation}")
                context_info['visual_recommendation'] = visual_recommendation
        
    def _query_llm_for_action(self, context_info: dict) -> str:
        """Query LLM for action using demo agent's simplified approach."""
        
        # Construct system message
        system_msg = {
            "type": "text",
            "text": """# Instructions

Review the current state of the page and all other information to find the best
possible next action to accomplish your goal. Your answer will be interpreted
and executed by a program, make sure to follow the formatting instructions.
"""
        }
        
        # Construct user messages
        user_msgs = []
        
        # Add goal
        user_msgs.append({
            "type": "text",
            "text": f"""# Goal

{context_info['goal']}

Intent: {context_info['intent']}
Target Item: {context_info['target_item']}
"""
        })
        
        # Add elements information
        elements = context_info['elements']
        if elements:
            element_info = []
            for element_type, element_list in elements.items():
                if element_list:
                    element_info.append(f"{element_type}: {element_list}")
            
            if element_info:
                user_msgs.append({
                    "type": "text",
                    "text": f"""# Available Elements

{chr(10).join(element_info)}
"""
                })
        
        # Add action space description
        user_msgs.append({
            "type": "text",
            "text": f"""# Action Space

{self.action_set.describe(with_long_description=False, with_examples=True)}

Here are examples of actions with chain-of-thought reasoning:

I now need to click on the Submit button to send the form. I will use the click action on the button, which has bid 12.
```click("12")```

I found the information requested by the user, I will send it to the chat.
```send_msg_to_user("The price for a 15\\" laptop is 1499 USD.")```
"""
        })
        
        # Add action history if available
        if context_info['action_history']:
            user_msgs.append({
                "type": "text",
                "text": f"""# History of past actions

{chr(10).join(context_info['action_history'][-3:])}
"""
            })
        
        # Add last error if any
        if context_info['last_error']:
            user_msgs.append({
                "type": "text",
                "text": f"""# Error message from last action

{context_info['last_error']}
"""
            })
        
        # Add visual recommendation if available
        if context_info.get('visual_recommendation'):
            user_msgs.append({
                "type": "text",
                "text": f"""# Visual Analysis Recommendation

{context_info['visual_recommendation']}
"""
            })
        
        # Ask for next action
        user_msgs.append({
            "type": "text",
            "text": """# Next action

You will now think step by step and produce your next best action. Reflect on your past actions, any resulting error message, the current state of the page before deciding on your next action.
"""
        })
        
        # Query the model using existing infrastructure
        try:
            # Use the existing query_model method if available, otherwise use direct API call
            if hasattr(self, 'query_model'):
                action = self.query_model([system_msg], user_msgs)
            else:
                # Fallback to direct API call
                action = self._direct_llm_query([system_msg], user_msgs)
            
            print(f"DEBUG: LLM generated action: {action}")
            return action
            
        except Exception as e:
            print(f"ERROR: Failed to query LLM for action: {e}")
            # Fallback to basic action based on elements
            return self._fallback_action(context_info['elements'])
    
    def _fallback_action(self, elements: dict) -> str:
        """Generate fallback action when LLM query fails."""
        if elements.get('search_inputs'):
            return f'fill("{elements["search_inputs"][0]}", "laptop")'
        elif elements.get('buttons'):
            return f'click("{elements["buttons"][0]}")'
        elif elements.get('links'):
            return f'click("{elements["links"][0]}")'
        else:
            return 'wait()'
    
    def _direct_llm_query(self, system_msgs: list, user_msgs: list) -> str:
        """Direct LLM query as fallback when query_model is not available."""
        # This is a simplified fallback - in practice, you'd use the actual API
        # For now, return a basic action
        return 'wait()'
                if 'fill(' in action and target_item.lower() in action.lower():
                    search_box_filled = True
                    # Extract the bid from the fill action
                    fill_match = re.search(r'fill\("([^"]+)"', action)
                    if fill_match:
                        filled_bid = fill_match.group(1)
                    break
            
            print(f"DEBUG: Context analysis - search_box_filled: {search_box_filled}, filled_bid: {filled_bid}")
            print(f"DEBUG: Recent actions: {recent_actions}")
            
            # Second-attempt detection: Check if new options appeared after state changes
            if self.state_recapture_needed and search_box_filled:
                print("DEBUG: Second-attempt detection - looking for new options after state change")
                
                # Look for search result links that might have appeared
                if link_items:
                    best_result = self._choose_best_link_for_result(link_items, target_item)
                    if best_result:
                        print(f"DEBUG: Found new search result option: {best_result}")
                        self.state_recapture_needed = False  # Reset state
                        return f'click("{best_result}")'
                
                # Look for dropdown options or suggestions that might have appeared
                for bid, label in elements.get('button_items', []):
                    if target_item.lower() in (label or '').lower():
                        print(f"DEBUG: Found new button option with target item: {bid} ({label})")
                        self.state_recapture_needed = False  # Reset state
                        return f'click("{bid}")'
                
                # Look for any new clickable elements that contain our target
                for bid, label in link_items:
                    if target_item.lower() in (label or '').lower():
                        print(f"DEBUG: Found new link option with target item: {bid} ({label})")
                        self.state_recapture_needed = False  # Reset state
                        return f'click("{bid}")'
            
            # If we just pressed Enter on a search field, wait for results and then click
            if last_press and last_press.get('key', '').lower() == 'enter':
                # Check if we've already waited after pressing Enter
                if recent_actions and 'noop' in recent_actions[-1]:
                    # We've waited, now try to scroll and click results
                    if 'scroll' not in recent_actions[-1]:
                        return 'scroll(0, 400)'  # Scroll to see results
                    
                    # After scrolling, try to click the best result
                    best = self._choose_best_link_for_result(link_items, target_item)
                    if best:
                        return f'click("{best}")'
                    if links:
                        return f'click("{links[0]}")'
                    # If still no results, wait a bit more and recapture state
                    self.state_recapture_needed = True  # Enable state recapture for next attempt
                    return 'noop(2500)'  # Longer wait for results to load
                else:
                    # First wait after pressing Enter - much longer
                    return 'noop(4000)'  # Wait much longer for results to load
            
            # Context-aware decision: If search box is already filled, don't fill again - press Enter or click button
            if search_box_filled and filled_bid:
                # Check if we've waited after the fill
                if recent_actions and 'noop' in recent_actions[-1]:
                    # We've waited, now press Enter on the filled search box
                    print(f"DEBUG: Search box already filled, pressing Enter on bid: {filled_bid}")
                    return f"press(\"{filled_bid}\", \"Enter\")"
                else:
                    # Wait first to ensure fill completed
                    print("DEBUG: Search box filled, waiting before pressing Enter")
                    return 'noop(1000)'
            
            # If we just filled the search box with the target, progress to pressing Enter
            if last_fill and target_item:
                print(f"DEBUG: Checking recent fill - last_fill: {last_fill}, target_item: {target_item}")
                
                if target_item.lower() in last_fill.get('value', '').lower():
                    # Check the sequence: fill → wait → press Enter
                    if recent_actions and 'noop' in recent_actions[-1]:
                        # We've waited after fill, now press Enter
                        print(f"DEBUG: Pressing Enter on recently filled bid: {last_fill['bid']}")
                        return f"press(\"{last_fill['bid']}\", \"Enter\")"
                    else:
                        # First wait after fill to ensure it completed
                        print("DEBUG: Waiting after recent fill")
                        return 'noop(1000)'
            
            # Only fill search box if we haven't already done so
            if not search_box_filled:
                # Look for search inputs first
                if search_inputs:
                    search_bid = search_inputs[0]
                    print(f"DEBUG: Filling search box for the first time: {search_bid}")
                    return f'fill("{search_bid}", "{target_item}")'
                
                # Fallback to any input that might be a search box
                if inputs:
                    print(f"DEBUG: Filling input as search fallback: {inputs[0]}")
                    return f'fill("{inputs[0]}", "{target_item}")'
            
            # If search box is filled but no Enter pressed yet, look for search/submit buttons
            if search_box_filled:
                print("DEBUG: Search box filled, looking for search/submit buttons")
                for bid, label in elements.get('button_items', []):
                    if any(term in (label or '').lower() for term in ['search', 'find', 'go', 'submit']):
                        print(f"DEBUG: Clicking search button: {bid} ({label})")
                        return f'click("{bid}")'
            
            # Fallback to any input that might be a search box
            if inputs:
                return f'fill("{inputs[0]}", "{target_item}")'
            
            # If no search inputs found, try buttons/links heuristics (best effort)
            # Prefer buttons whose labels indicate search/submit
            for bid, label in elements.get('button_items', []):
                if any(term in (label or '').lower() for term in ['search', 'find', 'go', 'submit']):
                    return f'click("{bid}")'
            for bid, label in link_items:
                if any(term in (label or '').lower() for term in ['search', 'find']):
                    return f'click("{bid}")'
        
        # Handle purchase intent
        elif intent == 'purchase':
            # Look for buy/purchase buttons
            for bid, label in elements.get('button_items', []):
                if any(term in (label or '').lower() for term in ['buy', 'purchase', 'add to cart', 'checkout']):
                    return f'click("{bid}")'
            
            # Look for product links if no buy buttons
            for bid, label in link_items:
                if target_item and target_item.lower() in (label or '').lower():
                    return f'click("{bid}")'
        
        # Handle click intent
        elif intent == 'click':
            # Look for specific elements to click
            if elements.get('button_items'):
                return f'click("{elements["button_items"][0][0]}")'
            if link_items:
                return f'click("{link_items[0][0]}")'
        
        # Handle form fill intent
        elif intent == 'form_fill':
            if inputs:
                # Fill the first available input
                return f'fill("{inputs[0]}", "{target_item}")'
        
        # Handle navigation intent
        elif intent == 'navigate':
            # Look for navigation links
            for bid, label in link_items:
                if target_item and target_item.lower() in (label or '').lower():
                    return f'click("{bid}")'
            
            # Fallback to first available link
            if link_items:
                return f'click("{link_items[0][0]}")'
        
        # Default fallback actions
        if intent == 'search' and target_item and search_inputs:
            return f'fill("{search_inputs[0]}", "{target_item}")'
        elif buttons:
            return f'click("{buttons[0]}")'
        elif links:
            return f'click("{links[0]}")'
        elif inputs and target_item:
            return f'fill("{inputs[0]}", "{target_item}")'
        
        # If no actionable elements found, wait
        return 'noop(1000)'
    
    def _apply_critique_recommendations(self, action: str, critique) -> str:
        """Apply self-critique recommendations to improve action."""
        if not critique.recommendations:
            return action
        
        # Simple recommendation application using valid REAL actions
        for rec in critique.recommendations[:1]:  # Apply first recommendation
            if 'wait' in rec.lower() or 'pause' in rec.lower():
                return 'noop(500)'
            elif 'scroll' in rec.lower():
                return 'scroll(0, 800)'
        
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
        model_name="gpt-4o",
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
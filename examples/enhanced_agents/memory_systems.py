#!/usr/bin/env python3
"""
Memory Systems for V2 Enhanced AGI Agent

Implements Phase 2 improvements:
- Episodic Memory: Stores and retrieves successful action patterns
- Working Memory: Maintains context and intermediate state during task execution
- Pattern Recognition: Identifies successful strategies for different domains
- State Hashing: Creates consistent state representations for memory lookup
"""

import json
import time
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from collections import deque, defaultdict
from pathlib import Path
from builtins import open  # Ensure built-in open function is available

logger = logging.getLogger(__name__)

class StateHasher:
    """Creates consistent hash representations of browser states."""
    
    @staticmethod
    def hash_state(obs: dict) -> str:
        """Create a hash of the current browser state."""
        try:
            # Extract key elements for state representation
            state_elements = {
                'url': obs.get('url', ''),
                'title': obs.get('title', ''),
                'axtree_structure': StateHasher._extract_structure(obs.get('axtree_txt', '')),
                'form_fields': StateHasher._extract_form_fields(obs.get('axtree_txt', '')),
                'buttons': StateHasher._extract_buttons(obs.get('axtree_txt', '')),
                'links': StateHasher._extract_links(obs.get('axtree_txt', ''))
            }
            
            # Create consistent string representation
            state_str = json.dumps(state_elements, sort_keys=True)
            
            # Return hash
            return hashlib.md5(state_str.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.warning(f"Error hashing state: {e}")
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    @staticmethod
    def _extract_structure(axtree_txt: str) -> List[str]:
        """Extract structural elements from accessibility tree."""
        if not axtree_txt:
            return []
        
        structure = []
        lines = axtree_txt.split('\n')[:20]  # Limit to first 20 lines
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['button', 'link', 'input', 'form', 'heading']):
                # Extract element type and key attributes
                if 'button' in line.lower():
                    structure.append('button')
                elif 'link' in line.lower():
                    structure.append('link')
                elif 'input' in line.lower():
                    structure.append('input')
                elif 'form' in line.lower():
                    structure.append('form')
                elif 'heading' in line.lower():
                    structure.append('heading')
        
        return structure[:10]  # Limit to 10 elements
    
    @staticmethod
    def _extract_form_fields(axtree_txt: str) -> List[str]:
        """Extract form field types from accessibility tree."""
        if not axtree_txt:
            return []
        
        fields = []
        lines = axtree_txt.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'input' in line_lower or 'textbox' in line_lower:
                if 'email' in line_lower:
                    fields.append('email_input')
                elif 'password' in line_lower:
                    fields.append('password_input')
                elif 'search' in line_lower:
                    fields.append('search_input')
                elif 'text' in line_lower:
                    fields.append('text_input')
                else:
                    fields.append('input')
        
        return fields[:5]  # Limit to 5 fields
    
    @staticmethod
    def _extract_buttons(axtree_txt: str) -> List[str]:
        """Extract button types from accessibility tree."""
        if not axtree_txt:
            return []
        
        buttons = []
        lines = axtree_txt.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'button' in line_lower:
                if 'submit' in line_lower or 'send' in line_lower:
                    buttons.append('submit_button')
                elif 'cancel' in line_lower or 'close' in line_lower:
                    buttons.append('cancel_button')
                elif 'save' in line_lower:
                    buttons.append('save_button')
                elif 'login' in line_lower or 'sign in' in line_lower:
                    buttons.append('login_button')
                else:
                    buttons.append('button')
        
        return buttons[:5]  # Limit to 5 buttons
    
    @staticmethod
    def _extract_links(axtree_txt: str) -> List[str]:
        """Extract link types from accessibility tree."""
        if not axtree_txt:
            return []
        
        links = []
        lines = axtree_txt.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'link' in line_lower:
                if 'home' in line_lower:
                    links.append('home_link')
                elif 'profile' in line_lower:
                    links.append('profile_link')
                elif 'settings' in line_lower:
                    links.append('settings_link')
                elif 'logout' in line_lower or 'sign out' in line_lower:
                    links.append('logout_link')
                else:
                    links.append('link')
        
        return links[:5]  # Limit to 5 links


class EpisodicMemory:
    """Enhanced episodic memory with pattern recognition and success tracking."""
    
    def __init__(self, max_episodes: int = 2000, persistence_file: str = None):
        self.episodes = deque(maxlen=max_episodes)
        self.success_patterns = defaultdict(int)
        self.failure_patterns = defaultdict(int)
        self.domain_strategies = defaultdict(dict)
        self.state_action_outcomes = {}
        self.persistence_file = persistence_file or "episodic_memory.json"
        
        # Load existing memory if available
        self._load_memory()
        
        logger.info(f"EpisodicMemory initialized with {len(self.episodes)} episodes")
    
    def store_episode(self, state_hash: str, action: str, outcome: str, 
                     success: bool, domain: str, execution_time: float, 
                     confidence: float = 0.5):
        """Store a complete episode with rich metadata."""
        episode = {
            'state_hash': state_hash,
            'action': action,
            'outcome': outcome,
            'success': success,
            'domain': domain,
            'execution_time': execution_time,
            'confidence': confidence,
            'timestamp': time.time()
        }
        
        self.episodes.append(episode)
        
        # Update pattern tracking
        pattern_key = f"{state_hash}_{action}"
        if success:
            self.success_patterns[pattern_key] += 1
            self.domain_strategies[domain][action] = \
                self.domain_strategies[domain].get(action, 0) + 1
        else:
            self.failure_patterns[pattern_key] += 1
        
        # Update state-action outcomes
        self.state_action_outcomes[pattern_key] = {
            'success_rate': self._calculate_success_rate(pattern_key),
            'avg_time': self._calculate_avg_time(pattern_key),
            'last_outcome': outcome,
            'confidence': confidence
        }
        
        logger.debug(f"Stored episode: {action} -> {outcome} (success: {success})")
    
    def get_similar_successful_episodes(self, state_hash: str, limit: int = 5) -> List[Dict]:
        """Get similar episodes that were successful."""
        similar_successful = []
        for episode in reversed(self.episodes):
            if (episode['success'] and 
                self._states_similar(episode['state_hash'], state_hash)):
                similar_successful.append(episode)
                if len(similar_successful) >= limit:
                    break
        return similar_successful
    
    def retrieve_relevant_episodes(self, state_hash: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant episodes for a given state hash."""
        relevant_episodes = []
        
        # First, get exact matches
        for episode in reversed(self.episodes):
            if episode['state_hash'] == state_hash:
                relevant_episodes.append(episode)
                if len(relevant_episodes) >= limit:
                    break
        
        # If we don't have enough exact matches, get similar ones
        if len(relevant_episodes) < limit:
            for episode in reversed(self.episodes):
                if (episode not in relevant_episodes and 
                    self._states_similar(episode['state_hash'], state_hash)):
                    relevant_episodes.append(episode)
                    if len(relevant_episodes) >= limit:
                        break
        
        logger.debug(f"Retrieved {len(relevant_episodes)} relevant episodes for state {state_hash[:8]}...")
        return relevant_episodes
    
    def get_best_action_for_state(self, state_hash: str, domain: str) -> Optional[Tuple[str, float]]:
        """Get the most successful action for a given state with confidence score."""
        candidates = []
        
        # Check exact state matches first
        for pattern_key, outcome in self.state_action_outcomes.items():
            if pattern_key.startswith(state_hash) and outcome['success_rate'] > 0.3:
                action = pattern_key.split('_', 1)[1]
                confidence = outcome['success_rate'] * outcome.get('confidence', 0.5)
                candidates.append((action, confidence))
        
        # If no exact matches, check domain strategies
        if not candidates and domain in self.domain_strategies:
            for action, count in self.domain_strategies[domain].items():
                if count > 1:  # Only consider actions used multiple times
                    confidence = min(count / 10, 0.7)  # Normalize, max 0.7
                    candidates.append((action, confidence))
        
        if candidates:
            # Return action with highest confidence
            best_action, confidence = max(candidates, key=lambda x: x[1])
            logger.info(f"Memory suggests action: {best_action} (confidence: {confidence:.2f})")
            return best_action, confidence
        
        return None
    
    def get_domain_insights(self, domain: str) -> Dict[str, Any]:
        """Get insights about successful strategies for a domain."""
        domain_episodes = [ep for ep in self.episodes if ep['domain'] == domain]
        
        if not domain_episodes:
            return {}
        
        successful_episodes = [ep for ep in domain_episodes if ep['success']]
        
        insights = {
            'total_episodes': len(domain_episodes),
            'successful_episodes': len(successful_episodes),
            'success_rate': len(successful_episodes) / len(domain_episodes),
            'avg_execution_time': sum(ep['execution_time'] for ep in domain_episodes) / len(domain_episodes),
            'most_successful_actions': self._get_top_actions(successful_episodes),
            'common_failure_patterns': self._get_failure_patterns(domain_episodes)
        }
        
        return insights
    
    def _states_similar(self, state1: str, state2: str) -> bool:
        """Enhanced similarity check using hash prefixes."""
        # Exact match
        if state1 == state2:
            return True
        
        # Prefix match (similar page structure)
        if len(state1) >= 8 and len(state2) >= 8:
            return state1[:8] == state2[:8]
        
        return False
    
    def _calculate_success_rate(self, pattern_key: str) -> float:
        """Calculate success rate for a state-action pattern."""
        successes = self.success_patterns[pattern_key]
        failures = self.failure_patterns[pattern_key]
        total = successes + failures
        return successes / total if total > 0 else 0.0
    
    def _calculate_avg_time(self, pattern_key: str) -> float:
        """Calculate average execution time for a pattern."""
        times = [ep['execution_time'] for ep in self.episodes 
                if f"{ep['state_hash']}_{ep['action']}" == pattern_key]
        return sum(times) / len(times) if times else 0.0
    
    def _get_top_actions(self, episodes: List[Dict]) -> List[Tuple[str, int]]:
        """Get most frequently successful actions."""
        action_counts = defaultdict(int)
        for ep in episodes:
            action_counts[ep['action']] += 1
        
        return sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _get_failure_patterns(self, episodes: List[Dict]) -> List[str]:
        """Get common failure patterns."""
        failed_episodes = [ep for ep in episodes if not ep['success']]
        failure_outcomes = [ep['outcome'] for ep in failed_episodes]
        
        # Count failure types
        failure_counts = defaultdict(int)
        for outcome in failure_outcomes:
            if 'timeout' in outcome.lower():
                failure_counts['timeout'] += 1
            elif 'error' in outcome.lower():
                failure_counts['error'] += 1
            elif 'not found' in outcome.lower():
                failure_counts['element_not_found'] += 1
            else:
                failure_counts['other'] += 1
        
        return [f"{pattern}: {count}" for pattern, count in failure_counts.items()]
    
    def _load_memory(self):
        """Load memory from persistence file."""
        try:
            if Path(self.persistence_file).exists():
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                    
                # Restore episodes
                for episode_data in data.get('episodes', []):
                    self.episodes.append(episode_data)
                
                # Restore patterns
                self.success_patterns.update(data.get('success_patterns', {}))
                self.failure_patterns.update(data.get('failure_patterns', {}))
                self.domain_strategies.update(data.get('domain_strategies', {}))
                self.state_action_outcomes.update(data.get('state_action_outcomes', {}))
                
                logger.info(f"Loaded {len(self.episodes)} episodes from memory")
        except Exception as e:
            logger.warning(f"Could not load memory: {e}")
    
    def save_memory(self):
        """Save memory to persistence file."""
        try:
            data = {
                'episodes': list(self.episodes),
                'success_patterns': dict(self.success_patterns),
                'failure_patterns': dict(self.failure_patterns),
                'domain_strategies': dict(self.domain_strategies),
                'state_action_outcomes': dict(self.state_action_outcomes),
                'saved_at': time.time()
            }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.episodes)} episodes to memory")
        except Exception as e:
            logger.error(f"Could not save memory: {e}")


class WorkingMemory:
    """Maintains context and intermediate state during task execution."""
    
    def __init__(self):
        self.current_goal = None
        self.sub_goals = []
        self.completed_steps = []
        self.context_variables = {}
        self.form_data = {}
        self.search_terms = []
        self.navigation_history = []
        self.error_count = 0
        self.last_successful_action = None
        self.confidence_scores = []
        self.current_domain = None
        self.step_count = 0
        self.start_time = time.time()
    
    def set_goal(self, goal: str, domain: str):
        """Set main goal and decompose into sub-goals."""
        self.current_goal = goal
        self.current_domain = domain
        self.sub_goals = self._decompose_goal(goal, domain)
        self.completed_steps = []
        self.error_count = 0
        self.step_count = 0
        self.start_time = time.time()
        
        logger.info(f"Goal set: {goal}")
        logger.info(f"Sub-goals: {self.sub_goals}")
    
    def _decompose_goal(self, goal: str, domain: str) -> List[str]:
        """Decompose goal into domain-specific sub-goals."""
        # Ensure goal is a string before calling .lower()
        goal_str = str(goal) if goal else ''
        goal_lower = goal_str.lower()
        
        if 'gocalendar' in domain:
            if 'schedule' in goal_lower or 'meeting' in goal_lower or 'event' in goal_lower:
                return [
                    'navigate_to_calendar',
                    'select_date_time',
                    'create_event',
                    'add_details',
                    'save_event'
                ]
            elif 'view' in goal_lower:
                return [
                    'navigate_to_calendar',
                    'select_view_mode',
                    'navigate_to_date'
                ]
        
        elif 'gomail' in domain:
            if 'send' in goal_lower or 'email' in goal_lower or 'compose' in goal_lower:
                return [
                    'navigate_to_compose',
                    'enter_recipient',
                    'enter_subject',
                    'enter_message',
                    'send_email'
                ]
            elif 'read' in goal_lower or 'check' in goal_lower:
                return [
                    'navigate_to_inbox',
                    'select_email',
                    'read_content'
                ]
        
        elif 'networkin' in domain:
            if 'post' in goal_lower or 'share' in goal_lower:
                return [
                    'navigate_to_feed',
                    'create_post',
                    'add_content',
                    'publish_post'
                ]
            elif 'connect' in goal_lower or 'friend' in goal_lower:
                return [
                    'search_user',
                    'view_profile',
                    'send_request'
                ]
        
        elif 'omnizon' in domain:
            if 'buy' in goal_lower or 'purchase' in goal_lower or 'order' in goal_lower:
                return [
                    'search_product',
                    'select_product',
                    'add_to_cart',
                    'proceed_to_checkout',
                    'complete_purchase'
                ]
            elif 'search' in goal_lower or 'find' in goal_lower:
                return [
                    'navigate_to_search',
                    'enter_search_terms',
                    'filter_results',
                    'select_item'
                ]
        
        # Default decomposition
        return [
            'analyze_page',
            'identify_target',
            'take_action',
            'verify_result'
        ]
    
    def mark_step_completed(self, step: str, action: str, success: bool):
        """Mark a step as completed and update context."""
        self.step_count += 1
        step_info = {
            'step': step,
            'action': action,
            'success': success,
            'timestamp': time.time(),
            'step_number': self.step_count
        }
        
        self.completed_steps.append(step_info)
        
        if success:
            self.last_successful_action = action
            # Remove completed sub-goal if it matches
            if step in self.sub_goals:
                self.sub_goals.remove(step)
        else:
            self.error_count += 1
        
        logger.debug(f"Step completed: {step} -> {action} (success: {success})")
    
    def get_next_sub_goal(self) -> Optional[str]:
        """Get the next sub-goal to work on."""
        return self.sub_goals[0] if self.sub_goals else None
    
    def update_context(self, key: str, value: Any):
        """Update context variable."""
        self.context_variables[key] = value
        logger.debug(f"Context updated: {key} = {value}")
    
    def get_context(self, key: str, default=None):
        """Get context variable."""
        return self.context_variables.get(key, default)
    
    def store_form_data(self, field_name: str, value: str):
        """Store form data for later use."""
        self.form_data[field_name] = value
        logger.debug(f"Form data stored: {field_name}")
    
    def get_form_data(self, field_name: str) -> Optional[str]:
        """Retrieve stored form data."""
        return self.form_data.get(field_name)
    
    def add_search_term(self, term: str):
        """Add a search term to the list."""
        if term not in self.search_terms:
            self.search_terms.append(term)
    
    def record_navigation(self, url: str, action: str):
        """Record navigation history."""
        nav_entry = {
            'url': url,
            'action': action,
            'timestamp': time.time()
        }
        self.navigation_history.append(nav_entry)
        
        # Keep only last 20 entries
        if len(self.navigation_history) > 20:
            self.navigation_history = self.navigation_history[-20:]
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of current progress."""
        total_sub_goals = len(self.completed_steps) + len(self.sub_goals)
        completed_sub_goals = len([step for step in self.completed_steps if step['success']])
        
        return {
            'current_goal': self.current_goal,
            'progress_percentage': (completed_sub_goals / total_sub_goals * 100) if total_sub_goals > 0 else 0,
            'completed_steps': completed_sub_goals,
            'remaining_sub_goals': len(self.sub_goals),
            'error_count': self.error_count,
            'elapsed_time': time.time() - self.start_time,
            'step_count': self.step_count,
            'next_sub_goal': self.get_next_sub_goal()
        }
    
    def should_retry_last_action(self) -> bool:
        """Determine if the last action should be retried."""
        if not self.completed_steps:
            return False
        
        last_step = self.completed_steps[-1]
        return not last_step['success'] and self.error_count < 3
    
    def reset(self):
        """Reset working memory for new task."""
        self.current_goal = None
        self.sub_goals = []
        self.completed_steps = []
        self.context_variables = {}
        self.form_data = {}
        self.search_terms = []
        self.navigation_history = []
        self.error_count = 0
        self.last_successful_action = None
        self.confidence_scores = []
        self.step_count = 0
        self.start_time = time.time()
        
        logger.info("Working memory reset")


if __name__ == "__main__":
    # Test the memory systems
    print("Testing Memory Systems...")
    
    # Test StateHasher
    print("\n1. Testing StateHasher:")
    test_obs = {
        'url': 'https://example.com',
        'title': 'Test Page',
        'axtree_txt': 'button "Submit" input "email" link "Home"'
    }
    state_hash = StateHasher.hash_state(test_obs)
    print(f"State hash: {state_hash}")
    
    # Test EpisodicMemory
    print("\n2. Testing EpisodicMemory:")
    episodic = EpisodicMemory(persistence_file="test_memory.json")
    
    # Store some test episodes
    episodic.store_episode(
        state_hash=state_hash,
        action="click(submit_button)",
        outcome="success",
        success=True,
        domain="webclones.omnizon",
        execution_time=1.5,
        confidence=0.8
    )
    
    # Get best action
    best_action = episodic.get_best_action_for_state(state_hash, "webclones.omnizon")
    print(f"Best action for state: {best_action}")
    
    # Get domain insights
    insights = episodic.get_domain_insights("webclones.omnizon")
    print(f"Domain insights: {insights}")
    
    # Test WorkingMemory
    print("\n3. Testing WorkingMemory:")
    working = WorkingMemory()
    working.set_goal("Send an email to john@example.com", "webclones.gomail")
    
    print(f"Sub-goals: {working.sub_goals}")
    print(f"Next sub-goal: {working.get_next_sub_goal()}")
    
    # Mark some steps as completed
    working.mark_step_completed("navigate_to_compose", "click(compose_button)", True)
    working.mark_step_completed("enter_recipient", "type(to_field, 'john@example.com')", True)
    
    progress = working.get_progress_summary()
    print(f"Progress: {progress}")
    
    # Save memory
    episodic.save_memory()
    
    print("\nMemory systems test completed!")
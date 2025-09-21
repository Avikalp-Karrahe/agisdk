#!/usr/bin/env python3
"""
Enhanced AI Agent System v2.0
Implementing comprehensive cognitive architecture based on PRD and Technical Architecture

Key Features:
- Multi-layered memory systems (episodic, working, semantic)
- Self-critique and continuous learning
- Hierarchical planning with adaptive replanning
- Advanced retry mechanisms with intelligent error handling
- Domain-specific optimizations
- Real-time performance monitoring
- REAL benchmark integration

Author: Enhanced Agent Development Team
Version: 2.0
Date: January 2025
"""

import re
import json
import time
import random
import traceback
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Import our enhanced components
try:
    from memory_systems import EpisodicMemory, WorkingMemory, StateHasher
    from self_critique import SelfCritiqueSystem, ActionCritique
    from planning_system import HierarchicalPlanner, SubGoal, ActionPlan, PlanStatus
    from advanced_retry_system import AdvancedRetrySystem, RetryStrategy, RetryResult
except ImportError as e:
    print(f"Warning: Could not import enhanced components: {e}")
    # We'll define minimal fallbacks if needed

try:
    from agisdk.REAL.browsergym.experiments import Agent, AbstractAgentArgs
    from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
except ImportError as e:
    print(f"Warning: Could not import browsergym components: {e}")
    # Define minimal fallbacks for development
    class Agent:
        def get_action(self, obs):
            return "", {}
    class AbstractAgentArgs:
        pass
    class HighLevelActionSet:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Comprehensive metrics for agent performance tracking."""
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    retry_count: int = 0
    total_execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    planning_time: float = 0.0
    critique_time: float = 0.0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    learning_rate: float = 0.0
    
    def update_success_rate(self):
        """Update success rate based on current metrics."""
        if self.total_actions > 0:
            self.success_rate = self.successful_actions / self.total_actions
    
    def update_avg_response_time(self):
        """Update average response time."""
        if self.total_actions > 0:
            self.avg_response_time = self.total_execution_time / self.total_actions

@dataclass
class CognitiveState:
    """Represents the current cognitive state of the agent."""
    current_goal: Optional[str] = None
    current_domain: Optional[str] = None
    active_plan: Optional[List[SubGoal]] = None
    current_sub_goal: Optional[SubGoal] = None
    confidence_level: float = 0.5
    attention_focus: List[str] = None
    working_memory_load: float = 0.0
    last_action_critique: Optional[ActionCritique] = None
    
    def __post_init__(self):
        if self.attention_focus is None:
            self.attention_focus = []

class EnhancedAgentV2(Agent):
    """
    Enhanced AI Agent with comprehensive cognitive architecture.
    
    This agent implements a multi-layered cognitive system with:
    - Memory systems for learning and adaptation
    - Self-critique for continuous improvement
    - Hierarchical planning for complex task execution
    - Advanced retry mechanisms for robust error handling
    """
    
    def __init__(self, config: Dict[str, Any] = None, model_name: str = "gpt-4"):
        super().__init__()
        
        # Configuration
        self.config = config or {}
        self.model_name = model_name
        self.max_steps = self.config.get("max_steps", 50)
        self.timeout_ms = self.config.get("timeout_ms", 3000)
        self.enable_learning = self.config.get("enable_learning", True)
        self.enable_planning = self.config.get("enable_planning", True)
        self.enable_critique = self.config.get("enable_critique", True)
        self.persistence_dir = Path(self.config.get("persistence_dir", "./agent_data"))
        
        # Create persistence directory
        self.persistence_dir.mkdir(exist_ok=True)
        
        # Initialize cognitive components
        self._initialize_cognitive_systems()
        
        # Initialize metrics and state
        self.metrics = AgentMetrics()
        self.cognitive_state = CognitiveState()
        self.step_count = 0
        self.session_start_time = time.time()
        
        # Action history for learning
        self.action_history = []
        self.state_history = []
        
        # Initialize action set
        try:
            self.action_set = HighLevelActionSet(
                subsets=["chat", "bid", "infeas"],
                strict=False,
                multiaction=False,
                demo_mode="off"
            )
        except (TypeError, AttributeError):
            # Fallback for when HighLevelActionSet doesn't accept arguments
            self.action_set = HighLevelActionSet()
        
        logger.info(f"Enhanced Agent v2.0 initialized with config: {self.config}")
    
    def _initialize_cognitive_systems(self):
        """Initialize all cognitive subsystems."""
        try:
            # Memory systems
            if self.enable_learning:
                self.episodic_memory = EpisodicMemory(
                    max_episodes=self.config.get("max_episodes", 5000),
                    persistence_file=str(self.persistence_dir / "episodic_memory.json")
                )
                self.working_memory = WorkingMemory()
                logger.info("Memory systems initialized")
            
            # Self-critique system
            if self.enable_critique:
                self.critique_system = SelfCritiqueSystem()
                logger.info("Self-critique system initialized")
            
            # Planning system
            if self.enable_planning:
                self.planner = HierarchicalPlanner(
                    persistence_file=str(self.persistence_dir / "planning_memory.json")
                )
                logger.info("Hierarchical planner initialized")
            
            # Advanced retry system
            self.retry_system = AdvancedRetrySystem(
                max_retries=self.config.get("max_retries", 5),
                base_delay=self.config.get("base_delay", 1.0)
            )
            logger.info("Advanced retry system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing cognitive systems: {e}")
            # Initialize minimal fallbacks
            self.episodic_memory = None
            self.working_memory = None
            self.critique_system = None
            self.planner = None
            self.retry_system = None
    
    def obs_preprocessor(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced observation preprocessing with cognitive integration.
        """
        start_time = time.time()
        
        try:
            # Extract basic information
            processed_obs = {
                'url': obs.get('url', ''),
                'title': obs.get('title', ''),
                'axtree_txt': obs.get('axtree_txt', ''),
                'screenshot': obs.get('screenshot'),
                'goal': self._extract_goal(obs),
                'domain': self._extract_domain(obs),
                'timestamp': datetime.now().isoformat(),
                'step_count': self.step_count
            }
            
            # Create state hash for memory systems
            if self.episodic_memory:
                processed_obs['state_hash'] = StateHasher.hash_state(obs)
            
            # Update working memory with current context
            if self.working_memory and processed_obs['goal']:
                if processed_obs['goal'] != self.cognitive_state.current_goal:
                    self.working_memory.set_goal(processed_obs['goal'], processed_obs['domain'])
                    self.cognitive_state.current_goal = processed_obs['goal']
                    self.cognitive_state.current_domain = processed_obs['domain']
            
            # Update cognitive state
            self._update_cognitive_state(processed_obs)
            
            processing_time = time.time() - start_time
            logger.debug(f"Observation preprocessing completed in {processing_time:.3f}s")
            
            return processed_obs
            
        except Exception as e:
            logger.error(f"Error in observation preprocessing: {e}")
            return obs
    
    def get_action(self, obs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Enhanced action selection with full cognitive architecture integration.
        """
        start_time = time.time()
        self.step_count += 1
        
        try:
            # Preprocess observations
            processed_obs = self.obs_preprocessor(obs)
            
            # Store current state for learning
            self.state_history.append(processed_obs)
            
            # Get action using cognitive architecture
            action = self._get_cognitive_action(processed_obs)
            
            # Record action in history
            action_record = {
                'step': self.step_count,
                'action': action,
                'state_hash': processed_obs.get('state_hash'),
                'timestamp': time.time(),
                'goal': processed_obs.get('goal'),
                'domain': processed_obs.get('domain')
            }
            self.action_history.append(action_record)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.metrics.total_execution_time += execution_time
            self.metrics.total_actions += 1
            self.metrics.update_avg_response_time()
            
            logger.info(f"Step {self.step_count}: Action selected in {execution_time:.3f}s")
            logger.debug(f"Action: {action}")
            
            return action, {}
            
        except Exception as e:
            logger.error(f"Error in action selection: {e}")
            logger.error(traceback.format_exc())
            
            # Fallback action
            fallback_action = self._get_fallback_action(obs)
            return fallback_action, {}
    
    def _get_cognitive_action(self, obs: Dict[str, Any]) -> str:
        """
        Core cognitive action selection using all available systems.
        """
        # Phase 1: Memory-based action retrieval
        memory_action = self._get_memory_based_action(obs)
        if memory_action and self._validate_action(memory_action, obs):
            logger.debug("Using memory-based action")
            return memory_action
        
        # Phase 2: Planning-based action selection
        if self.enable_planning:
            planning_action = self._get_planning_based_action(obs)
            if planning_action and self._validate_action(planning_action, obs):
                logger.debug("Using planning-based action")
                return planning_action
        
        # Phase 3: Heuristic-based action generation
        heuristic_action = self._get_heuristic_action(obs)
        if heuristic_action and self._validate_action(heuristic_action, obs):
            logger.debug("Using heuristic-based action")
            return heuristic_action
        
        # Phase 4: Fallback action
        logger.warning("Using fallback action - no suitable action found")
        return self._get_fallback_action(obs)
    
    def _get_memory_based_action(self, obs: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve action based on episodic memory of successful patterns.
        """
        if not self.episodic_memory or not obs.get('state_hash'):
            return None
        
        try:
            # Get best action for current state
            domain = obs.get('domain', 'general')
            result = self.episodic_memory.get_best_action_for_state(
                obs['state_hash'], domain
            )
            
            if result and result[1] > 0.7:  # Confidence threshold
                action, confidence = result
                logger.debug(f"Memory suggests action: {action} (confidence: {confidence:.2f})")
                return action
            
            return None
            
        except Exception as e:
            logger.error(f"Error in memory-based action retrieval: {e}")
            return None
    
    def _get_planning_based_action(self, obs: Dict[str, Any]) -> Optional[str]:
        """
        Get action based on hierarchical planning system.
        """
        if not self.planner:
            return None
        
        try:
            goal = obs.get('goal')
            domain = obs.get('domain', 'general')
            
            if not goal:
                return None
            
            # Create or update plan if needed
            if not self.cognitive_state.active_plan:
                self.cognitive_state.active_plan = self.planner.create_plan(
                    goal, domain, obs
                )
                logger.info(f"Created new plan with {len(self.cognitive_state.active_plan)} sub-goals")
            
            # Get next action from current sub-goal
            if self.cognitive_state.active_plan:
                # Find current sub-goal
                current_sub_goal = None
                for sub_goal in self.cognitive_state.active_plan:
                    if sub_goal.status == PlanStatus.PENDING or sub_goal.status == PlanStatus.IN_PROGRESS:
                        current_sub_goal = sub_goal
                        break
                
                if current_sub_goal:
                    self.cognitive_state.current_sub_goal = current_sub_goal
                    action_plan = self.planner.get_next_action_plan(obs, current_sub_goal)
                    
                    if action_plan:
                        # Convert action plan to executable action
                        action = self._convert_action_plan_to_action(action_plan)
                        logger.debug(f"Planning suggests action: {action}")
                        return action
            
            return None
            
        except Exception as e:
            logger.error(f"Error in planning-based action selection: {e}")
            return None
    
    def _get_heuristic_action(self, obs: Dict[str, Any]) -> Optional[str]:
        """
        Generate action using domain-specific heuristics.
        """
        try:
            domain = obs.get('domain', 'general')
            goal = obs.get('goal', '')
            axtree = obs.get('axtree_txt', '')
            url = obs.get('url', '')
            
            # Domain-specific heuristics
            if 'omnizon' in domain.lower() or 'omnizon' in url.lower():
                return self._get_omnizon_heuristic_action(obs, goal, axtree)
            elif 'email' in domain.lower() or 'mail' in url.lower():
                return self._get_email_heuristic_action(obs, goal, axtree)
            elif 'calendar' in domain.lower() or 'calendar' in url.lower():
                return self._get_calendar_heuristic_action(obs, goal, axtree)
            else:
                return self._get_general_heuristic_action(obs, goal, axtree)
                
        except Exception as e:
            logger.error(f"Error in heuristic action generation: {e}")
            return None
    
    def _get_omnizon_heuristic_action(self, obs: Dict[str, Any], goal: str, axtree: str) -> Optional[str]:
        """
        Omnizon-specific heuristic actions for e-commerce tasks.
        """
        goal_lower = goal.lower()
        
        # Search phase
        if any(keyword in goal_lower for keyword in ['search', 'find', 'look for']):
            # Look for search box
            if 'searchbox' in axtree or 'search' in axtree:
                search_term = self._extract_search_term(goal)
                if search_term:
                    return f"type(text='{search_term}')"
            
            # Look for search button
            if 'search' in axtree and 'button' in axtree:
                return "click(text='Search')"
        
        # Product selection phase
        if any(keyword in goal_lower for keyword in ['select', 'choose', 'click']):
            # Look for product links
            if 'link' in axtree and any(product in axtree.lower() for product in ['laptop', 'phone', 'product']):
                return "click(text='product')"
        
        # Add to cart phase
        if 'cart' in goal_lower or 'add' in goal_lower:
            if 'add to cart' in axtree.lower():
                return "click(text='Add to Cart')"
            if 'add to basket' in axtree.lower():
                return "click(text='Add to Basket')"
        
        # Checkout phase
        if any(keyword in goal_lower for keyword in ['checkout', 'purchase', 'buy']):
            if 'checkout' in axtree.lower():
                return "click(text='Checkout')"
            if 'proceed' in axtree.lower():
                return "click(text='Proceed')"
        
        return None
    
    def _get_email_heuristic_action(self, obs: Dict[str, Any], goal: str, axtree: str) -> Optional[str]:
        """
        Email-specific heuristic actions.
        """
        goal_lower = goal.lower()
        
        if 'compose' in goal_lower or 'send' in goal_lower:
            if 'compose' in axtree.lower():
                return "click(text='Compose')"
        
        if 'to:' in goal_lower or '@' in goal:
            # Extract email address
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', goal)
            if email_match and 'textbox' in axtree:
                return f"type(text='{email_match.group()}')"
        
        if 'subject' in goal_lower:
            subject_match = re.search(r'subject[:\s]+([^,\.]+)', goal_lower)
            if subject_match and 'textbox' in axtree:
                return f"type(text='{subject_match.group(1).strip()}')"
        
        return None
    
    def _get_calendar_heuristic_action(self, obs: Dict[str, Any], goal: str, axtree: str) -> Optional[str]:
        """
        Calendar-specific heuristic actions.
        """
        goal_lower = goal.lower()
        
        if 'schedule' in goal_lower or 'meeting' in goal_lower:
            if 'new event' in axtree.lower() or 'create' in axtree.lower():
                return "click(text='New Event')"
        
        if 'time' in goal_lower:
            time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2}\s*[ap]m)', goal_lower)
            if time_match and 'textbox' in axtree:
                return f"type(text='{time_match.group()}')"
        
        return None
    
    def _get_general_heuristic_action(self, obs: Dict[str, Any], goal: str, axtree: str) -> Optional[str]:
        """
        General heuristic actions for common web interactions.
        """
        # Look for obvious interactive elements
        if 'button' in axtree and 'submit' in axtree.lower():
            return "click(text='Submit')"
        
        if 'textbox' in axtree and any(keyword in goal.lower() for keyword in ['enter', 'type', 'input']):
            # Try to extract text to type from goal
            text_match = re.search(r'["\']([^"\']+)["\']', goal)
            if text_match:
                return f"type(text='{text_match.group(1)}')"
        
        if 'link' in axtree and any(keyword in goal.lower() for keyword in ['click', 'go to', 'navigate']):
            return "click(text='link')"
        
        return None
    
    def _validate_action(self, action: str, obs: Dict[str, Any]) -> bool:
        """
        Validate that an action is applicable to the current state.
        """
        try:
            axtree = obs.get('axtree_txt', '')
            
            # Basic validation - check if target elements exist
            if 'click(' in action:
                # Extract click target
                target_match = re.search(r'click\(.*?text=["\']([^"\']+)["\']', action)
                if target_match:
                    target_text = target_match.group(1).lower()
                    return target_text in axtree.lower()
            
            elif 'type(' in action:
                # Check if there are input fields
                return 'textbox' in axtree or 'input' in axtree
            
            return True  # Default to valid for other actions
            
        except Exception as e:
            logger.error(f"Error validating action: {e}")
            return False
    
    def _convert_action_plan_to_action(self, action_plan: ActionPlan) -> str:
        """
        Convert an ActionPlan object to an executable action string.
        """
        try:
            action_type = action_plan.action_type
            target = action_plan.target_element
            params = action_plan.parameters
            
            if action_type == 'click':
                if 'text' in params:
                    return f"click(text='{params['text']}')"
                else:
                    return f"click({target})"
            
            elif action_type == 'type':
                text = params.get('text', '')
                return f"type(text='{text}')"
            
            elif action_type == 'scroll':
                direction = params.get('direction', 'down')
                return f"scroll({direction})"
            
            else:
                return f"{action_type}({target})"
                
        except Exception as e:
            logger.error(f"Error converting action plan: {e}")
            return "scroll(down)"  # Safe fallback
    
    def _get_fallback_action(self, obs: Dict[str, Any]) -> str:
        """
        Generate a safe fallback action when all other methods fail.
        """
        axtree = obs.get('axtree_txt', '')
        
        # Try to find any clickable element
        if 'button' in axtree:
            return "click(text='button')"
        elif 'link' in axtree:
            return "click(text='link')"
        elif 'textbox' in axtree:
            return "type(text='test')"
        else:
            return "scroll(down)"
    
    def _extract_goal(self, obs: Dict[str, Any]) -> Optional[str]:
        """
        Extract goal from observation with improved error handling.
        """
        try:
            # Handle different observation formats
            if isinstance(obs, dict):
                if 'goal' in obs:
                    goal_obj = obs['goal']
                    if isinstance(goal_obj, dict):
                        return goal_obj.get('description') or goal_obj.get('text') or str(goal_obj)
                    elif isinstance(goal_obj, list) and goal_obj:
                        return str(goal_obj[0])
                    else:
                        return str(goal_obj)
                
                # Try alternative keys
                for key in ['task', 'objective', 'instruction']:
                    if key in obs:
                        return str(obs[key])
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting goal: {e}")
            return None
    
    def _extract_domain(self, obs: Dict[str, Any]) -> str:
        """
        Extract domain from observation.
        """
        try:
            url = obs.get('url', '')
            
            if 'omnizon' in url.lower():
                return 'webclones.omnizon'
            elif 'email' in url.lower() or 'mail' in url.lower():
                return 'webclones.email'
            elif 'calendar' in url.lower():
                return 'webclones.calendar'
            else:
                return 'general'
                
        except Exception:
            return 'general'
    
    def _extract_search_term(self, goal: str) -> Optional[str]:
        """
        Extract search term from goal description.
        """
        try:
            goal_lower = goal.lower()
            
            # Look for quoted terms
            quoted_match = re.search(r'["\']([^"\']+)["\']', goal)
            if quoted_match:
                return quoted_match.group(1)
            
            # Look for "search for X" patterns
            search_patterns = [
                r'search for ([^,\.\n]+)',
                r'find ([^,\.\n]+)',
                r'look for ([^,\.\n]+)',
                r'looking for ([^,\.\n]+)'
            ]
            
            for pattern in search_patterns:
                match = re.search(pattern, goal_lower)
                if match:
                    return match.group(1).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting search term: {e}")
            return None
    
    def _update_cognitive_state(self, obs: Dict[str, Any]):
        """
        Update the agent's cognitive state based on current observations.
        """
        try:
            # Update attention focus based on current elements
            axtree = obs.get('axtree_txt', '')
            self.cognitive_state.attention_focus = self._extract_attention_elements(axtree)
            
            # Update working memory load
            if self.working_memory:
                progress = self.working_memory.get_progress_summary()
                self.cognitive_state.working_memory_load = progress.get('completion_rate', 0.0)
            
            # Update confidence based on recent performance
            if self.metrics.total_actions > 0:
                self.cognitive_state.confidence_level = self.metrics.success_rate
            
        except Exception as e:
            logger.error(f"Error updating cognitive state: {e}")
    
    def _extract_attention_elements(self, axtree: str) -> List[str]:
        """
        Extract key elements that should receive attention.
        """
        elements = []
        
        # Look for interactive elements
        if 'button' in axtree:
            elements.append('buttons')
        if 'textbox' in axtree:
            elements.append('input_fields')
        if 'link' in axtree:
            elements.append('links')
        if 'form' in axtree:
            elements.append('forms')
        
        return elements
    
    def post_action_callback(self, action: str, obs_before: Dict[str, Any], 
                           obs_after: Dict[str, Any], success: bool, error_msg: Optional[str] = None):
        """
        Post-action processing for learning and adaptation.
        """
        try:
            execution_time = time.time() - self.action_history[-1]['timestamp'] if self.action_history else 0.0
            
            # Update metrics
            if success:
                self.metrics.successful_actions += 1
            else:
                self.metrics.failed_actions += 1
            
            self.metrics.update_success_rate()
            
            # Self-critique if enabled
            if self.enable_critique and self.critique_system:
                critique_start = time.time()
                critique = self.critique_system.evaluate_action_outcome(
                    action, obs_before, obs_after, error_msg, execution_time
                )
                self.cognitive_state.last_action_critique = critique
                self.metrics.critique_time += time.time() - critique_start
            
            # Store in episodic memory if enabled
            if self.enable_learning and self.episodic_memory:
                state_hash = obs_before.get('state_hash')
                domain = obs_before.get('domain', 'general')
                
                if state_hash:
                    confidence = self.cognitive_state.last_action_critique.confidence_score if self.cognitive_state.last_action_critique else 0.5
                    
                    self.episodic_memory.store_episode(
                        state_hash=state_hash,
                        action=action,
                        outcome="success" if success else "failure",
                        success=success,
                        domain=domain,
                        execution_time=execution_time,
                        confidence=confidence
                    )
            
            # Update planning progress if enabled
            if self.enable_planning and self.planner and self.cognitive_state.current_sub_goal:
                self.planner.update_plan_progress(
                    self.cognitive_state.current_sub_goal.id,
                    success,
                    1,  # actual_steps
                    error_msg
                )
            
            logger.debug(f"Post-action processing completed for action: {action}")
            
        except Exception as e:
            logger.error(f"Error in post-action callback: {e}")
    
    def reset(self, seed: Optional[int] = None):
        """
        Reset agent state for new episode.
        """
        try:
            # Reset counters and state
            self.step_count = 0
            self.action_history = []
            self.state_history = []
            self.session_start_time = time.time()
            
            # Reset cognitive state
            self.cognitive_state = CognitiveState()
            
            # Reset working memory
            if self.working_memory:
                self.working_memory.reset()
            
            # Save persistent data
            if self.episodic_memory:
                self.episodic_memory.save_memory()
            
            logger.info("Agent reset completed")
            
        except Exception as e:
            logger.error(f"Error during reset: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive agent statistics.
        """
        try:
            session_time = time.time() - self.session_start_time
            
            stats = {
                'session_info': {
                    'session_duration': session_time,
                    'total_steps': self.step_count,
                    'steps_per_minute': (self.step_count / session_time * 60) if session_time > 0 else 0
                },
                'performance_metrics': asdict(self.metrics),
                'cognitive_state': {
                    'current_goal': self.cognitive_state.current_goal,
                    'current_domain': self.cognitive_state.current_domain,
                    'confidence_level': self.cognitive_state.confidence_level,
                    'working_memory_load': self.cognitive_state.working_memory_load,
                    'attention_focus': self.cognitive_state.attention_focus
                },
                'system_status': {
                    'memory_enabled': self.enable_learning,
                    'planning_enabled': self.enable_planning,
                    'critique_enabled': self.enable_critique,
                    'episodic_memory_size': len(self.episodic_memory.episodes) if self.episodic_memory else 0
                }
            }
            
            # Add domain insights if available
            if self.episodic_memory and self.cognitive_state.current_domain:
                domain_insights = self.episodic_memory.get_domain_insights(self.cognitive_state.current_domain)
                stats['domain_insights'] = domain_insights
            
            # Add planning metrics if available
            if self.planner:
                planning_metrics = self.planner.get_plan_metrics()
                stats['planning_metrics'] = planning_metrics
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}

class EnhancedAgentV2Args(AbstractAgentArgs):
    """
    Arguments class for Enhanced Agent v2.0.
    """
    
    def __init__(self, config: Dict[str, Any] = None, model_name: str = "gpt-4"):
        self.config = config or {
            'max_steps': 50,
            'timeout_ms': 3000,
            'enable_learning': True,
            'enable_planning': True,
            'enable_critique': True,
            'max_episodes': 5000,
            'max_retries': 5,
            'base_delay': 1.0,
            'persistence_dir': './agent_data'
        }
        self.model_name = model_name
    
    def make_agent(self) -> EnhancedAgentV2:
        """Create an instance of the enhanced agent."""
        return EnhancedAgentV2(config=self.config, model_name=self.model_name)

if __name__ == "__main__":
    # Example usage and testing
    print("Enhanced AI Agent System v2.0")
    print("=" * 50)
    
    # Create agent with comprehensive configuration
    config = {
        'max_steps': 50,
        'timeout_ms': 3000,
        'enable_learning': True,
        'enable_planning': True,
        'enable_critique': True,
        'max_episodes': 5000,
        'max_retries': 5,
        'persistence_dir': './agent_data'
    }
    
    agent_args = EnhancedAgentV2Args(config=config)
    agent = agent_args.make_agent()
    
    print(f"Agent initialized successfully!")
    print(f"Configuration: {config}")
    
    # Display initial stats
    stats = agent.get_stats()
    print(f"\nInitial Stats:")
    for category, data in stats.items():
        print(f"  {category}: {data}")
    
    print("\nAgent ready for task execution!")
#!/usr/bin/env python3
"""
Phase 4: Hierarchical Planning System

This module implements a comprehensive hierarchical task planning system that:
- Decomposes complex goals into manageable sub-goals
- Creates detailed action plans for each sub-goal
- Tracks execution progress and adapts plans based on results
- Provides replanning capabilities when original plans fail
- Integrates with the self-critique system for plan optimization

Author: AGI SDK Development Team
Date: 2025-06-15
Version: 1.0
"""

import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    """Status enumeration for plan execution tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class SubGoal:
    """Represents a sub-goal in the hierarchical plan."""
    id: str
    description: str
    priority: int
    estimated_steps: int
    dependencies: List[str]
    status: PlanStatus = PlanStatus.PENDING
    actual_steps: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence: float = 0.5
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['status'] = self.status.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SubGoal':
        """Create from dictionary."""
        data['status'] = PlanStatus(data['status'])
        return cls(**data)

@dataclass
class ActionPlan:
    """Detailed action plan for executing a sub-goal."""
    goal_id: str
    action_type: str
    target_element: str
    parameters: Dict[str, Any]
    expected_outcome: str
    confidence: float
    fallback_actions: List[str]
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ActionPlan':
        """Create from dictionary."""
        return cls(**data)

class HierarchicalPlanner:
    """Advanced hierarchical task planning system."""
    
    def __init__(self, persistence_file: str = "planning_memory.json"):
        self.goal_templates = self._initialize_goal_templates()
        self.action_strategies = self._initialize_action_strategies()
        self.current_plan: Optional[List[SubGoal]] = None
        self.execution_history: List[Dict] = []
        self.persistence_file = persistence_file
        self.plan_metrics = {
            'total_plans_created': 0,
            'successful_plans': 0,
            'failed_plans': 0,
            'replanning_events': 0,
            'average_plan_completion_time': 0.0,
            'most_successful_goal_types': {},
            'common_failure_patterns': {}
        }
        self._load_persistence()
    
    def create_plan(self, goal_description: str, domain: str, current_state: Dict) -> List[SubGoal]:
        """Create a hierarchical plan for achieving the goal."""
        logger.info(f"Creating plan for goal: {goal_description} in domain: {domain}")
        
        # Identify goal type
        goal_type = self._classify_goal(goal_description, domain)
        logger.info(f"Classified goal type: {goal_type}")
        
        # Get template for this goal type
        template = self.goal_templates.get(goal_type, self.goal_templates['default'])
        
        # Create sub-goals based on template
        sub_goals = []
        for i, sub_goal_template in enumerate(template['sub_goals']):
            sub_goal = SubGoal(
                id=f"{goal_type}_{i}_{int(time.time())}",
                description=sub_goal_template['description'],
                priority=sub_goal_template.get('priority', 1),
                estimated_steps=sub_goal_template.get('estimated_steps', 3),
                dependencies=sub_goal_template.get('dependencies', [])
            )
            sub_goals.append(sub_goal)
        
        # Customize plan based on current state
        sub_goals = self._customize_plan(sub_goals, current_state, domain)
        
        # Update metrics
        self.plan_metrics['total_plans_created'] += 1
        
        self.current_plan = sub_goals
        self._save_persistence()
        
        logger.info(f"Created plan with {len(sub_goals)} sub-goals")
        return sub_goals
    
    def get_next_action_plan(self, current_state: Dict, sub_goal: SubGoal) -> Optional[ActionPlan]:
        """Generate detailed action plan for current sub-goal."""
        logger.info(f"Generating action plan for sub-goal: {sub_goal.description}")
        
        strategy = self.action_strategies.get(sub_goal.description, {})
        if not strategy:
            logger.warning(f"No strategy found for sub-goal: {sub_goal.description}")
            return None
        
        # Select best action based on current state
        for action_option in strategy.get('actions', []):
            if self._is_action_applicable(action_option, current_state):
                action_plan = ActionPlan(
                    goal_id=sub_goal.id,
                    action_type=action_option['type'],
                    target_element=action_option['target'],
                    parameters=action_option.get('parameters', {}),
                    expected_outcome=action_option['expected_outcome'],
                    confidence=self._calculate_action_confidence(action_option, current_state),
                    fallback_actions=action_option.get('fallbacks', [])
                )
                logger.info(f"Generated action plan: {action_plan.action_type} on {action_plan.target_element}")
                return action_plan
        
        logger.warning(f"No applicable action found for sub-goal: {sub_goal.description}")
        return None
    
    def update_plan_progress(self, sub_goal_id: str, success: bool, actual_steps: int, 
                           error_message: Optional[str] = None):
        """Update plan progress based on execution results."""
        if not self.current_plan:
            return
        
        for sub_goal in self.current_plan:
            if sub_goal.id == sub_goal_id:
                sub_goal.actual_steps = actual_steps
                sub_goal.status = PlanStatus.COMPLETED if success else PlanStatus.FAILED
                sub_goal.end_time = time.time()
                
                if not success:
                    sub_goal.retry_count += 1
                    # Track failure patterns
                    failure_type = self._classify_failure(sub_goal.description, error_message)
                    if failure_type not in self.plan_metrics['common_failure_patterns']:
                        self.plan_metrics['common_failure_patterns'][failure_type] = 0
                    self.plan_metrics['common_failure_patterns'][failure_type] += 1
                
                logger.info(f"Updated sub-goal {sub_goal_id}: {'SUCCESS' if success else 'FAILED'}")
                break
        
        self._save_persistence()
    
    def should_replan(self, execution_state: Dict) -> bool:
        """Determine if replanning is necessary."""
        if not self.current_plan:
            return False
        
        # Check for multiple failures
        failed_goals = [g for g in self.current_plan if g.status == PlanStatus.FAILED]
        if len(failed_goals) > 2:
            logger.info("Replanning triggered: Multiple failures detected")
            return True
        
        # Check for goals that have exceeded retry limits
        max_retry_exceeded = [g for g in self.current_plan 
                            if g.retry_count >= g.max_retries and g.status == PlanStatus.FAILED]
        if max_retry_exceeded:
            logger.info("Replanning triggered: Max retries exceeded")
            return True
        
        # Check for time overruns
        current_time = time.time()
        for goal in self.current_plan:
            if (goal.start_time and 
                current_time - goal.start_time > goal.estimated_steps * 15):  # 15 seconds per step
                logger.info("Replanning triggered: Time overrun detected")
                return True
        
        # Check for unexpected state
        if execution_state.get('unexpected_state', False):
            logger.info("Replanning triggered: Unexpected state detected")
            return True
        
        return False
    
    def replan(self, failed_plan: List[SubGoal], current_state: Dict, 
              original_goal: str, domain: str) -> List[SubGoal]:
        """Generate alternative plan when current plan fails."""
        logger.info("Initiating replanning process")
        
        # Update metrics
        self.plan_metrics['replanning_events'] += 1
        
        # Analyze failure patterns
        failure_analysis = self._analyze_failures(failed_plan)
        logger.info(f"Failure analysis: {failure_analysis}")
        
        # Get alternative strategy
        alternative_strategy = self._get_alternative_strategy(
            original_goal, domain, failure_analysis
        )
        
        if alternative_strategy:
            logger.info(f"Using alternative strategy: {alternative_strategy}")
            return self.create_plan(alternative_strategy, domain, current_state)
        
        # Fallback: simplify original plan
        logger.info("Using simplified plan as fallback")
        simplified_plan = self._simplify_plan(failed_plan, current_state)
        self.current_plan = simplified_plan
        return simplified_plan
    
    def get_plan_metrics(self) -> Dict:
        """Get comprehensive planning metrics."""
        if self.current_plan:
            completed_goals = [g for g in self.current_plan if g.status == PlanStatus.COMPLETED]
            failed_goals = [g for g in self.current_plan if g.status == PlanStatus.FAILED]
            
            current_metrics = {
                'current_plan_progress': {
                    'total_goals': len(self.current_plan),
                    'completed_goals': len(completed_goals),
                    'failed_goals': len(failed_goals),
                    'completion_rate': len(completed_goals) / len(self.current_plan) if self.current_plan else 0
                }
            }
            
            return {**self.plan_metrics, **current_metrics}
        
        return self.plan_metrics
    
    def _classify_goal(self, goal_description: str, domain: str) -> str:
        """Classify goal type based on description and domain."""
        # Ensure goal_description is a string before calling .lower()
        goal_str = str(goal_description) if goal_description else ''
        goal_lower = goal_str.lower()
        domain_lower = domain.lower()
        
        # Calendar-related goals
        if any(keyword in goal_lower for keyword in ['schedule', 'meeting', 'appointment', 'calendar']):
            return 'calendar_schedule_meeting'
        
        # Email-related goals
        if any(keyword in goal_lower for keyword in ['email', 'compose', 'send', 'message']):
            return 'email_compose_send'
        
        # Social networking goals
        if any(keyword in goal_lower for keyword in ['connect', 'friend', 'follow', 'network']):
            return 'social_connect_message'
        
        # Restaurant/dining goals
        if any(keyword in goal_lower for keyword in ['restaurant', 'reservation', 'book', 'dining']):
            return 'restaurant_reservation'
        
        # E-commerce goals
        if any(keyword in goal_lower for keyword in ['buy', 'purchase', 'order', 'cart', 'checkout']):
            return 'ecommerce_purchase'
        
        # Travel/transportation goals
        if any(keyword in goal_lower for keyword in ['ride', 'uber', 'taxi', 'transport', 'book']):
            return 'transportation_booking'
        
        return 'default'
    
    def _customize_plan(self, sub_goals: List[SubGoal], current_state: Dict, domain: str) -> List[SubGoal]:
        """Customize plan based on current state and domain."""
        # Adjust priorities based on current state
        page_elements = current_state.get('elements', [])
        
        for goal in sub_goals:
            # Increase confidence if relevant elements are already visible
            if any(keyword in goal.description for keyword in ['navigate', 'find']):
                if any(element for element in page_elements if 'nav' in str(element).lower()):
                    goal.confidence += 0.2
            
            # Adjust estimated steps based on page complexity
            if len(page_elements) > 20:  # Complex page
                goal.estimated_steps += 2
            elif len(page_elements) < 5:  # Simple page
                goal.estimated_steps = max(1, goal.estimated_steps - 1)
        
        return sub_goals
    
    def _is_action_applicable(self, action_option: Dict, current_state: Dict) -> bool:
        """Check if action is applicable in current state."""
        target = action_option.get('target', '').lower()
        elements = [str(elem).lower() for elem in current_state.get('elements', [])]
        
        # Check if target element exists or similar elements exist
        if any(target in element for element in elements):
            return True
        
        # Check for semantic similarity
        target_keywords = target.split('_')
        for element in elements:
            if any(keyword in element for keyword in target_keywords):
                return True
        
        return False
    
    def _calculate_action_confidence(self, action_option: Dict, current_state: Dict) -> float:
        """Calculate confidence for action based on current state."""
        base_confidence = 0.4
        
        target = action_option.get('target', '').lower()
        elements = [str(elem).lower() for elem in current_state.get('elements', [])]
        
        # Increase confidence if target element is clearly present
        if any(target in element for element in elements):
            base_confidence += 0.4
        
        # Increase confidence based on action type reliability
        action_type = action_option.get('type', '')
        if action_type in ['click', 'type']:
            base_confidence += 0.1
        
        # Consider page stability
        if current_state.get('page_stable', True):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _analyze_failures(self, failed_plan: List[SubGoal]) -> Dict:
        """Analyze failure patterns in the plan."""
        analysis = {
            'failed_goals': [g for g in failed_plan if g.status == PlanStatus.FAILED],
            'common_failure_points': [],
            'time_overruns': [],
            'dependency_issues': [],
            'retry_exhausted': []
        }
        
        # Identify common failure patterns
        for goal in analysis['failed_goals']:
            if 'navigate' in goal.description:
                analysis['common_failure_points'].append('navigation_issues')
            elif 'select' in goal.description or 'click' in goal.description:
                analysis['common_failure_points'].append('element_interaction_issues')
            elif 'fill' in goal.description or 'enter' in goal.description:
                analysis['common_failure_points'].append('form_filling_issues')
            elif 'search' in goal.description:
                analysis['common_failure_points'].append('search_issues')
            
            # Check for time overruns
            if goal.start_time and goal.end_time:
                execution_time = goal.end_time - goal.start_time
                expected_time = goal.estimated_steps * 10  # 10 seconds per step
                if execution_time > expected_time * 1.5:
                    analysis['time_overruns'].append(goal.id)
            
            # Check for retry exhaustion
            if goal.retry_count >= goal.max_retries:
                analysis['retry_exhausted'].append(goal.id)
        
        return analysis
    
    def _get_alternative_strategy(self, original_goal: str, domain: str, 
                                failure_analysis: Dict) -> Optional[str]:
        """Get alternative strategy based on failure analysis."""
        common_failures = failure_analysis.get('common_failure_points', [])
        
        if 'navigation_issues' in common_failures:
            return f"simplified_{original_goal}"
        elif 'element_interaction_issues' in common_failures:
            return f"alternative_interaction_{original_goal}"
        elif 'form_filling_issues' in common_failures:
            return f"step_by_step_{original_goal}"
        elif 'search_issues' in common_failures:
            return f"direct_access_{original_goal}"
        
        return None
    
    def _simplify_plan(self, failed_plan: List[SubGoal], current_state: Dict) -> List[SubGoal]:
        """Create simplified version of failed plan."""
        simplified = []
        
        # Keep only essential sub-goals and reduce complexity
        for goal in failed_plan:
            if goal.priority <= 3 and goal.status != PlanStatus.COMPLETED:
                # Reset goal for retry
                goal.status = PlanStatus.PENDING
                goal.estimated_steps = max(1, goal.estimated_steps // 2)
                goal.retry_count = 0
                goal.confidence = max(0.3, goal.confidence - 0.1)
                simplified.append(goal)
        
        return simplified
    
    def _classify_failure(self, goal_description: str, error_message: Optional[str]) -> str:
        """Classify the type of failure for metrics tracking."""
        if error_message:
            error_lower = error_message.lower()
            if 'timeout' in error_lower:
                return 'timeout_error'
            elif 'element' in error_lower and 'not found' in error_lower:
                return 'element_not_found'
            elif 'click' in error_lower:
                return 'click_failure'
            elif 'type' in error_lower or 'input' in error_lower:
                return 'input_failure'
        
        # Classify based on goal description
        if 'navigate' in goal_description:
            return 'navigation_failure'
        elif 'search' in goal_description:
            return 'search_failure'
        elif 'fill' in goal_description or 'enter' in goal_description:
            return 'form_failure'
        
        return 'unknown_failure'
    
    def _save_persistence(self):
        """Save planning state to persistence file."""
        try:
            data = {
                'current_plan': [goal.to_dict() for goal in self.current_plan] if self.current_plan else [],
                'execution_history': self.execution_history,
                'plan_metrics': self.plan_metrics
            }
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save planning persistence: {e}")
    
    def _load_persistence(self):
        """Load planning state from persistence file."""
        try:
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            if data.get('current_plan'):
                self.current_plan = [SubGoal.from_dict(goal_data) for goal_data in data['current_plan']]
            
            self.execution_history = data.get('execution_history', [])
            self.plan_metrics.update(data.get('plan_metrics', {}))
            
            logger.info("Loaded planning persistence successfully")
        except FileNotFoundError:
            logger.info("No planning persistence file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load planning persistence: {e}")
    
    def _initialize_goal_templates(self) -> Dict[str, Dict]:
        """Initialize goal decomposition templates."""
        return {
            'calendar_schedule_meeting': {
                'sub_goals': [
                    {
                        'description': 'navigate_to_calendar',
                        'priority': 1,
                        'estimated_steps': 2
                    },
                    {
                        'description': 'select_date_time',
                        'priority': 2,
                        'estimated_steps': 4,
                        'dependencies': ['navigate_to_calendar']
                    },
                    {
                        'description': 'create_event_form',
                        'priority': 3,
                        'estimated_steps': 3,
                        'dependencies': ['select_date_time']
                    },
                    {
                        'description': 'fill_event_details',
                        'priority': 4,
                        'estimated_steps': 5,
                        'dependencies': ['create_event_form']
                    },
                    {
                        'description': 'save_event',
                        'priority': 5,
                        'estimated_steps': 2,
                        'dependencies': ['fill_event_details']
                    }
                ]
            },
            'email_compose_send': {
                'sub_goals': [
                    {
                        'description': 'navigate_to_compose',
                        'priority': 1,
                        'estimated_steps': 2
                    },
                    {
                        'description': 'enter_recipient',
                        'priority': 2,
                        'estimated_steps': 2,
                        'dependencies': ['navigate_to_compose']
                    },
                    {
                        'description': 'enter_subject',
                        'priority': 3,
                        'estimated_steps': 2,
                        'dependencies': ['enter_recipient']
                    },
                    {
                        'description': 'compose_message',
                        'priority': 4,
                        'estimated_steps': 3,
                        'dependencies': ['enter_subject']
                    },
                    {
                        'description': 'send_email',
                        'priority': 5,
                        'estimated_steps': 2,
                        'dependencies': ['compose_message']
                    }
                ]
            },
            'social_connect_message': {
                'sub_goals': [
                    {
                        'description': 'search_for_person',
                        'priority': 1,
                        'estimated_steps': 3
                    },
                    {
                        'description': 'view_profile',
                        'priority': 2,
                        'estimated_steps': 2,
                        'dependencies': ['search_for_person']
                    },
                    {
                        'description': 'initiate_connection',
                        'priority': 3,
                        'estimated_steps': 2,
                        'dependencies': ['view_profile']
                    },
                    {
                        'description': 'send_message',
                        'priority': 4,
                        'estimated_steps': 3,
                        'dependencies': ['initiate_connection']
                    }
                ]
            },
            'restaurant_reservation': {
                'sub_goals': [
                    {
                        'description': 'search_restaurants',
                        'priority': 1,
                        'estimated_steps': 3
                    },
                    {
                        'description': 'select_restaurant',
                        'priority': 2,
                        'estimated_steps': 2,
                        'dependencies': ['search_restaurants']
                    },
                    {
                        'description': 'choose_date_time',
                        'priority': 3,
                        'estimated_steps': 4,
                        'dependencies': ['select_restaurant']
                    },
                    {
                        'description': 'enter_party_details',
                        'priority': 4,
                        'estimated_steps': 3,
                        'dependencies': ['choose_date_time']
                    },
                    {
                        'description': 'confirm_reservation',
                        'priority': 5,
                        'estimated_steps': 2,
                        'dependencies': ['enter_party_details']
                    }
                ]
            },
            'ecommerce_purchase': {
                'sub_goals': [
                    {
                        'description': 'search_product',
                        'priority': 1,
                        'estimated_steps': 3
                    },
                    {
                        'description': 'select_product',
                        'priority': 2,
                        'estimated_steps': 2,
                        'dependencies': ['search_product']
                    },
                    {
                        'description': 'add_to_cart',
                        'priority': 3,
                        'estimated_steps': 2,
                        'dependencies': ['select_product']
                    },
                    {
                        'description': 'proceed_to_checkout',
                        'priority': 4,
                        'estimated_steps': 3,
                        'dependencies': ['add_to_cart']
                    },
                    {
                        'description': 'complete_purchase',
                        'priority': 5,
                        'estimated_steps': 4,
                        'dependencies': ['proceed_to_checkout']
                    }
                ]
            },
            'transportation_booking': {
                'sub_goals': [
                    {
                        'description': 'enter_pickup_location',
                        'priority': 1,
                        'estimated_steps': 2
                    },
                    {
                        'description': 'enter_destination',
                        'priority': 2,
                        'estimated_steps': 2,
                        'dependencies': ['enter_pickup_location']
                    },
                    {
                        'description': 'select_ride_type',
                        'priority': 3,
                        'estimated_steps': 3,
                        'dependencies': ['enter_destination']
                    },
                    {
                        'description': 'confirm_booking',
                        'priority': 4,
                        'estimated_steps': 2,
                        'dependencies': ['select_ride_type']
                    }
                ]
            },
            'default': {
                'sub_goals': [
                    {
                        'description': 'analyze_page',
                        'priority': 1,
                        'estimated_steps': 2
                    },
                    {
                        'description': 'identify_target_elements',
                        'priority': 2,
                        'estimated_steps': 3,
                        'dependencies': ['analyze_page']
                    },
                    {
                        'description': 'execute_primary_action',
                        'priority': 3,
                        'estimated_steps': 4,
                        'dependencies': ['identify_target_elements']
                    },
                    {
                        'description': 'verify_outcome',
                        'priority': 4,
                        'estimated_steps': 2,
                        'dependencies': ['execute_primary_action']
                    }
                ]
            }
        }
    
    def _initialize_action_strategies(self) -> Dict[str, Dict]:
        """Initialize action strategies for each sub-goal type."""
        return {
            'navigate_to_calendar': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'calendar_link',
                        'expected_outcome': 'calendar_page_loaded',
                        'fallbacks': ['search_for_calendar', 'use_navigation_menu']
                    },
                    {
                        'type': 'click',
                        'target': 'nav_calendar',
                        'expected_outcome': 'calendar_page_loaded',
                        'fallbacks': ['search_for_calendar']
                    }
                ]
            },
            'select_date_time': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'date_picker',
                        'expected_outcome': 'date_picker_opened',
                        'fallbacks': ['click_calendar_date', 'type_date_manually']
                    },
                    {
                        'type': 'click',
                        'target': 'time_slot',
                        'expected_outcome': 'time_selected',
                        'fallbacks': ['type_time_manually']
                    }
                ]
            },
            'create_event_form': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'new_event_button',
                        'expected_outcome': 'event_form_opened',
                        'fallbacks': ['click_add_event', 'double_click_date']
                    }
                ]
            },
            'fill_event_details': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'event_title_field',
                        'parameters': {'text': 'Meeting'},
                        'expected_outcome': 'title_entered',
                        'fallbacks': ['click_title_field_first']
                    },
                    {
                        'type': 'type',
                        'target': 'event_description_field',
                        'parameters': {'text': 'Important meeting'},
                        'expected_outcome': 'description_entered',
                        'fallbacks': ['skip_description']
                    }
                ]
            },
            'save_event': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'save_button',
                        'expected_outcome': 'event_saved',
                        'fallbacks': ['click_create_button', 'press_enter']
                    }
                ]
            },
            'navigate_to_compose': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'compose_button',
                        'expected_outcome': 'compose_window_opened',
                        'fallbacks': ['click_new_message', 'use_keyboard_shortcut']
                    }
                ]
            },
            'enter_recipient': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'to_field',
                        'parameters': {'text': 'recipient@example.com'},
                        'expected_outcome': 'recipient_entered',
                        'fallbacks': ['click_to_field_first']
                    }
                ]
            },
            'enter_subject': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'subject_field',
                        'parameters': {'text': 'Important Message'},
                        'expected_outcome': 'subject_entered',
                        'fallbacks': ['click_subject_field_first']
                    }
                ]
            },
            'compose_message': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'message_body',
                        'parameters': {'text': 'Hello, this is an important message.'},
                        'expected_outcome': 'message_composed',
                        'fallbacks': ['click_body_field_first']
                    }
                ]
            },
            'send_email': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'send_button',
                        'expected_outcome': 'email_sent',
                        'fallbacks': ['use_keyboard_shortcut', 'click_send_now']
                    }
                ]
            },
            'search_for_person': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'search_field',
                        'parameters': {'text': 'John Doe'},
                        'expected_outcome': 'search_results_displayed',
                        'fallbacks': ['click_search_field_first']
                    }
                ]
            },
            'view_profile': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'profile_link',
                        'expected_outcome': 'profile_page_loaded',
                        'fallbacks': ['click_first_result']
                    }
                ]
            },
            'initiate_connection': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'connect_button',
                        'expected_outcome': 'connection_request_sent',
                        'fallbacks': ['click_add_friend', 'click_follow']
                    }
                ]
            },
            'send_message': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'message_button',
                        'expected_outcome': 'message_window_opened',
                        'fallbacks': ['click_send_message']
                    },
                    {
                        'type': 'type',
                        'target': 'message_field',
                        'parameters': {'text': 'Hello! Nice to connect with you.'},
                        'expected_outcome': 'message_typed',
                        'fallbacks': ['click_message_field_first']
                    }
                ]
            },
            'search_restaurants': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'search_field',
                        'parameters': {'text': 'Italian restaurant'},
                        'expected_outcome': 'restaurant_results_displayed',
                        'fallbacks': ['click_search_field_first']
                    }
                ]
            },
            'select_restaurant': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'restaurant_card',
                        'expected_outcome': 'restaurant_details_loaded',
                        'fallbacks': ['click_first_restaurant']
                    }
                ]
            },
            'choose_date_time': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'date_selector',
                        'expected_outcome': 'date_picker_opened',
                        'fallbacks': ['click_calendar_icon']
                    },
                    {
                        'type': 'click',
                        'target': 'time_slot',
                        'expected_outcome': 'time_selected',
                        'fallbacks': ['select_available_time']
                    }
                ]
            },
            'enter_party_details': {
                'actions': [
                    {
                        'type': 'type',
                        'target': 'party_size_field',
                        'parameters': {'text': '4'},
                        'expected_outcome': 'party_size_entered',
                        'fallbacks': ['click_party_size_dropdown']
                    },
                    {
                        'type': 'type',
                        'target': 'special_requests_field',
                        'parameters': {'text': 'Window table preferred'},
                        'expected_outcome': 'special_requests_entered',
                        'fallbacks': ['skip_special_requests']
                    }
                ]
            },
            'confirm_reservation': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'confirm_button',
                        'expected_outcome': 'reservation_confirmed',
                        'fallbacks': ['click_book_now', 'click_reserve']
                    }
                ]
            },
            'analyze_page': {
                'actions': [
                    {
                        'type': 'observe',
                        'target': 'page_content',
                        'expected_outcome': 'page_structure_understood',
                        'fallbacks': ['scroll_to_see_more']
                    }
                ]
            },
            'identify_target_elements': {
                'actions': [
                    {
                        'type': 'scan',
                        'target': 'interactive_elements',
                        'expected_outcome': 'target_elements_identified',
                        'fallbacks': ['search_for_keywords']
                    }
                ]
            },
            'execute_primary_action': {
                'actions': [
                    {
                        'type': 'click',
                        'target': 'primary_button',
                        'expected_outcome': 'action_executed',
                        'fallbacks': ['try_alternative_element']
                    }
                ]
            },
            'verify_outcome': {
                'actions': [
                    {
                        'type': 'observe',
                        'target': 'page_changes',
                        'expected_outcome': 'outcome_verified',
                        'fallbacks': ['wait_for_changes']
                    }
                ]
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize planner
    planner = HierarchicalPlanner()
    
    # Example: Create a plan for scheduling a meeting
    current_state = {
        'elements': ['calendar_link', 'nav_menu', 'date_picker', 'new_event_button'],
        'page_stable': True
    }
    
    plan = planner.create_plan(
        goal_description="Schedule a meeting for tomorrow at 2 PM",
        domain="calendar",
        current_state=current_state
    )
    
    print("\n=== Created Plan ===")
    for i, sub_goal in enumerate(plan):
        print(f"{i+1}. {sub_goal.description} (Priority: {sub_goal.priority}, Steps: {sub_goal.estimated_steps})")
    
    # Example: Get action plan for first sub-goal
    if plan:
        action_plan = planner.get_next_action_plan(current_state, plan[0])
        if action_plan:
            print(f"\n=== Action Plan for '{plan[0].description}' ===")
            print(f"Action: {action_plan.action_type} on {action_plan.target_element}")
            print(f"Expected: {action_plan.expected_outcome}")
            print(f"Confidence: {action_plan.confidence:.2f}")
            print(f"Fallbacks: {action_plan.fallback_actions}")
    
    # Example: Update progress and check metrics
    if plan:
        planner.update_plan_progress(plan[0].id, success=True, actual_steps=2)
        metrics = planner.get_plan_metrics()
        print(f"\n=== Planning Metrics ===")
        print(f"Total plans created: {metrics['total_plans_created']}")
        if 'current_plan_progress' in metrics:
            progress = metrics['current_plan_progress']
            print(f"Current plan progress: {progress['completed_goals']}/{progress['total_goals']} goals completed")
            print(f"Completion rate: {progress['completion_rate']:.1%}")
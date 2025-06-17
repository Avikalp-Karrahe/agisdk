#!/usr/bin/env python3
"""
Self-Critique System for V3 Enhanced AGI Agent

Implements Phase 3 improvements:
- Action Evaluation: Comprehensive assessment of action outcomes
- Confidence Scoring: Dynamic confidence calculation based on context
- Alternative Suggestions: Smart recommendations for failed actions
- Effectiveness Tracking: Historical performance analysis
- Error Pattern Recognition: Learning from common failure modes
"""

import re
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ActionCritique:
    """Comprehensive critique of an action's performance."""
    action: str
    confidence_score: float
    effectiveness_score: float
    alternative_actions: List[str]
    reasoning: str
    recommendations: List[str]
    error_analysis: Optional[str] = None
    improvement_suggestions: List[str] = None

class SelfCritiqueSystem:
    """Advanced self-critique and reflection system."""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.effectiveness_history = defaultdict(list)
        self.error_patterns = defaultdict(int)
        self.action_success_rates = defaultdict(float)
        
        self.success_indicators = {
            'page_change': ['url changed', 'new page loaded', 'navigation successful'],
            'form_submission': ['form submitted', 'data saved', 'submission successful'],
            'element_interaction': ['clicked', 'typed', 'selected', 'interaction successful'],
            'navigation': ['navigated', 'redirected', 'moved', 'page loaded'],
            'search': ['results found', 'search completed', 'items displayed'],
            'login': ['logged in', 'authentication successful', 'dashboard loaded']
        }
        
        self.error_patterns_db = {
            'element_not_found': {
                'keywords': ['not found', 'does not exist', 'cannot locate'],
                'severity': 'high',
                'alternatives': [
                    'wait_for_element_to_appear',
                    'scroll_to_find_element',
                    'try_alternative_selector',
                    'refresh_page_and_retry'
                ]
            },
            'timeout_error': {
                'keywords': ['timeout', 'timed out', 'took too long'],
                'severity': 'medium',
                'alternatives': [
                    'increase_wait_time',
                    'check_page_loading_status',
                    'try_with_explicit_wait',
                    'break_into_smaller_steps'
                ]
            },
            'click_failed': {
                'keywords': ['click failed', 'not clickable', 'element blocked'],
                'severity': 'medium',
                'alternatives': [
                    'try_javascript_click',
                    'scroll_element_into_view',
                    'wait_for_element_to_be_clickable',
                    'remove_overlaying_elements'
                ]
            },
            'input_failed': {
                'keywords': ['input failed', 'cannot type', 'field not editable'],
                'severity': 'medium',
                'alternatives': [
                    'clear_field_before_typing',
                    'click_field_first',
                    'use_keyboard_shortcuts',
                    'try_alternative_input_method'
                ]
            }
        }
    
    def evaluate_action_outcome(self, action: str, before_state: Dict, 
                              after_state: Dict, error_msg: Optional[str] = None,
                              execution_time: float = 0.0) -> ActionCritique:
        """Comprehensive evaluation of action outcome."""
        
        # Calculate effectiveness score
        effectiveness = self._assess_effectiveness(before_state, after_state, action)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(action, before_state, error_msg, execution_time)
        
        # Generate alternative actions
        alternatives = self._suggest_alternatives(action, before_state, error_msg)
        
        # Analyze error patterns
        error_analysis = self._analyze_error_patterns(error_msg) if error_msg else None
        
        # Generate reasoning
        reasoning = self._generate_reasoning(action, effectiveness, confidence, error_msg)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(action, effectiveness, confidence, error_analysis)
        
        # Generate improvement suggestions
        improvements = self._suggest_improvements(action, effectiveness, confidence, error_analysis)
        
        # Update historical data
        self._update_history(action, effectiveness, error_msg)
        
        return ActionCritique(
            action=action,
            confidence_score=confidence,
            effectiveness_score=effectiveness,
            alternative_actions=alternatives,
            reasoning=reasoning,
            recommendations=recommendations,
            error_analysis=error_analysis,
            improvement_suggestions=improvements
        )
    
    def _assess_effectiveness(self, before_state: Dict, after_state: Dict, action: str) -> float:
        """Assess how effective the action was."""
        effectiveness_score = 0.0
        
        # Check for positive changes
        if self._page_changed(before_state, after_state):
            effectiveness_score += 0.3
            logger.debug("Page change detected - effectiveness +0.3")
        
        if self._new_elements_appeared(before_state, after_state):
            effectiveness_score += 0.2
            logger.debug("New elements appeared - effectiveness +0.2")
        
        if self._form_data_accepted(before_state, after_state):
            effectiveness_score += 0.3
            logger.debug("Form data accepted - effectiveness +0.3")
        
        if self._goal_progress_made(before_state, after_state, action):
            effectiveness_score += 0.2
            logger.debug("Goal progress detected - effectiveness +0.2")
        
        # Check for negative indicators
        if self._error_occurred(before_state, after_state):
            effectiveness_score -= 0.2
            logger.debug("Error occurred - effectiveness -0.2")
        
        return max(0.0, min(1.0, effectiveness_score))
    
    def _calculate_confidence(self, action: str, state: Dict, error_msg: Optional[str], 
                            execution_time: float) -> float:
        """Calculate confidence score for the action."""
        base_confidence = 0.5
        
        # Reduce confidence if there was an error
        if error_msg:
            base_confidence -= 0.3
            
            # Specific error penalties
            error_lower = error_msg.lower()
            if 'not found' in error_lower:
                base_confidence -= 0.2
            elif 'timeout' in error_lower:
                base_confidence -= 0.1
            elif 'failed' in error_lower:
                base_confidence -= 0.2
            elif 'blocked' in error_lower or 'overlapped' in error_lower:
                base_confidence -= 0.15
        
        # Increase confidence based on action type and context
        if 'click' in action and self._element_clearly_identified(action, state):
            base_confidence += 0.2
        
        if 'type' in action and self._input_field_available(action, state):
            base_confidence += 0.2
        
        # Execution time factor
        if execution_time > 0:
            if execution_time < 2.0:  # Fast execution usually means success
                base_confidence += 0.1
            elif execution_time > 10.0:  # Very slow might indicate problems
                base_confidence -= 0.1
        
        # Historical success rate
        historical_success = self.action_success_rates.get(action, 0.5)
        base_confidence = (base_confidence + historical_success) / 2
        
        return max(0.0, min(1.0, base_confidence))
    
    def _suggest_alternatives(self, action: str, state: Dict, error_msg: Optional[str]) -> List[str]:
        """Suggest alternative actions based on current context."""
        alternatives = []
        
        # Error-based alternatives
        if error_msg:
            for pattern_name, pattern_info in self.error_patterns_db.items():
                if any(keyword in error_msg.lower() for keyword in pattern_info['keywords']):
                    alternatives.extend(pattern_info['alternatives'])
                    break
        
        # Action-type based alternatives
        if 'click' in action:
            alternatives.extend([
                'double_click_instead',
                'right_click_for_context_menu',
                'hover_before_clicking',
                'use_keyboard_enter'
            ])
        elif 'type' in action:
            alternatives.extend([
                'clear_field_before_typing',
                'type_character_by_character',
                'use_keyboard_shortcuts',
                'paste_instead_of_typing'
            ])
        elif 'scroll' in action:
            alternatives.extend([
                'use_page_down_key',
                'scroll_to_specific_element',
                'use_mouse_wheel',
                'navigate_with_keyboard'
            ])
        
        # Remove duplicates and return top alternatives
        return list(dict.fromkeys(alternatives))[:5]
    
    def _analyze_error_patterns(self, error_msg: str) -> Optional[str]:
        """Analyze error message for patterns and categorization."""
        if not error_msg:
            return None
        
        error_lower = error_msg.lower()
        
        for pattern_name, pattern_info in self.error_patterns_db.items():
            if any(keyword in error_lower for keyword in pattern_info['keywords']):
                self.error_patterns[pattern_name] += 1
                return f"Error pattern '{pattern_name}' detected (severity: {pattern_info['severity']}). " \
                       f"This pattern has occurred {self.error_patterns[pattern_name]} times."
        
        # Generic error analysis
        self.error_patterns['unknown_error'] += 1
        return f"Unknown error pattern detected: {error_msg[:100]}..."
    
    def _generate_reasoning(self, action: str, effectiveness: float, 
                          confidence: float, error_msg: Optional[str]) -> str:
        """Generate human-readable reasoning for the evaluation."""
        reasoning_parts = []
        
        # Effectiveness reasoning
        if effectiveness > 0.7:
            reasoning_parts.append("Action was highly effective")
        elif effectiveness > 0.4:
            reasoning_parts.append("Action was moderately effective")
        else:
            reasoning_parts.append("Action had low effectiveness")
        
        # Confidence reasoning
        if confidence > 0.7:
            reasoning_parts.append("with high confidence")
        elif confidence > 0.4:
            reasoning_parts.append("with moderate confidence")
        else:
            reasoning_parts.append("with low confidence")
        
        # Error reasoning
        if error_msg:
            reasoning_parts.append(f"Error encountered: {error_msg[:100]}")
        
        # Historical context
        if action in self.action_success_rates:
            success_rate = self.action_success_rates[action]
            if success_rate > 0.8:
                reasoning_parts.append("This action type has high historical success")
            elif success_rate < 0.3:
                reasoning_parts.append("This action type has low historical success")
        
        return ". ".join(reasoning_parts) + "."
    
    def _generate_recommendations(self, action: str, effectiveness: float, 
                                confidence: float, error_analysis: Optional[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if effectiveness < 0.3:
            recommendations.append("Consider alternative approach to achieve goal")
        
        if confidence < 0.5:
            recommendations.append("Gather more context before next action")
        
        if effectiveness < 0.5 and confidence < 0.5:
            recommendations.append("Consider breaking down task into smaller steps")
        
        if error_analysis and 'timeout' in error_analysis.lower():
            recommendations.append("Increase wait times for page loading")
        
        if error_analysis and 'not found' in error_analysis.lower():
            recommendations.append("Verify element selectors and page structure")
        
        # Action-specific recommendations
        if 'click' in action and effectiveness < 0.5:
            recommendations.append("Ensure element is visible and clickable before clicking")
        
        if 'type' in action and effectiveness < 0.5:
            recommendations.append("Clear input field and verify it accepts text input")
        
        return recommendations
    
    def _suggest_improvements(self, action: str, effectiveness: float, 
                            confidence: float, error_analysis: Optional[str]) -> List[str]:
        """Suggest specific improvements for future similar actions."""
        improvements = []
        
        if effectiveness < 0.6:
            improvements.append("Add explicit waits before action execution")
            improvements.append("Verify element state before interaction")
        
        if confidence < 0.6:
            improvements.append("Implement better element detection strategies")
            improvements.append("Add fallback mechanisms for failed actions")
        
        if error_analysis:
            if 'element_not_found' in error_analysis:
                improvements.append("Implement dynamic element waiting")
                improvements.append("Use multiple selector strategies")
            elif 'timeout' in error_analysis:
                improvements.append("Optimize page load detection")
                improvements.append("Implement progressive timeout strategies")
        
        return improvements
    
    def _update_history(self, action: str, effectiveness: float, error_msg: Optional[str]):
        """Update historical performance data."""
        self.effectiveness_history[action].append(effectiveness)
        
        # Calculate rolling success rate
        recent_effectiveness = self.effectiveness_history[action][-10:]  # Last 10 attempts
        success_count = sum(1 for eff in recent_effectiveness if eff > 0.5)
        self.action_success_rates[action] = success_count / len(recent_effectiveness)
        
        logger.debug(f"Updated {action} success rate: {self.action_success_rates[action]:.2f}")
    
    # Helper methods for state analysis
    def _page_changed(self, before: Dict, after: Dict) -> bool:
        """Check if page changed significantly."""
        # Handle cases where before/after might be strings instead of dicts
        if not isinstance(before, dict):
            before = {'url': str(before) if before else '', 'elements': []}
        if not isinstance(after, dict):
            after = {'url': str(after) if after else '', 'elements': []}
            
        before_url = before.get('url', '')
        after_url = after.get('url', '')
        return before_url != after_url
    
    def _new_elements_appeared(self, before: Dict, after: Dict) -> bool:
        """Check if new elements appeared on the page."""
        # Handle cases where before/after might be strings instead of dicts
        if not isinstance(before, dict):
            before = {'url': str(before) if before else '', 'elements': []}
        if not isinstance(after, dict):
            after = {'url': str(after) if after else '', 'elements': []}
            
        before_elements = len(before.get('elements', []))
        after_elements = len(after.get('elements', []))
        return after_elements > before_elements
    
    def _form_data_accepted(self, before: Dict, after: Dict) -> bool:
        """Check if form data was accepted."""
        # Handle cases where before/after might be strings instead of dicts
        if not isinstance(before, dict):
            before = {'url': str(before) if before else '', 'elements': []}
        if not isinstance(after, dict):
            after = {'url': str(after) if after else '', 'elements': []}
            
        # Look for success indicators in page content
        after_text = after.get('text', '').lower()
        success_keywords = ['success', 'submitted', 'saved', 'confirmed', 'thank you']
        return any(keyword in after_text for keyword in success_keywords)
    
    def _goal_progress_made(self, before: Dict, after: Dict, action: str) -> bool:
        """Check if progress was made toward the goal."""
        # Handle cases where before/after might be strings instead of dicts
        if not isinstance(before, dict):
            before = {'url': str(before) if before else '', 'elements': []}
        if not isinstance(after, dict):
            after = {'url': str(after) if after else '', 'elements': []}
            
        # This is a simplified check - in practice, this would be more sophisticated
        after_text = after.get('text', '').lower()
        
        if 'click' in action:
            return any(indicator in after_text for indicators in self.success_indicators.values() 
                      for indicator in indicators)
        
        return False
    
    def _error_occurred(self, before: Dict, after: Dict) -> bool:
        """Check if an error occurred."""
        # Handle case where after might be a string instead of dict
        if isinstance(after, str):
            after = {'url': '', 'elements': [], 'text': after}
        
        after_text = after.get('text', '').lower()
        error_keywords = ['error', 'failed', 'invalid', 'incorrect', 'not found']
        return any(keyword in after_text for keyword in error_keywords)
    
    def _element_clearly_identified(self, action: str, state: Dict) -> bool:
        """Check if the target element was clearly identified."""
        # Look for specific selectors in the action
        return bool(re.search(r'(id=|class=|xpath=|css=)', action))
    
    def _input_field_available(self, action: str, state: Dict) -> bool:
        """Check if input field is available for typing."""
        # Handle case where state might be a string instead of dict
        if isinstance(state, str):
            state = {'url': '', 'elements': [], 'text': state}
        
        # Simplified check - would be more sophisticated in practice
        elements = state.get('elements', [])
        input_elements = [el for el in elements if 'input' in str(el).lower()]
        return len(input_elements) > 0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        total_actions = sum(len(history) for history in self.effectiveness_history.values())
        
        if total_actions == 0:
            return {'message': 'No actions evaluated yet'}
        
        avg_effectiveness = sum(
            sum(history) / len(history) for history in self.effectiveness_history.values()
        ) / len(self.effectiveness_history)
        
        return {
            'total_actions_evaluated': total_actions,
            'average_effectiveness': avg_effectiveness,
            'action_types_analyzed': len(self.effectiveness_history),
            'common_error_patterns': dict(self.error_patterns),
            'top_performing_actions': {
                action: rate for action, rate in 
                sorted(self.action_success_rates.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        }


# Test the self-critique system
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    print("Testing Self-Critique System...")
    
    critique_system = SelfCritiqueSystem()
    
    # Test successful action
    before_state = {'url': 'https://example.com', 'elements': ['button1', 'input1']}
    after_state = {'url': 'https://example.com/success', 'elements': ['button1', 'input1', 'success_msg']}
    
    critique = critique_system.evaluate_action_outcome(
        action="click(button[id='submit'])",
        before_state=before_state,
        after_state=after_state,
        execution_time=1.2
    )
    
    print(f"\n1. Successful Action Critique:")
    print(f"Action: {critique.action}")
    print(f"Effectiveness: {critique.effectiveness_score:.2f}")
    print(f"Confidence: {critique.confidence_score:.2f}")
    print(f"Reasoning: {critique.reasoning}")
    print(f"Recommendations: {critique.recommendations}")
    
    # Test failed action
    critique_failed = critique_system.evaluate_action_outcome(
        action="click(button[id='nonexistent'])",
        before_state=before_state,
        after_state=before_state,  # No change
        error_msg="Element not found: button[id='nonexistent']",
        execution_time=5.0
    )
    
    print(f"\n2. Failed Action Critique:")
    print(f"Action: {critique_failed.action}")
    print(f"Effectiveness: {critique_failed.effectiveness_score:.2f}")
    print(f"Confidence: {critique_failed.confidence_score:.2f}")
    print(f"Error Analysis: {critique_failed.error_analysis}")
    print(f"Alternatives: {critique_failed.alternative_actions}")
    print(f"Improvements: {critique_failed.improvement_suggestions}")
    
    # Test performance summary
    print(f"\n3. Performance Summary:")
    summary = critique_system.get_performance_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\nSelf-critique system test completed!")
#!/usr/bin/env python3
"""
Advanced Retry System for TrayBuilder Agent

This module implements a comprehensive retry system with four key features:
1. Adaptive Retry + Classify-&-Patch
2. State Rollback for Multi-Step Tasks
3. Self-Debug for Persistent Failures
4. Multi-Agent Retry for Non-Deterministic Tasks

Designed for AGI SDK/TrayBuilder web automation context.
"""

import json
import time
import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import copy
from datetime import datetime


class ErrorType(Enum):
    """Classification of error types for targeted retry strategies."""
    TIMEOUT = "timeout"
    DOM_MISSING = "dom_missing"
    ACTION_INCOMPLETE = "action_incomplete"
    NETWORK_ERROR = "network_error"
    ELEMENT_NOT_FOUND = "element_not_found"
    STALE_ELEMENT = "stale_element"
    PERMISSION_DENIED = "permission_denied"
    UNEXPECTED_ERROR = "unexpected_error"
    RATE_LIMITED = "rate_limited"
    PAGE_LOAD_ERROR = "page_load_error"


class RetryStrategy(Enum):
    """Available retry strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE = "immediate"
    ADAPTIVE = "adaptive"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0
    timeout_multiplier: float = 1.5
    enable_state_rollback: bool = True
    enable_self_debug: bool = True
    enable_multi_agent: bool = True
    debug_threshold: int = 2  # Trigger self-debug after N failures


@dataclass
class TaskState:
    """Represents a snapshot of task state for rollback purposes."""
    timestamp: str
    browser_state: Dict[str, Any]
    dom_snapshot: Optional[str] = None
    variables: Dict[str, Any] = None
    step_index: int = 0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskState':
        return cls(**data)


@dataclass
class FailureAnalysis:
    """Analysis of a failure for debugging purposes."""
    error_type: ErrorType
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    suggested_fix: str
    confidence: float
    timestamp: str


class ErrorClassifier:
    """Classifies errors into specific types for targeted retry strategies."""
    
    def __init__(self):
        self.classification_rules = {
            ErrorType.TIMEOUT: [
                "timeout", "timed out", "TimeoutError", "selenium.common.exceptions.TimeoutException"
            ],
            ErrorType.DOM_MISSING: [
                "element not found", "NoSuchElementException", "element is not attached"
            ],
            ErrorType.ACTION_INCOMPLETE: [
                "click intercepted", "element not interactable", "ElementNotInteractableException"
            ],
            ErrorType.NETWORK_ERROR: [
                "network", "connection", "ConnectionError", "requests.exceptions"
            ],
            ErrorType.ELEMENT_NOT_FOUND: [
                "NoSuchElementException", "element not found", "unable to locate element"
            ],
            ErrorType.STALE_ELEMENT: [
                "StaleElementReferenceException", "stale element", "element is no longer attached"
            ],
            ErrorType.RATE_LIMITED: [
                "rate limit", "429", "too many requests", "throttled"
            ],
            ErrorType.PAGE_LOAD_ERROR: [
                "page load", "navigation", "page not loaded", "WebDriverException"
            ]
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorType:
        """Classify an error into a specific error type."""
        error_str = str(error).lower()
        error_type_str = type(error).__name__.lower()
        
        for error_type, keywords in self.classification_rules.items():
            for keyword in keywords:
                if keyword.lower() in error_str or keyword.lower() in error_type_str:
                    return error_type
        
        return ErrorType.UNEXPECTED_ERROR


class RetryPatch:
    """Defines patches to apply based on error classification."""
    
    def __init__(self):
        self.patches = {
            ErrorType.TIMEOUT: self._patch_timeout,
            ErrorType.DOM_MISSING: self._patch_dom_missing,
            ErrorType.ACTION_INCOMPLETE: self._patch_action_incomplete,
            ErrorType.NETWORK_ERROR: self._patch_network_error,
            ErrorType.ELEMENT_NOT_FOUND: self._patch_element_not_found,
            ErrorType.STALE_ELEMENT: self._patch_stale_element,
            ErrorType.RATE_LIMITED: self._patch_rate_limited,
            ErrorType.PAGE_LOAD_ERROR: self._patch_page_load_error,
            ErrorType.UNEXPECTED_ERROR: self._patch_unexpected_error
        }
    
    def apply_patch(self, error_type: ErrorType, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Apply appropriate patch based on error type."""
        patch_func = self.patches.get(error_type, self._patch_unexpected_error)
        return patch_func(context, attempt)
    
    def _patch_timeout(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for timeout errors - increase timeouts and add waits."""
        multiplier = 1.5 ** attempt
        return {
            "timeout_multiplier": multiplier,
            "additional_wait": min(5 * attempt, 15),
            "retry_strategy": "exponential_backoff",
            "actions": ["refresh_page", "wait_for_stability"]
        }
    
    def _patch_dom_missing(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for DOM missing errors - refresh and re-query."""
        return {
            "actions": ["refresh_page", "wait_for_dom_ready", "scroll_to_element"],
            "additional_wait": 3 * attempt,
            "use_alternative_selectors": True
        }
    
    def _patch_action_incomplete(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for incomplete actions - scroll and ensure visibility."""
        return {
            "actions": ["scroll_to_element", "wait_for_clickable", "clear_overlays"],
            "use_javascript_click": True,
            "additional_wait": 2 * attempt
        }
    
    def _patch_network_error(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for network errors - exponential backoff."""
        return {
            "retry_strategy": "exponential_backoff",
            "base_delay": 5.0,
            "max_delay": 60.0,
            "actions": ["check_connectivity"]
        }
    
    def _patch_element_not_found(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for element not found - try alternative selectors."""
        return {
            "use_alternative_selectors": True,
            "actions": ["wait_for_dom_ready", "scroll_page"],
            "additional_wait": 2 * attempt
        }
    
    def _patch_stale_element(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for stale elements - re-find elements."""
        return {
            "actions": ["refresh_element_references", "wait_for_dom_ready"],
            "force_element_refind": True
        }
    
    def _patch_rate_limited(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for rate limiting - longer delays."""
        return {
            "retry_strategy": "exponential_backoff",
            "base_delay": 30.0,
            "max_delay": 300.0,
            "actions": ["rotate_user_agent"]
        }
    
    def _patch_page_load_error(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Patch for page load errors - reload and wait."""
        return {
            "actions": ["reload_page", "wait_for_page_load"],
            "additional_wait": 5 * attempt,
            "timeout_multiplier": 2.0
        }
    
    def _patch_unexpected_error(self, context: Dict[str, Any], attempt: int) -> Dict[str, Any]:
        """Default patch for unexpected errors."""
        return {
            "retry_strategy": "exponential_backoff",
            "additional_wait": 3 * attempt,
            "actions": ["take_screenshot", "log_page_source"]
        }


class StateManager:
    """Manages state snapshots for rollback functionality."""
    
    def __init__(self):
        self.states: List[TaskState] = []
        self.max_states = 10  # Keep last 10 states
    
    def save_state(self, browser_state: Dict[str, Any], description: str = "", 
                   variables: Dict[str, Any] = None) -> str:
        """Save current state and return state ID."""
        state = TaskState(
            timestamp=datetime.now().isoformat(),
            browser_state=copy.deepcopy(browser_state),
            variables=copy.deepcopy(variables) if variables else {},
            step_index=len(self.states),
            description=description
        )
        
        self.states.append(state)
        
        # Keep only the last max_states
        if len(self.states) > self.max_states:
            self.states = self.states[-self.max_states:]
        
        return state.timestamp
    
    def rollback_to_state(self, state_id: str = None) -> Optional[TaskState]:
        """Rollback to a specific state or the last saved state."""
        if not self.states:
            return None
        
        if state_id is None:
            # Return the last state
            return self.states[-1]
        
        # Find state by timestamp
        for state in reversed(self.states):
            if state.timestamp == state_id:
                return state
        
        return None
    
    def get_state_history(self) -> List[TaskState]:
        """Get all saved states."""
        return self.states.copy()
    
    def clear_states(self):
        """Clear all saved states."""
        self.states.clear()


class SelfDebugger:
    """Analyzes failures and provides debugging insights."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.failure_history: List[FailureAnalysis] = []
    
    def analyze_failure(self, error: Exception, context: Dict[str, Any], 
                       attempt_history: List[Dict[str, Any]]) -> FailureAnalysis:
        """Analyze a failure and provide debugging insights."""
        error_classifier = ErrorClassifier()
        error_type = error_classifier.classify_error(error, context)
        
        analysis = FailureAnalysis(
            error_type=error_type,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context=context,
            suggested_fix=self._generate_suggested_fix(error_type, context, attempt_history),
            confidence=self._calculate_confidence(error_type, attempt_history),
            timestamp=datetime.now().isoformat()
        )
        
        self.failure_history.append(analysis)
        return analysis
    
    def _generate_suggested_fix(self, error_type: ErrorType, context: Dict[str, Any], 
                               attempt_history: List[Dict[str, Any]]) -> str:
        """Generate a suggested fix based on error analysis."""
        suggestions = {
            ErrorType.TIMEOUT: "Increase timeout values and add stability waits",
            ErrorType.DOM_MISSING: "Refresh page and wait for DOM to be ready",
            ErrorType.ACTION_INCOMPLETE: "Scroll to element and ensure it's clickable",
            ErrorType.NETWORK_ERROR: "Check network connectivity and retry with backoff",
            ErrorType.ELEMENT_NOT_FOUND: "Use alternative selectors or wait longer",
            ErrorType.STALE_ELEMENT: "Re-find elements after page changes",
            ErrorType.RATE_LIMITED: "Implement longer delays between requests",
            ErrorType.PAGE_LOAD_ERROR: "Reload page and wait for complete load"
        }
        
        base_suggestion = suggestions.get(error_type, "Review error details and context")
        
        # Add context-specific suggestions
        if len(attempt_history) > 2:
            base_suggestion += ". Consider using alternative agent configuration."
        
        return base_suggestion
    
    def _calculate_confidence(self, error_type: ErrorType, attempt_history: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the analysis based on error patterns."""
        if error_type == ErrorType.UNEXPECTED_ERROR:
            return 0.3
        
        # Higher confidence for known error types
        base_confidence = 0.8
        
        # Reduce confidence if we've seen this error type repeatedly
        same_error_count = sum(1 for attempt in attempt_history 
                              if attempt.get('error_type') == error_type)
        
        if same_error_count > 2:
            base_confidence *= 0.7
        
        return min(base_confidence, 1.0)
    
    def generate_debug_report(self) -> str:
        """Generate a comprehensive debug report."""
        if not self.failure_history:
            return "No failures recorded."
        
        report = "=== Self-Debug Report ===\n\n"
        
        # Summary
        error_counts = {}
        for failure in self.failure_history:
            error_counts[failure.error_type] = error_counts.get(failure.error_type, 0) + 1
        
        report += "Error Summary:\n"
        for error_type, count in error_counts.items():
            report += f"  - {error_type.value}: {count} occurrences\n"
        
        # Recent failures
        report += "\nRecent Failures:\n"
        for failure in self.failure_history[-3:]:
            report += f"  - {failure.timestamp}: {failure.error_type.value}\n"
            report += f"    Message: {failure.error_message}\n"
            report += f"    Suggested Fix: {failure.suggested_fix}\n"
            report += f"    Confidence: {failure.confidence:.2f}\n\n"
        
        return report


class AgentInterface(ABC):
    """Abstract interface for different agent implementations."""
    
    @abstractmethod
    def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results."""
        pass
    
    @abstractmethod
    def get_agent_id(self) -> str:
        """Get unique identifier for this agent."""
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Get agent configuration details."""
        pass


class MultiAgentManager:
    """Manages multiple agent configurations for retry scenarios."""
    
    def __init__(self):
        self.agents: Dict[str, AgentInterface] = {}
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        self.current_agent_id: Optional[str] = None
    
    def register_agent(self, agent: AgentInterface):
        """Register an agent for multi-agent retry."""
        agent_id = agent.get_agent_id()
        self.agents[agent_id] = agent
        
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_execution_time": 0.0,
                "last_used": None
            }
    
    def get_next_agent(self, exclude_agents: List[str] = None) -> Optional[AgentInterface]:
        """Get the next best agent for retry, excluding failed agents."""
        exclude_agents = exclude_agents or []
        available_agents = {k: v for k, v in self.agents.items() if k not in exclude_agents}
        
        if not available_agents:
            return None
        
        # Select agent based on performance
        best_agent_id = self._select_best_agent(available_agents.keys())
        self.current_agent_id = best_agent_id
        return self.agents[best_agent_id]
    
    def _select_best_agent(self, available_agent_ids: List[str]) -> str:
        """Select the best performing agent."""
        if len(available_agent_ids) == 1:
            return list(available_agent_ids)[0]
        
        # Calculate success rate for each agent
        best_agent = None
        best_score = -1
        
        for agent_id in available_agent_ids:
            perf = self.agent_performance[agent_id]
            total_attempts = perf["success_count"] + perf["failure_count"]
            
            if total_attempts == 0:
                # New agent, give it a chance
                success_rate = 0.5
            else:
                success_rate = perf["success_count"] / total_attempts
            
            # Factor in recency (prefer recently successful agents)
            recency_bonus = 0.1 if perf["last_used"] else 0
            score = success_rate + recency_bonus
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent or list(available_agent_ids)[0]
    
    def record_agent_result(self, agent_id: str, success: bool, execution_time: float):
        """Record the result of an agent execution."""
        if agent_id not in self.agent_performance:
            return
        
        perf = self.agent_performance[agent_id]
        
        if success:
            perf["success_count"] += 1
        else:
            perf["failure_count"] += 1
        
        # Update average execution time
        total_attempts = perf["success_count"] + perf["failure_count"]
        perf["avg_execution_time"] = (
            (perf["avg_execution_time"] * (total_attempts - 1) + execution_time) / total_attempts
        )
        
        perf["last_used"] = datetime.now().isoformat()


class AdvancedRetrySystem:
    """Main retry system orchestrating all advanced retry features."""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.error_classifier = ErrorClassifier()
        self.retry_patch = RetryPatch()
        self.state_manager = StateManager()
        self.self_debugger = SelfDebugger()
        self.multi_agent_manager = MultiAgentManager()
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(self, task_func: Callable, task_args: tuple = (), 
                          task_kwargs: Dict[str, Any] = None, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task with advanced retry capabilities."""
        task_kwargs = task_kwargs or {}
        context = context or {}
        attempt_history = []
        failed_agents = []
        
        # Save initial state if rollback is enabled
        if self.config.enable_state_rollback:
            initial_state_id = self.state_manager.save_state(
                browser_state=context.get("browser_state", {}),
                description="Initial state before task execution",
                variables=context.get("variables", {})
            )
        
        for attempt in range(self.config.max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{self.config.max_attempts}")
                
                # Apply patches from previous failures
                if attempt_history:
                    last_failure = attempt_history[-1]
                    patch = self.retry_patch.apply_patch(
                        last_failure["error_type"], context, attempt
                    )
                    context.update(patch)
                
                # Execute the task
                start_time = time.time()
                
                if self.config.enable_multi_agent and attempt > 0:
                    # Try with alternative agent
                    agent = self.multi_agent_manager.get_next_agent(exclude_agents=failed_agents)
                    if agent:
                        result = agent.execute_task({"func": task_func, "args": task_args, "kwargs": task_kwargs}, context)
                        execution_time = time.time() - start_time
                        self.multi_agent_manager.record_agent_result(agent.get_agent_id(), True, execution_time)
                        return {"success": True, "result": result, "attempts": attempt + 1}
                
                # Execute with primary method
                result = task_func(*task_args, **task_kwargs)
                
                self.logger.info(f"Task succeeded on attempt {attempt + 1}")
                return {"success": True, "result": result, "attempts": attempt + 1}
                
            except Exception as error:
                execution_time = time.time() - start_time
                
                # Classify the error
                error_type = self.error_classifier.classify_error(error, context)
                
                # Record failure
                failure_info = {
                    "attempt": attempt + 1,
                    "error": str(error),
                    "error_type": error_type,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time
                }
                attempt_history.append(failure_info)
                
                # Record agent failure if using multi-agent
                if self.multi_agent_manager.current_agent_id:
                    self.multi_agent_manager.record_agent_result(
                        self.multi_agent_manager.current_agent_id, False, execution_time
                    )
                    failed_agents.append(self.multi_agent_manager.current_agent_id)
                
                self.logger.warning(f"Attempt {attempt + 1} failed: {error_type.value} - {error}")
                
                # Trigger self-debug if threshold reached
                if (self.config.enable_self_debug and 
                    len(attempt_history) >= self.config.debug_threshold):
                    analysis = self.self_debugger.analyze_failure(error, context, attempt_history)
                    self.logger.info(f"Self-debug analysis: {analysis.suggested_fix}")
                
                # Rollback state if enabled and not the last attempt
                if (self.config.enable_state_rollback and 
                    attempt < self.config.max_attempts - 1):
                    rollback_state = self.state_manager.rollback_to_state()
                    if rollback_state:
                        context["browser_state"] = rollback_state.browser_state
                        context["variables"] = rollback_state.variables
                        self.logger.info("Rolled back to previous state")
                
                # Calculate delay before next attempt
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, error_type)
                    self.logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
        
        # All attempts failed
        debug_report = self.self_debugger.generate_debug_report() if self.config.enable_self_debug else ""
        
        return {
            "success": False,
            "error": "All retry attempts failed",
            "attempts": self.config.max_attempts,
            "attempt_history": attempt_history,
            "debug_report": debug_report
        }
    
    def _calculate_delay(self, attempt: int, error_type: ErrorType) -> float:
        """Calculate delay before next retry attempt."""
        base_delay = self.config.base_delay
        
        # Adjust base delay based on error type
        error_multipliers = {
            ErrorType.RATE_LIMITED: 5.0,
            ErrorType.NETWORK_ERROR: 3.0,
            ErrorType.TIMEOUT: 2.0,
            ErrorType.PAGE_LOAD_ERROR: 2.0
        }
        
        base_delay *= error_multipliers.get(error_type, 1.0)
        
        # Apply exponential backoff
        delay = base_delay * (self.config.backoff_multiplier ** attempt)
        
        return min(delay, self.config.max_delay)
    
    def register_agent(self, agent: AgentInterface):
        """Register an agent for multi-agent retry."""
        self.multi_agent_manager.register_agent(agent)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all components."""
        return {
            "agent_performance": self.multi_agent_manager.agent_performance,
            "failure_history": [asdict(f) for f in self.self_debugger.failure_history],
            "state_history_count": len(self.state_manager.states)
        }


# Example Usage and Integration
if __name__ == "__main__":
    # Example of how to use the Advanced Retry System
    
    # Configure the retry system
    config = RetryConfig(
        max_attempts=5,
        base_delay=2.0,
        enable_state_rollback=True,
        enable_self_debug=True,
        enable_multi_agent=True
    )
    
    # Initialize the retry system
    retry_system = AdvancedRetrySystem(config)
    
    # Example task function (replace with your actual task)
    def example_web_task(url: str, action: str):
        """Example web automation task."""
        # This would contain your actual web automation logic
        # For demo purposes, we'll simulate different types of failures
        import random
        
        failure_types = [
            "TimeoutError: Page load timed out",
            "NoSuchElementException: Element not found",
            "ElementNotInteractableException: Element not clickable",
            None  # Success case
        ]
        
        failure = random.choice(failure_types)
        if failure:
            raise Exception(failure)
        
        return {"status": "success", "data": "Task completed"}
    
    # Execute task with retry
    context = {
        "browser_state": {"url": "https://example.com", "session_id": "abc123"},
        "variables": {"user_id": "user123"}
    }
    
    result = retry_system.execute_with_retry(
        task_func=example_web_task,
        task_args=("https://example.com", "click_button"),
        context=context
    )
    
    print("Execution Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Get performance statistics
    stats = retry_system.get_performance_stats()
    print("\nPerformance Statistics:")
    print(json.dumps(stats, indent=2, default=str))
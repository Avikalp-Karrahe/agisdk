#!/usr/bin/env python3
"""
Real Enhanced Agent - Simplified version based on demo agent insights
"""

import dataclasses
import json
import time
import re
import base64
import io
import os
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image

# Import LLM clients
from openai import OpenAI
from anthropic import Anthropic

# Import browsergym components
from agisdk.REAL.browsergym.experiments import Agent, AbstractAgentArgs
from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str, prune_html

# Import enhanced systems
from memory_systems import EpisodicMemory, WorkingMemory, StateHasher
from self_critique import SelfCritiqueSystem
from planning_system import HierarchicalPlanner
from advanced_retry_system import AdvancedRetrySystem, RetryConfig

@dataclasses.dataclass
class RealEnhancedAgentArgs(AbstractAgentArgs):
    """Arguments for the Real Enhanced Agent"""
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
        return RealEnhancedAgent(self)


class RealEnhancedAgent(Agent):
    """Enhanced agent with simplified action generation based on demo agent insights"""
    
    def __init__(self, args: RealEnhancedAgentArgs):
        super().__init__()
        self.args = args
        self.model_name = args.model_name
        self.enhanced_selection = args.enhanced_selection
        self.timeout_ms = args.timeout_ms
        self.retry_attempts = args.retry_attempts
        self.simulate_execution = args.simulate_execution
        self.use_html = args.use_html
        self.use_axtree = args.use_axtree
        self.use_screenshot = args.use_screenshot
        self.max_steps = args.max_steps
        
        self.action_set = HighLevelActionSet(
            subsets=["chat", "bid"],
            strict=False,
            multiaction=False,
            demo_mode="off"
        )
        
        # Initialize enhanced systems
        self.episodic_memory = EpisodicMemory()
        self.working_memory = WorkingMemory()
        self.state_hasher = StateHasher()
        self.self_critique = SelfCritiqueSystem()
        self.planner = HierarchicalPlanner()
        self.retry_system = AdvancedRetrySystem(RetryConfig())
        
        # Action tracking
        self.action_history = []
        self.last_observation = None
        self.step_count = 0
        
        # Context tracking (simplified and consistent)
        self.last_fill = None
        self.last_press = None
        self.context_cache = {}
        self.last_context_refresh = 0
        
        # Initialize LLM client based on model name
        self._initialize_llm_client()
        
        print(f"Initialized {self.args.agent_name} with model {self.args.model_name}")

    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client based on model name"""
        model_name = self.model_name
        
    def _initialize_llm_client(self):
        """Initialize the appropriate LLM client based on model name"""
        model_name = self.model_name
        
        # Force mock for testing - can be controlled via environment variable
        use_mock = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
        
        # For testing, use a mock query_model if no API keys are available OR if forced
        if use_mock or (not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY")):
            # Mock LLM for testing - with state tracking for natural progression
            # Reset mock state for each new agent instance
            mock_state = {'last_action': None, 'fill_count': 0}
            
            def query_model(system_msgs, user_msgs):
                # Mock response for testing - return a simple click action
                print(f"[MOCK LLM] System: {system_msgs[0][:200]}...")
                print(f"[MOCK LLM] User: {user_msgs[0][:500]}...")
                
                user_lower = user_msgs[0].lower()
                
                # Extract available elements from user message
                import json
                import re
                
                # Look for available elements in the user message - try broader pattern
                elements_match = re.search(r'Available Elements:\s*(\{[^}]*\})', user_msgs[0], re.DOTALL)
                if not elements_match:
                    # Also try the JSON key format
                    elements_match = re.search(r'"available_elements":\s*(\{.*?\})', user_msgs[0], re.DOTALL)
                if elements_match:
                    try:
                        elements_str = elements_match.group(1)
                        print(f"[MOCK LLM] Found elements section: {elements_str[:300]}...")
                        
                        # Simple parsing to find button and input elements
                        button_match = re.search(r'"button_items":\s*\[([^\]]*)\]', elements_str)
                        input_match = re.search(r'"input_items":\s*\[([^\]]*)\]', elements_str)
                        
                        if "search" in user_lower or "laptop" in user_lower:
                            # Check if we've already filled an input - if so, look for buttons or press Enter
                            if mock_state['fill_count'] > 0:
                                # First try to find a button
                                if button_match and button_match.group(1):
                                    button_content = button_match.group(1)
                                    print(f"[MOCK LLM] Button content: {button_content}")
                                    id_match = re.search(r'"([^"]*)"', button_content)
                                    if id_match:
                                        button_id = id_match.group(1)
                                        print(f"[MOCK LLM] Found button element after fill: {button_id} - returning click action")
                                        mock_state['last_action'] = 'click'
                                        return f'click("{button_id}")'
                                
                                # If no button found, try pressing Enter on the input field
                                if input_match and input_match.group(1):
                                    input_content = input_match.group(1)
                                    id_match = re.search(r'"([^"]*)"', input_content)
                                    if id_match:
                                        input_id = id_match.group(1)
                                        print(f"[MOCK LLM] No button found, pressing Enter on input: {input_id}")
                                        mock_state['last_action'] = 'press'
                                        return f'press("{input_id}", "Enter")'
                            
                            # Try to find a search input first
                            if input_match and input_match.group(1):
                                # Extract first input element ID
                                input_content = input_match.group(1)
                                print(f"[MOCK LLM] Input content: {input_content}")
                                id_match = re.search(r'"([^"]*)"', input_content)
                                if id_match:
                                    input_id = id_match.group(1)
                                    print(f"[MOCK LLM] Found input element: {input_id} - returning fill action")
                                    mock_state['last_action'] = 'fill'
                                    mock_state['fill_count'] += 1
                                    return f'fill("{input_id}", "laptop")'
                            
                            # Otherwise try to find a button
                            if button_match and button_match.group(1):
                                button_content = button_match.group(1)
                                print(f"[MOCK LLM] Button content: {button_content}")
                                id_match = re.search(r'"([^"]*)"', button_content)
                                if id_match:
                                    button_id = id_match.group(1)
                                    print(f"[MOCK LLM] Found button element: {button_id} - returning click action")
                                    mock_state['last_action'] = 'click'
                                    return f'click("{button_id}")'
                    except Exception as e:
                        print(f"[MOCK LLM] Error parsing elements: {e}")
                else:
                    print("[MOCK LLM] No available_elements section found in user message")
                
                print("[MOCK LLM] No suitable elements found - returning noop")
                return 'noop()'
            
            self._mock_state = mock_state
            self.query_model = query_model
            return
        
        if model_name.startswith("gpt-") or model_name.startswith("o1") or model_name.startswith("o3"):
            # Use OpenAI models
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                # Fallback to mock for testing
                def query_model(system_msgs, user_msgs):
                    return 'noop()'
                self.query_model = query_model
                return
                
            self.client = OpenAI(api_key=api_key)
            
            def query_model(system_msgs, user_msgs):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_msgs},
                        {"role": "user", "content": user_msgs},
                    ],
                )
                return response.choices[0].message.content
            self.query_model = query_model
            
        elif any(model_name.startswith(prefix) for prefix in ["claude-", "sonnet-"]):
            # Anthropic model mapping
            ANTHROPIC_MODELS = {
                "claude-3-opus": "claude-3-opus-20240229",
                "claude-3-sonnet": "claude-3-sonnet-20240229",
                "claude-3-haiku": "claude-3-haiku-20240307",
                "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
                "claude-opus-4": "claude-opus-4-20250514",
                "claude-sonnet-4": "claude-sonnet-4-20250514",
                "sonnet-3.7": "claude-3-7-sonnet-20250219"
            }
            
            # Get the actual model ID
            if model_name in ANTHROPIC_MODELS:
                self.model_name = ANTHROPIC_MODELS[model_name]
            
            # Initialize Anthropic client
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                # Fallback to mock for testing
                def query_model(system_msgs, user_msgs):
                    return 'noop()'
                self.query_model = query_model
                return
                
            self.client = Anthropic(api_key=api_key)
            
            def query_model(system_msgs, user_msgs):
                # Convert to Anthropic format
                anthropic_content = []
                for msg in user_msgs:
                    if isinstance(msg, dict) and msg.get("type") == "text":
                        anthropic_content.append({"type": "text", "text": msg["text"]})
                    elif isinstance(msg, str):
                        anthropic_content.append({"type": "text", "text": msg})
                
                # Handle system message
                system_content = ""
                if isinstance(system_msgs, list) and system_msgs:
                    if isinstance(system_msgs[0], dict):
                        system_content = system_msgs[0].get("text", "")
                    else:
                        system_content = str(system_msgs[0])
                elif isinstance(system_msgs, str):
                    system_content = system_msgs
                
                messages = [{"role": "user", "content": anthropic_content}]
                
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=8000,
                    system=system_content,
                    messages=messages,
                )
                return response.content[0].text
            self.query_model = query_model
            
        else:
            # Fallback for unknown models
            def query_model(system_msgs, user_msgs):
                return 'noop()'
            self.query_model = query_model

    def obs_preprocessor(self, obs: dict) -> dict:
        """Preprocess observations to extract relevant information"""
        from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str, prune_html
        
        print(f"DEBUG: obs_preprocessor called with keys: {list(obs.keys())}")
        
        # Process DOM content using the same approach as demo agent
        html_content = ''
        if 'dom_object' in obs and obs['dom_object'] is not None:
            try:
                html_content = prune_html(flatten_dom_to_str(obs['dom_object']))
                print(f"DEBUG: Processed DOM content length: {len(html_content)}")
            except Exception as e:
                print(f"DEBUG: Error processing DOM: {e}")
                html_content = ''
        
        # Process AXTree content using the same approach as demo agent
        axtree_content = ''
        if 'axtree_object' in obs and obs['axtree_object'] is not None:
            try:
                axtree_content = flatten_axtree_to_str(obs['axtree_object'])
                print(f"DEBUG: Processed AXTree content length: {len(axtree_content)}")
            except Exception as e:
                print(f"DEBUG: Error processing AXTree: {e}")
                axtree_content = ''
        
        if len(html_content) == 0 and len(axtree_content) == 0:
            print("DEBUG: No HTML or AXTree content - using empty elements")
            processed = {'elements': {}}
        else:
            elements = self._analyze_page_elements(html_content, axtree_content)
            processed = {'elements': elements}
            print(f"DEBUG: Processed elements: {elements}")
        
        return {
            'html': html_content,
            'axtree': axtree_content,
            'elements': processed['elements'],
            'goal': self._extract_goal_safely(obs),
            'screenshot': obs.get('screenshot'),
            'goal_object': obs.get('goal_object'),
            'last_action': obs.get('last_action'),
            'last_action_error': obs.get('last_action_error'),
            'chat_messages': obs.get('chat_messages', [])
        }

    def get_action(self, obs: dict) -> tuple[str, dict]:
        """Main action generation method - simplified based on demo agent insights"""
        try:
            self.step_count += 1
            
            # The framework already calls obs_preprocessor, so obs is already processed
            # Check if obs is already processed (has 'elements' key) or raw (has 'dom_object' key)
            if 'elements' in obs:
                # Already processed by framework
                processed_obs = obs
            else:
                # Raw observation, need to process
                processed_obs = self.obs_preprocessor(obs)
            
            # Extract key information
            goal = processed_obs['goal']
            elements = processed_obs['elements']
            last_error = processed_obs.get('last_action_error', '')
            screenshot = processed_obs.get('screenshot')
            
            # Analyze goal to understand intent
            goal_analysis = self._analyze_goal(goal)
            
            # Generate action using simplified LLM-centric approach
            action = self._generate_contextual_action(
                goal_analysis, elements, last_error, screenshot
            )
            
            # Update tracking
            self._update_action_tracking(action, processed_obs)
            
            # Create metadata
            metadata = {
                'step': self.step_count,
                'goal_analysis': goal_analysis,
                'elements_found': len(elements.get('button_items', [])) + len(elements.get('link_items', [])),
                'action_type': self._get_action_type(action)
            }
            
            return action, metadata
            
        except Exception as e:
            print(f"Error in get_action: {e}")
            return 'noop()', {'error': str(e)}

    def _generate_contextual_action(self, goal_analysis: dict, elements: dict, last_error: str, screenshot: np.ndarray = None) -> str:
        """Simplified action generation based on demo agent insights"""
        
        # Prepare comprehensive context for LLM
        context_info = {
            'goal': goal_analysis.get('goal', ''),
            'intent': goal_analysis.get('intent', 'general'),
            'target_item': goal_analysis.get('target_item', ''),
            'available_elements': elements,
            'action_space_description': self._get_action_space_description(),
            'action_history': self.action_history[-5:] if self.action_history else [],
            'last_error': last_error,
            'visual_recommendations': self._get_visual_recommendations(screenshot, elements) if screenshot is not None else None,
            'last_fill': self.last_fill,
            'last_press': self.last_press
        }
        
        # Check for intelligent action sequencing (fill -> press Enter)
        if self._should_sequence_actions(context_info):
            return self._get_sequence_action(context_info)
        
        # Use LLM to generate action
        return self._query_llm_for_action(context_info)

    def _query_llm_for_action(self, context_info: dict) -> str:
        """Query LLM for action decision - simplified approach like demo agent"""
        
        # Construct system message
        system_msgs = [
            "You are a web automation agent. Analyze the context and choose the best action.",
            "Focus on the goal and available elements. Be direct and decisive.",
            "Use the action format: action_type(\"element_id\", \"value\") or action_type(\"element_id\")"
        ]
        
        # Construct user message with all context
        user_msgs = [
            f"Goal: {context_info['goal']}",
            f"Intent: {context_info['intent']}",
            f"Target Item: {context_info['target_item']}",
            f"Available Elements: {json.dumps(context_info['available_elements'], indent=2)}",
            f"Action Space: {context_info['action_space_description']}",
            f"Recent Actions: {context_info['action_history']}",
            f"Last Error: {context_info['last_error']}",
        ]
        
        if context_info['visual_recommendations']:
            user_msgs.append(f"Visual Analysis: {context_info['visual_recommendations']}")
        
        user_msgs.append("What is the next action?")
        
        # Query LLM using the initialized client
        try:
            # Convert to string format for the query_model method
            system_text = "\n".join(system_msgs)
            user_text = "\n".join(user_msgs)
            
            response = self.query_model(system_text, user_text)
            return self._parse_action_from_response(response)
        except Exception as e:
            print(f"LLM query failed: {e}")
            return self._fallback_action(context_info['available_elements'])

    def _direct_llm_query(self, system_msgs: list, user_msgs: list) -> str:
        """Direct LLM query as fallback when query_model is not available."""
        # This is a simplified fallback - in practice, you'd use the actual API
        # For now, return a basic action
        return 'noop()'

    def _fallback_action(self, elements: dict) -> str:
        """Fallback action when LLM query fails"""
        # Simple heuristic-based action selection
        if elements.get('button_items'):
            return f'click("{elements["button_items"][0][0]}")'
        elif elements.get('link_items'):
            return f'click("{elements["link_items"][0][0]}")'
        elif elements.get('input_items'):
            return f'fill("{elements["input_items"][0][0]}", "test")'
        else:
            return 'noop()'

    def _should_sequence_actions(self, context_info: dict) -> bool:
        """Determine if we should use intelligent action sequencing"""
        last_fill = context_info.get('last_fill')
        target_item = context_info.get('target_item', '')
        intent = context_info.get('intent', '')
        
        # If we just filled a search box with the target item, we should press Enter
        if (last_fill and target_item and intent == 'search' and 
            target_item.lower() in last_fill.get('value', '').lower()):
            
            # Check if we haven't already pressed Enter on this fill
            recent_actions = [action.get('action', '') for action in context_info.get('action_history', [])]
            last_press_action = None
            for action in reversed(recent_actions):
                if action.startswith('press('):
                    last_press_action = action
                    break
            
            # If the last press wasn't on the same element we just filled, sequence the action
            if not last_press_action or last_fill['bid'] not in last_press_action:
                return True
        
        return False

    def _get_sequence_action(self, context_info: dict) -> str:
        """Get the next action in an intelligent sequence"""
        last_fill = context_info.get('last_fill')
        
        if last_fill:
            # Press Enter on the element we just filled
            return f'press("{last_fill["bid"]}", "Enter")'
        
        return 'noop()'

    def _refresh_context_after_action(self, obs: dict, action: str, success: bool) -> dict:
        """Refresh context after action execution to enable smarter subsequent actions"""
        current_time = time.time()
        
        # Only refresh if enough time has passed or action was successful
        if current_time - self.last_context_refresh < 1.0 and not success:
            return self.context_cache.get('last_refresh', {})
        
        # Extract fresh DOM and AXTree data
        dom_text = obs.get('dom_txt', '')
        axtree_text = obs.get('axtree_txt', '')
        
        # Analyze refreshed page elements
        refreshed_elements = self._analyze_page_elements(dom_text, axtree_text)
        
        # Update context cache with fresh data
        refreshed_context = {
            'timestamp': current_time,
            'elements': refreshed_elements,
            'dom_text': dom_text,
            'axtree_text': axtree_text,
            'last_action': action,
            'action_success': success
        }
        
        # Store in context cache
        self.context_cache['current_refresh'] = refreshed_context
        self.last_context_refresh = current_time
        
        return refreshed_context

    def _parse_action_from_response(self, response: str) -> str:
        """Parse action from LLM response"""
        # Extract action from response (simplified)
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if any(action in line for action in ['click(', 'fill(', 'press(', 'scroll(', 'wait(', 'noop(']):
                return line
        
        # If no valid action found, return wait
        return 'noop()'

    def _get_action_space_description(self) -> str:
        """Get description of available actions"""
        return """
Available actions:
- click("element_id"): Click on an element
- fill("element_id", "text"): Fill an input field with text
- press("element_id", "key"): Press a key on an element (e.g., "Enter", "Tab")
- scroll(x, y): Scroll the page
- noop(): Wait for page to load
- noop(ms): Wait for specified milliseconds
"""

    def _get_visual_recommendations(self, screenshot: np.ndarray, elements: dict) -> str:
        """Get visual analysis recommendations (simplified)"""
        if screenshot is None:
            return "No screenshot available"
        
        # Simplified visual analysis
        return "Visual analysis: Page appears loaded and ready for interaction"

    def _analyze_goal(self, goal: str) -> dict:
        """Analyze goal to extract intent and target item"""
        goal_lower = goal.lower()
        
        # Determine intent
        intent = 'general'
        if any(word in goal_lower for word in ['search', 'find', 'look for']):
            intent = 'search'
        elif any(word in goal_lower for word in ['buy', 'purchase', 'add to cart']):
            intent = 'purchase'
        elif any(word in goal_lower for word in ['click', 'press', 'select']):
            intent = 'click'
        elif any(word in goal_lower for word in ['fill', 'enter', 'type']):
            intent = 'form_fill'
        elif any(word in goal_lower for word in ['navigate', 'go to', 'visit']):
            intent = 'navigate'
        
        # Extract target item (simplified)
        target_item = ''
        words = goal.split()
        for i, word in enumerate(words):
            if word.lower() in ['for', 'find', 'search', 'buy', 'purchase']:
                if i + 1 < len(words):
                    target_item = ' '.join(words[i+1:])
                    break
        
        return {
            'goal': goal,
            'intent': intent,
            'target_item': target_item.strip('"\'')
        }

    def _analyze_page_elements(self, dom_text: str, axtree_text: str) -> dict:
        """Analyze page elements to extract actionable items"""
        elements = {
            'button_items': self._find_button_items(dom_text, axtree_text),
            'link_items': self._find_link_items(dom_text, axtree_text),
            'input_items': self._find_input_items(dom_text, axtree_text),
            'search_inputs': self._find_search_input_bids(dom_text, axtree_text)
        }
        return elements

    def _find_button_items(self, html_content: str, axtree_content: str) -> List[Tuple[str, str]]:
        """Find button elements with their labels"""
        button_items = []
        
        # Extract from HTML - look for buttons with bid attributes
        button_pattern = r'<button[^>]*bid="([^"]*)"[^>]*>([^<]*)</button>'
        for match in re.finditer(button_pattern, html_content, re.IGNORECASE):
            bid = match.group(1)
            label = match.group(2).strip()
            if bid and label:
                button_items.append((bid, label))
        
        # Also look for input type="button" or type="submit"
        input_button_pattern = r'<input[^>]*type="(?:button|submit)"[^>]*bid="([^"]*)"[^>]*value="([^"]*)"'
        for match in re.finditer(input_button_pattern, html_content, re.IGNORECASE):
            bid = match.group(1)
            label = match.group(2).strip()
            if bid and label:
                button_items.append((bid, label))
        
        # Extract from accessibility tree - look for button role elements
        button_ax_pattern = r'button\s+"([^"]*)".*?bid="([^"]*)"'
        for match in re.finditer(button_ax_pattern, axtree_content, re.IGNORECASE):
            label = match.group(1).strip()
            bid = match.group(2)
            if bid and label and (bid, label) not in button_items:
                button_items.append((bid, label))
        
        print(f"DEBUG: Found {len(button_items)} button items: {button_items[:5]}")  # Show first 5
        return button_items

    def _find_link_items(self, html_content: str, axtree_content: str) -> List[Tuple[str, str]]:
        """Find link elements with their labels"""
        link_items = []
        
        # Extract from HTML
        link_pattern = r'<a[^>]*bid="([^"]*)"[^>]*>([^<]*)</a>'
        for match in re.finditer(link_pattern, html_content, re.IGNORECASE):
            bid = match.group(1)
            label = match.group(2).strip()
            if bid and label:
                link_items.append((bid, label))
        
        # Extract from accessibility tree
        link_ax_pattern = r'link\s+"([^"]*)".*?bid="([^"]*)"'
        for match in re.finditer(link_ax_pattern, axtree_content, re.IGNORECASE):
            label = match.group(1).strip()
            bid = match.group(2)
            if bid and label:
                link_items.append((bid, label))
        
        return link_items

    def _find_input_items(self, html_content: str, axtree_content: str) -> List[Tuple[str, str]]:
        """Find input elements with their labels"""
        input_items = []
        
        # Extract from HTML - improved pattern to capture more attributes
        input_pattern = r'<input[^>]*bid="([^"]*)"[^>]*(?:placeholder="([^"]*)")?[^>]*(?:type="([^"]*)")?[^>]*(?:value="([^"]*)")?'
        for match in re.finditer(input_pattern, html_content, re.IGNORECASE):
            bid = match.group(1)
            placeholder = match.group(2) or ''
            input_type = match.group(3) or 'text'
            value = match.group(4) or ''
            label = placeholder or value or input_type
            if bid:
                input_items.append((bid, label))
        
        # Extract from accessibility tree
        input_ax_pattern = r'textbox\s+"([^"]*)".*?bid="([^"]*)"'
        for match in re.finditer(input_ax_pattern, axtree_content, re.IGNORECASE):
            label = match.group(1).strip()
            bid = match.group(2)
            if bid and (bid, label) not in input_items:
                input_items.append((bid, label))
        
        print(f"DEBUG: Found {len(input_items)} input items: {input_items[:5]}")  # Show first 5
        return input_items

    def _find_search_input_bids(self, html_content: str, axtree_content: str) -> List[str]:
        """Find search input elements"""
        search_bids = []
        
        # Look for inputs with search-related attributes
        search_patterns = [
            r'<input[^>]*(?:name|id|class|placeholder)="[^"]*search[^"]*"[^>]*bid="([^"]*)"',
            r'<input[^>]*bid="([^"]*)"[^>]*(?:name|id|class|placeholder)="[^"]*search[^"]*"'
        ]
        
        for pattern in search_patterns:
            for match in re.finditer(pattern, html_content, re.IGNORECASE):
                bid = match.group(1)
                if bid:
                    search_bids.append(bid)
        
        return search_bids

    def _update_action_tracking(self, action: str, obs: dict):
        """Update action tracking information"""
        action_info = {
            'action': action,
            'timestamp': time.time(),
            'step': self.step_count
        }
        
        self.action_history.append(action_info)
        
        # Track specific action types for intelligent sequencing
        if action.startswith('fill('):
            fill_match = re.search(r'fill\("([^"]+)",\s*"([^"]*)"', action)
            if fill_match:
                self.last_fill = {
                    'bid': fill_match.group(1),
                    'value': fill_match.group(2),
                    'timestamp': time.time()
                }
        
        elif action.startswith('press('):
            press_match = re.search(r'press\("([^"]+)",\s*"([^"]*)"', action)
            if press_match:
                self.last_press = {
                    'bid': press_match.group(1),
                    'key': press_match.group(2),
                    'timestamp': time.time()
                }
        
        # Note: Context refresh removed to prevent double processing of obs_preprocessor

    def _get_action_type(self, action: str) -> str:
        """Get the type of action"""
        if action.startswith('click('):
            return 'click'
        elif action.startswith('fill('):
            return 'fill'
        elif action.startswith('press('):
            return 'press'
        elif action.startswith('scroll('):
            return 'scroll'
        elif action.startswith('wait('):
            return 'wait'
        elif action.startswith('noop('):
            return 'noop'
        else:
            return 'unknown'

    def _extract_goal_safely(self, obs: dict) -> str:
        """Safely extract goal from observation"""
        try:
            if 'goal_object' in obs and obs['goal_object']:
                if isinstance(obs['goal_object'], dict):
                    return obs['goal_object'].get('utterance', '')
                else:
                    return str(obs['goal_object'])
            elif 'goal' in obs:
                return str(obs['goal'])
            else:
                return ''
        except Exception as e:
            print(f"Error extracting goal: {e}")
            return ''

    def update_last_observation(self, obs):
        """Update the last observation"""
        self.last_observation = obs

    def close(self):
        """Clean up resources"""
        print(f"Closing {self.args.agent_name}")
        if hasattr(self, 'episodic_memory'):
            self.episodic_memory.close()
        if hasattr(self, 'working_memory'):
            self.working_memory.close()


def make_agent(args: RealEnhancedAgentArgs) -> RealEnhancedAgent:
    """Factory function to create agent"""
    return RealEnhancedAgent(args)


if __name__ == "__main__":
    # Test the agent
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
    
    # Test with sample observation
    test_obs = {
        'chat_messages': [],
        'screenshot': None,
        'goal_object': {'utterance': 'Search for laptops'},
        'last_action': '',
        'last_action_error': ''
    }
    
    action, metadata = agent.get_action(test_obs)
    print(f"Generated action: {action}")
    print(f"Metadata: {metadata}")
    
    agent.close()
#!/bin/bash

cat > enhanced_demo_agent.py << 'ENDFILE'
import base64
import dataclasses
import numpy as np
import io
import logging
import json
import time
import hashlib
import re
from datetime import datetime
from typing import Literal, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

from PIL import Image

from agisdk.REAL.browsergym.experiments import Agent, AbstractAgentArgs
from agisdk.REAL.browsergym.core.action.highlevel import HighLevelActionSet
from agisdk.REAL.browsergym.core.action.python import PythonActionSet
from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str, prune_html

logger = logging.getLogger(__name__)

@dataclass
class ProductInfo:
    """Information about a product being researched"""
    name: str
    price: Optional[str] = None
    specifications: Dict[str, str] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    url: Optional[str] = None
    research_complete: bool = False

@dataclass
class ComparisonAnalysis:
    """Analysis comparing multiple products"""
    products: List[ProductInfo] = field(default_factory=list)
    comparison_matrix: Dict[str, Dict[str, str]] = field(default_factory=dict)
    value_analysis: Dict[str, str] = field(default_factory=dict)
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None

@dataclass
class StepInfo:
    """Information about a single step in the agent's execution"""
    step_number: int
    timestamp: str
    action: str
    action_type: str
    action_args: str
    reasoning: str
    goal_snippet: str
    page_state_summary: str
    error_message: Optional[str] = None
    success_indicators: List[str] = field(default_factory=list)
    completion_signals: List[str] = field(default_factory=list)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)

class EnhancedDemoAgent(Agent):
    """Enhanced demo agent with structured analysis and product comparison capabilities"""
    
    def __init__(
        self,
        model_name: str, 
        chat_mode: bool = False,
        demo_mode: str = "off",
        use_html: bool = False,
        use_axtree: bool = True,
        use_screenshot: bool = True,  # Changed default to True to make screenshots mandatory
        system_message_handling: Literal["separate", "combined"] = "separate",
        thinking_budget: int = 10000,
        openai_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        openrouter_site_url: Optional[str] = None,
        openrouter_site_name: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.model_name = model_name
        self.chat_mode = chat_mode
        self.demo_mode = demo_mode
        self.use_html = use_html
        self.use_axtree = use_axtree
        self.use_screenshot = True  # Always use screenshots regardless of parameter
        self.system_message_handling = system_message_handling
        self.thinking_budget = thinking_budget
        self.openai_api_key = openai_api_key
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_site_url = openrouter_site_url
        self.openrouter_site_name = openrouter_site_name
        self.anthropic_api_key = anthropic_api_key
        
        # Initialize tracking attributes
        self.step_history: List[StepInfo] = []
        self.goal_text: str = ""
        self.step_count = 0
        self.last_action = ""
        self.last_reasoning = ""
        
        # Product research and comparison attributes
        self.products_to_research: List[str] = []
        self.researched_products: List[ProductInfo] = []
        self.comparison_analysis: Optional[ComparisonAnalysis] = None
        self.research_phase: str = "initial"  # initial, researching, comparing, deciding, purchasing
        
        # Page state tracking
        self.last_page_hash: str = ""
        self.repeated_state_count: int = 0
        self.no_progress_count: int = 0
        
        # Page exploration journey tracking
        self.page_journey: List[Dict[str, Any]] = []  # Stores visited pages with URL, page type, and outcomes
        self.visited_urls: Dict[str, int] = {}  # Tracks frequency of URL visits
        self.page_outcomes: Dict[str, List[str]] = {}  # Maps URLs to action outcomes
        
        # Set up action space
        self.action_set = HighLevelActionSet(
            subsets=["chat", "bid"],
            strict=False,
            multiaction=True,
            demo_mode=self.demo_mode,
        )
        
        # Initialize LLM client
        self._init_llm_client()
        
    def _init_llm_client(self):
        """Initialize the LLM client based on model name"""
        import os
        
        if self.model_name.startswith("gpt"):
            from openai import OpenAI
            # Use provided API key or get from environment
            api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass openai_api_key parameter.")
            self.client = OpenAI(api_key=api_key)
        elif self.model_name.startswith("claude"):
            import anthropic
            # Use provided API key or get from environment
            api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass anthropic_api_key parameter.")
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            from openai import OpenAI
            # Use provided API key or get from environment
            api_key = self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass openrouter_api_key parameter.")
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )

    def obs_preprocessor(self, obs: dict) -> dict:
        """Preprocess observations to extract relevant information"""
        # Always try to get both AXTree and HTML content
        axtree_txt = ""
        if self.use_axtree and obs.get("axtree") is not None:
            try:
                axtree_txt = flatten_axtree_to_str(obs.get("axtree", {}))
            except Exception as e:
                logger.warning(f"Error extracting AXTree text: {e}")
        
        pruned_html = ""
        # Always try to get HTML content as fallback, even if use_html is False
        if obs.get("dom_txt"):
            try:
                pruned_html = prune_html(obs.get("dom_txt", ""))
            except Exception as e:
                logger.warning(f"Error extracting HTML text: {e}")
        
        # Track page state
        page_text = self.get_page_text({"axtree_txt": axtree_txt, "pruned_html": pruned_html})
        if page_text:
            # Create a hash of the first 1000 chars to track state changes
            current_hash = hashlib.md5(page_text[:1000].encode()).hexdigest()
            if current_hash == self.last_page_hash:
                self.repeated_state_count += 1
            else:
                self.repeated_state_count = 0
                self.last_page_hash = current_hash
        
        return {
            "url": obs.get("url", ""),
            "axtree_txt": axtree_txt,
            "pruned_html": pruned_html,
            "screenshot": obs.get("screenshot") if self.use_screenshot else None,
            "page_hash": self.last_page_hash,
            "repeated_state_count": self.repeated_state_count
        }

    def get_page_text(self, obs: dict) -> str:
        """Get the best available page text from the observation"""
        # First try AXTree text if available
        if obs.get("axtree_txt"):
            return obs.get("axtree_txt")
        # Fall back to HTML if AXTree is not available
        elif obs.get("pruned_html"):
            return obs.get("pruned_html")
        # Return empty string if neither is available
        return ""

    def detect_goal_completion(self, obs: dict, action: str) -> tuple[bool, List[str]]:
        """Detect if the goal has been completed"""
        page_text = self.get_page_text(obs).lower()
        url = obs.get("url", "").lower()
        
        completion_signals = []
        
        # Check for purchase completion indicators
        purchase_indicators = [
            "order confirmed", "purchase successful", "thank you for your order",
            "order placed", "payment successful", "confirmation number",
            "order summary", "receipt", "your order has been placed"
        ]
        
        for indicator in purchase_indicators:
            if indicator in page_text:
                completion_signals.append(f"Purchase indicator found: {indicator}")
        
        # Check for cart/checkout progression
        if "cart" in url or "checkout" in url:
            completion_signals.append("In checkout/cart process")
            
        # Check for product comparison completion
        if self.research_phase == "deciding" and self.comparison_analysis:
            if self.comparison_analysis.recommendation:
                completion_signals.append("Product comparison completed with recommendation")
                
        # Check if we've researched both products and made a decision
        if (len(self.researched_products) >= 2 and 
            self.comparison_analysis and 
            self.comparison_analysis.recommendation):
            completion_signals.append("Research and comparison phase completed")
            
        # Goal is complete if we have strong purchase indicators or completed the full research cycle
        is_complete = (len([s for s in completion_signals if "purchase" in s.lower() or "order" in s.lower()]) > 0 or
                      (len(self.researched_products) >= 2 and 
                       self.comparison_analysis and 
                       self.comparison_analysis.recommendation and
                       any("buy" in page_text or "purchase" in page_text or "add to cart" in page_text)))
        
        return is_complete, completion_signals

    def analyze_page_state(self, obs: dict) -> str:
        """Analyze the current page state with advanced intelligence and track exploration journey"""
        url = obs.get("url", "")
        page_text = self.get_page_text(obs)
        
        # Enhanced page analysis
        analysis_parts = [f"Current URL: {url}"]
        
        # Add page text source info with quality assessment
        if obs.get("axtree_txt") and obs.get("pruned_html"):
            analysis_parts.append("Using: AXTree text (High quality)")
        elif not obs.get("axtree_txt") and obs.get("pruned_html"):
            analysis_parts.append("Using: HTML text (Medium quality, AXTree unavailable)")
        elif obs.get("axtree_txt") and not obs.get("pruned_html"):
            analysis_parts.append("Using: AXTree text (HTML unavailable)")
        
        # Add state tracking info with actionable insights
        if obs.get("repeated_state_count", 0) > 0:
            count = obs.get("repeated_state_count")
            if count >= 3:
                analysis_parts.append(f"Critical: Stuck in same state {count} times - need radical action change")
            elif count == 2:
                analysis_parts.append(f"Warning: Repeated state {count} times - try alternative approach")
            else:
                analysis_parts.append(f"Notice: Repeated state {count} time - monitor progress")
        
        # Advanced page type detection with confidence levels
        page_type = "Unknown"
        confidence = 0
        
        # Track URL visit frequency
        if url in self.visited_urls:
            self.visited_urls[url] += 1
        else:
            self.visited_urls[url] = 1
            
        # Add URL visit frequency to analysis
        visit_count = self.visited_urls.get(url, 0)
        if visit_count > 1:
            analysis_parts.append(f"Revisit: Page visited {visit_count} times")
        
        # Check for search page indicators
        search_indicators = ["search results", "found", "results for", "search for", "no results", "filter"]
        search_count = sum(1 for indicator in search_indicators if indicator in page_text.lower())
        if search_count >= 2 or "search" in url.lower():
            page_type = "Search"
            confidence = min(0.5 + (search_count * 0.1), 0.9)
            
        # Check for product page indicators
        product_indicators = ["add to cart", "buy now", "specifications", "features", "product details", 
                             "description", "reviews", "rating", "price", "in stock", "out of stock"]
        product_count = sum(1 for indicator in product_indicators if indicator in page_text.lower())
        if product_count >= 3:
            if product_count > search_count or "product" in url.lower():
                page_type = "Product"
                confidence = min(0.6 + (product_count * 0.05), 0.95)
        
        # Check for cart/checkout indicators
        cart_indicators = ["shopping cart", "your cart", "checkout", "payment", "shipping", "billing", 
                          "order summary", "subtotal", "total", "quantity", "remove"]
        cart_count = sum(1 for indicator in cart_indicators if indicator in page_text.lower())
        if cart_count >= 3 or "cart" in url.lower() or "checkout" in url.lower():
            page_type = "Cart/Checkout"
            confidence = min(0.7 + (cart_count * 0.05), 0.98)
            
        # Check for homepage indicators
        home_indicators = ["welcome", "featured", "popular", "categories", "deals", "trending"]
        home_count = sum(1 for indicator in home_indicators if indicator in page_text.lower())
        if home_count >= 2 and (url.endswith("/") or url.endswith(".com") or url.endswith(".org")):
            page_type = "Homepage"
            confidence = min(0.5 + (home_count * 0.1), 0.9)
            
        # Add page type with confidence
        analysis_parts.append(f"Page type: {page_type} (confidence: {int(confidence*100)}%)")
        
        # Record page in journey history
        journey_entry = {
            "url": url,
            "page_type": page_type,
            "confidence": confidence,
            "visit_count": self.visited_urls.get(url, 0),
            "timestamp": datetime.now().isoformat()
        }
        self.page_journey.append(journey_entry)
        
        # Analyze similar paths from history
        similar_pages = [p for p in self.page_journey if p["page_type"] == page_type and p["url"] != url]
        if similar_pages:
            analysis_parts.append(f"Similar pages visited: {len(similar_pages)}")
            
            # Check for patterns in exploration
            if len(similar_pages) >= 2 and page_type == "Product":
                analysis_parts.append("Pattern: Multiple product pages explored")
            elif len(similar_pages) >= 3 and page_type == "Search":
                analysis_parts.append("Pattern: Multiple searches performed - consider refining search terms")
        
        # Identify actionable elements on the page
        actionable_elements = []
        
        if "search" in page_text.lower():
            actionable_elements.append("Search box")
        if "add to cart" in page_text.lower():
            actionable_elements.append("Add to cart button")
        if "buy now" in page_text.lower():
            actionable_elements.append("Buy now button")
        if "checkout" in page_text.lower():
            actionable_elements.append("Checkout button")
        if "sign in" in page_text.lower() or "login" in page_text.lower():
            actionable_elements.append("Login form")
        
        # Add actionable elements if found
        if actionable_elements:
            analysis_parts.append(f"Actionable elements: {', '.join(actionable_elements)}")
        
        # Add screenshot availability info
        if obs.get("screenshot") is not None:
            analysis_parts.append("Visual data: Available")
        else:
            analysis_parts.append("Visual data: Unavailable")
            
        return " | ".join(analysis_parts)

    def parse_structured_response(self, response: str) -> tuple[str, str]:
        """Parse structured response to extract analysis and action"""
        lines = response.strip().split('\n')
        analysis_lines = []
        action_lines = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('**Analysis:**') or line.startswith('Analysis:'):
                current_section = 'analysis'
                continue
            elif line.startswith('**Strategy:**') or line.startswith('Strategy:'):
                current_section = 'analysis'  # Include strategy in analysis
                continue
            elif line.startswith('**Action:**') or line.startswith('Action:'):
                current_section = 'action'
                continue
            elif line.startswith('**') and line.endswith('**'):
                current_section = 'analysis'  # Default unknown sections to analysis
                continue
                
            if current_section == 'analysis':
                analysis_lines.append(line)
            elif current_section == 'action':
                action_lines.append(line)
            else:
                # If no section identified yet, assume it's analysis
                analysis_lines.append(line)
        
        analysis = '\n'.join(analysis_lines).strip()
        action = '\n'.join(action_lines).strip()
        
        # If no action found, use the last line as action
        if not action and analysis_lines:
            action = analysis_lines[-1]
            analysis = '\n'.join(analysis_lines[:-1]).strip()
            
        return analysis, action

    def _get_comparison_summary(self) -> str:
        """Get a summary of the comparison analysis"""
        if not self.comparison_analysis:
            return ""
            
        summary = "COMPARISON ANALYSIS:\n"
        if self.comparison_analysis.recommendation:
            summary += f"Recommended product: {self.comparison_analysis.recommendation}\n"
            summary += f"Reasoning: {self.comparison_analysis.reasoning}\n"
            
        if self.comparison_analysis.value_analysis:
            summary += "Value Analysis:\n"
            for product, analysis in self.comparison_analysis.value_analysis.items():
                summary += f"- {product}: {analysis}\n"
                
        return summary

    def get_step_summary(self, last_n: int = 15) -> str:
        """Get a summary of the last N steps"""
        if not self.step_history:
            return "No previous steps."
        
        recent_steps = self.step_history[-last_n:]
        summary_parts = []
        
        for step in recent_steps:
            step_summary = f"Step {step.step_number}: {step.action_type}({step.action_args}) - {step.reasoning[:100]}..."
            if step.error_message:
                step_summary += f" [ERROR: {step.error_message}]"
            summary_parts.append(step_summary)
        
        return "\n".join(summary_parts)

    def _get_exploration_pattern(self) -> str:
        """Analyze the page journey to identify navigation patterns"""
        if len(self.page_journey) < 3:
            return "Insufficient data"
            
        # Get the sequence of page types
        page_types = [entry["page_type"] for entry in self.page_journey[-5:]]
        
        # Identify common patterns
        if page_types.count("Search") > 2:
            return "Multiple searches - consider more specific search terms"
        elif page_types.count("Product") > 2:
            return "Multiple product pages - comparison shopping"
        elif "Search" in page_types and "Product" in page_types and "Cart/Checkout" in page_types:
            return "Search → Product → Checkout flow"
        elif page_types[-3:].count("Homepage") > 1:
            return "Returning to homepage frequently - may be lost"
        elif len(set(page_types[-3:])) == 1:
            return f"Staying on {page_types[-1]} pages"
        
        # Check for back-and-forth navigation
        if len(self.page_journey) > 3:
            recent_urls = [entry["url"] for entry in self.page_journey[-4:]]
            if len(set(recent_urls)) < len(recent_urls):
                return "Back-and-forth navigation between pages"
                
        return "Mixed navigation pattern"

    def get_action(self, obs: dict) -> tuple[str, dict]:
        """Get the next action to take"""
        self.step_count += 1
        timestamp = datetime.now().isoformat()
        
        # Preprocess observations
        processed_obs = self.obs_preprocessor(obs)
        
        # Initialize product research if needed
        if not self.products_to_research and self.goal_text:
            self.products_to_research = self.extract_products_from_goal(self.goal_text)
            if self.products_to_research:
                self.research_phase = "researching"
        
        # Extract product information if on a product page
        product_info = self.extract_product_info(processed_obs)
        if product_info and product_info not in self.researched_products:
            self.researched_products.append(product_info)
            
        # Update research phase
        if self.research_phase == "researching" and len(self.researched_products) >= len(self.products_to_research):
            self.research_phase = "comparing"
            self.comparison_analysis = self.perform_comparison_analysis()
        
        # Get research phase guidance
        research_guidance = self.get_research_phase_guidance()
        
        # Analyze current page state
        page_analysis = self.analyze_page_state(processed_obs)
        
        # Check for goal completion
        is_complete, completion_signals = self.detect_goal_completion(processed_obs, self.last_action)
        
        # Check for repeated states and suggest recovery actions
        recovery_guidance = ""
        if processed_obs.get("repeated_state_count", 0) >= 2:
            recovery_guidance = "\nWARNING: Page state has not changed in multiple steps. Try a different action such as scrolling, clicking a different element, or navigating back."
            self.no_progress_count += 1
        else:
            self.no_progress_count = 0
        
        # Build system message
        system_message = f"""You are an intelligent web browsing agent that provides structured analysis and reasoning while executing actions.

IMPORTANT: You must ALWAYS structure your response with these sections:
**Analysis:** [Your analysis of the current situation]
**Strategy:** [Your strategy for the next action]
**Action:** [The specific action you will take]

For search functionality:
1. First click on the search input field to focus it
2. Then type your search term
3. Finally press Enter or click the search button

PRODUCT RESEARCH METHODOLOGY:
When researching products, follow this systematic approach:
1. Search for each product individually using the search functionality
2. Navigate to product detail pages to gather specifications and pricing
3. Document key features: display, processor, camera, battery, storage, price
4. Compare products based on feature-to-price ratio
5. Make informed decision and proceed to purchase the recommended product

Current goal: {self.goal_text}
Research phase: {self.research_phase}
Research guidance: {research_guidance}{recovery_guidance}

Products to research: {', '.join(self.products_to_research) if self.products_to_research else 'None identified yet'}
Researched products: {len(self.researched_products)} of {len(self.products_to_research)}

{self._get_comparison_summary() if self.comparison_analysis else ''}

Page analysis: {page_analysis}
Step count: {self.step_count}

Exploration history: {len(self.page_journey)} pages visited
Most revisited pages: {', '.join([f"{url} ({count} visits)" for url, count in sorted(self.visited_urls.items(), key=lambda x: x[1], reverse=True)[:3] if count > 1]) or "None"}
{f"Navigation pattern: {self._get_exploration_pattern()}" if len(self.page_journey) > 2 else ""}

Recent steps summary:
{self.get_step_summary()}

Available actions: {self.action_set.describe()}

Provide structured analysis and then specify your next action."""

        # Build user message with the best available page content
        page_text = self.get_page_text(processed_obs)
        user_message = f"""Current page state:
URL: {processed_obs['url']}

Page content:
{page_text[:3000]}...

What should I do next? Remember to provide structured analysis before taking action."""

        try:
            # Get LLM response
            if self.model_name.startswith("gpt"):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                llm_response = response.choices[0].message.content
            elif self.model_name.startswith("claude"):
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    temperature=0.1,
                    system=system_message,
                    messages=[{"role": "user", "content": user_message}]
                )
                llm_response = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                llm_response = response.choices[0].message.content

            # Parse structured response
            analysis, action_text = self.parse_structured_response(llm_response)
            
            # Log the structured response
            logger.info(f"Step {self.step_count} Analysis: {analysis}")
            logger.info(f"Step {self.step_count} Action: {action_text}")
            
            # Parse action
            action_dict = self.action_set.to_python_code(action_text)
            
            # Store step information
            step_info = StepInfo(
                step_number=self.step_count,
                timestamp=timestamp,
                action=action_text,
                action_type=list(action_dict.keys())[0] if action_dict else "unknown",
                action_args=str(list(action_dict.values())[0]) if action_dict else "",
                reasoning=analysis,
                goal_snippet=self.goal_text[:100],
                page_state_summary=page_analysis,
                completion_signals=completion_signals
            )
            
            self.step_history.append(step_info)
            self.last_action = action_text
            self.last_reasoning = analysis
            
            return action_text, {
                "step_info": step_info,
                "analysis": analysis,
                "research_phase": self.research_phase,
                "products_researched": len(self.researched_products),
                "comparison_ready": self.comparison_analysis is not None
            }
            
        except Exception as e:
            error_msg = f"Error in get_action: {str(e)}"
            logger.error(error_msg)
            
            # Store error step
            step_info = StepInfo(
                step_number=self.step_count,
                timestamp=timestamp,
                action="wait(1)",
                action_type="wait",
                action_args="1",
                reasoning="Error occurred, waiting before retry",
                goal_snippet=self.goal_text[:100],
                page_state_summary=page_analysis,
                error_message=error_msg
            )
            
            self.step_history.append(step_info)
            return "wait(1)", {"error": error_msg, "step_info": step_info}

    def reset(self, seed: int = None) -> None:
        """Reset the agent state"""
        self.step_history = []
        self.step_count = 0
        self.last_action = ""
        self.last_reasoning = ""
        self.goal_text = ""
        # Reset product research state
        self.products_to_research = []
        self.researched_products = []
        self.comparison_analysis = None
        self.research_phase = "initial"
        # Reset page state tracking
        self.last_page_hash = ""
        self.repeated_state_count = 0
        self.no_progress_count = 0
        
        # Reset page exploration journey tracking
        self.page_journey = []
        self.visited_urls = {}
        self.page_outcomes = {}

    def close(self):
        """Clean up resources"""
        pass

    def extract_products_from_goal(self, goal_text: str) -> List[str]:
        """Extract product names from the goal text"""
        products = []
        goal_lower = goal_text.lower()
        
        # Look for Samsung products specifically
        if "samsung galaxy s24 ultra" in goal_lower:
            products.append("SAMSUNG Galaxy S24 Ultra")
        if "samsung galaxy z fold 6" in goal_lower:
            products.append("SAMSUNG Galaxy Z Fold 6")
            
        # Generic product extraction patterns
        import re
        # Look for quoted product names
        quoted_products = re.findall(r'"([^"]*)"', goal_text)
        for product in quoted_products:
            if product not in products and len(product) > 3:
                products.append(product)
        
        return products



    def get_research_phase_guidance(self) -> str:
        """Get guidance based on current research phase"""
        if self.research_phase == "initial":
            if not self.products_to_research:
                return "Extract product names from goal and start research phase"
            else:
                return f"Begin researching products: {', '.join(self.products_to_research)}"
                
        elif self.research_phase == "researching":
            incomplete_products = [p for p in self.products_to_research 
                                 if not any(rp.name == p and rp.research_complete 
                                          for rp in self.researched_products)]
            if incomplete_products:
                return f"Continue researching: {incomplete_products[0]}"
            else:
                return "All products researched, move to comparison phase"
                
        elif self.research_phase == "comparing":
            return "Perform comparative analysis of researched products"
            
        elif self.research_phase == "deciding":
            return "Make final decision based on comparison analysis"
            
        elif self.research_phase == "purchasing":
            return "Proceed with purchase of selected product"
            
        return "Continue with current task"

    def extract_product_info(self, obs: dict) -> Optional[ProductInfo]:
        """Extract product information from current page"""
        page_text = self.get_page_text(obs).lower()
        current_url = obs.get("url", "")
        
        # Try to identify if we're on a product page
        product_indicators = ["price", "specifications", "features", "buy now", "add to cart"]
        if not any(indicator in page_text for indicator in product_indicators):
            return None
            
        # Extract product name
        product_name = None
        for product in self.products_to_research:
            if product.lower() in page_text:
                product_name = product
                break
                
        if not product_name:
            return None
            
        # Extract price
        price = None
        price_patterns = [r'\$[\d,]+\.?\d*', r'price[:\s]*\$?[\d,]+\.?\d*']
        for pattern in price_patterns:
            import re
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                price = matches[0]
                break
                
        # Extract specifications
        specs = {}
        spec_keywords = ["display", "screen", "processor", "cpu", "camera", "battery", "storage", "memory", "ram"]
        lines = page_text.split('\n')
        for line in lines:
            for keyword in spec_keywords:
                if keyword in line.lower():
                    specs[keyword] = line.strip()
                    
        return ProductInfo(
            name=product_name,
            price=price,
            specifications=specs,
            url=current_url,
            research_complete=bool(price and specs)
        )

    def perform_comparison_analysis(self) -> ComparisonAnalysis:
        """Perform comparative analysis of researched products"""
        if len(self.researched_products) < 2:
            return ComparisonAnalysis()
            
        analysis = ComparisonAnalysis(products=self.researched_products.copy())
        
        # Build comparison matrix
        spec_categories = set()
        for product in self.researched_products:
            spec_categories.update(product.specifications.keys())
            
        for category in spec_categories:
            analysis.comparison_matrix[category] = {}
            for product in self.researched_products:
                analysis.comparison_matrix[category][product.name] = product.specifications.get(category, "N/A")
                
        # Enhanced value analysis with feature-to-price ratio
        product_scores = {}
        for product in self.researched_products:
            value_score = 0
            reasoning_parts = []
            
            # Price analysis with more granular scoring
            price_score = 0
            if product.price:
                try:
                    import re
                    price_num = float(re.sub(r'[^\d.]', '', product.price))
                    if price_num < 800:
                        price_score = 5
                        reasoning_parts.append("Excellent price point (<$800)")
                    elif price_num < 1000:
                        price_score = 4
                        reasoning_parts.append("Very good price point (<$1000)")
                    elif price_num < 1200:
                        price_score = 3
                        reasoning_parts.append("Good price point (<$1200)")
                    elif price_num < 1500:
                        price_score = 2
                        reasoning_parts.append("Fair price point (<$1500)")
                    else:
                        price_score = 1
                        reasoning_parts.append("Premium price point (>$1500)")
                except:
                    price_score = 2
                    reasoning_parts.append("Price information available")
            else:
                price_score = 1
                reasoning_parts.append("No clear price information")
                
            # Feature analysis with weighted scoring
            feature_score = 0
            feature_count = len(product.specifications)
            
            # Base feature score
            if feature_count > 8:
                feature_score += 4
                reasoning_parts.append("Comprehensive feature set (8+ specs)")
            elif feature_count > 5:
                feature_score += 3
                reasoning_parts.append("Rich feature set (5+ specs)")
            elif feature_count > 3:
                feature_score += 2
                reasoning_parts.append("Good feature set (3+ specs)")
            else:
                feature_score += 1
                reasoning_parts.append("Basic feature information")
                
            # Bonus for key specifications
            key_specs = ["display", "processor", "camera", "battery", "storage"]
            key_spec_count = sum(1 for spec in key_specs if any(spec in k.lower() for k in product.specifications.keys()))
            if key_spec_count >= 4:
                feature_score += 2
                reasoning_parts.append("Has most key specifications")
            elif key_spec_count >= 2:
                feature_score += 1
                reasoning_parts.append("Has some key specifications")
                
            # Calculate feature-to-price ratio
            total_score = (feature_score * 0.6) + (price_score * 0.4)  # Weight features slightly more
            product_scores[product.name] = total_score
            
            analysis.value_analysis[product.name] = f"Score: {total_score:.1f}/10 - {', '.join(reasoning_parts)}"
            
        # Make recommendation based on highest score
        if product_scores:
            best_product_name = max(product_scores.keys(), key=lambda k: product_scores[k])
            best_score = product_scores[best_product_name]
            
            analysis.recommendation = best_product_name
            
            # Generate detailed reasoning
            reasoning_parts = [
                f"Highest overall score: {best_score:.1f}/10",
                "Based on feature-to-price ratio analysis"
            ]
            
            # Compare with other products
            other_products = [p for p in product_scores.keys() if p != best_product_name]
            if other_products:
                other_scores = [f"{p}: {product_scores[p]:.1f}" for p in other_products]
                reasoning_parts.append(f"Compared to: {', '.join(other_scores)}")
                
            analysis.reasoning = ". ".join(reasoning_parts)
            
        return analysis


@dataclasses.dataclass
class EnhancedDemoAgentArgs(AbstractAgentArgs):
    """Arguments for EnhancedDemoAgent"""
    model_name: str = "gpt-4o"
    chat_mode: bool = False
    demo_mode: str = "off"
    use_html: bool = True  # Changed to True to enable HTML fallback
    use_axtree: bool = True
    use_screenshot: bool = False
    system_message_handling: Literal["separate", "combined"] = "separate"
    thinking_budget: int = 10000
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_site_url: Optional[str] = None
    openrouter_site_name: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    def make_agent(self):
        return EnhancedDemoAgent(
            model_name=self.model_name,
            chat_mode=self.chat_mode,
            demo_mode=self.demo_mode,
            use_html=self.use_html,
            use_axtree=self.use_axtree,
            use_screenshot=self.use_screenshot,
            system_message_handling=self.system_message_handling,
            thinking_budget=self.thinking_budget,
            openai_api_key=self.openai_api_key,
            openrouter_api_key=self.openrouter_api_key,
            openrouter_site_url=self.openrouter_site_url,
            openrouter_site_name=self.openrouter_site_name,
            anthropic_api_key=self.anthropic_api_key,
        )
ENDFILE

chmod +x enhanced_demo_agent.py
echo "Enhanced Demo Agent class implementation restored successfully."

#!/usr/bin/env python3
"""
🚀 WOW DEMO #4: Adaptive Workflows & Intelligent Decision Making
================================================================

This demo showcases Nova Act's ability to dynamically adapt its behavior
based on page content, user preferences, and contextual information.
It demonstrates true AI-powered decision making in web automation.

WOW FACTORS:
- Dynamic workflow adaptation based on page analysis
- Context-aware decision making and strategy switching
- Intelligent fallback mechanisms and error recovery
- User preference learning and application
- Real-time strategy optimization
"""

import os
import json
import time
from datetime import datetime
from nova_act import NovaAct
from typing import Dict, List, Any, Optional


class AdaptiveWorkflowDemo:
    """Demonstrates intelligent workflow adaptation and decision making"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.user_preferences = {
            "budget_range": {"min": 50, "max": 500},
            "preferred_brands": ["Apple", "Google", "Samsung", "Microsoft"],
            "avoid_brands": ["Unknown", "Generic"],
            "priority_factors": ["price", "rating", "reviews"],
            "shopping_style": "research_heavy",  # vs "quick_buyer"
            "risk_tolerance": "low",  # low, medium, high
            "time_preference": "thorough"  # quick, balanced, thorough
        }
        self.context_memory = {}
        
    def demo_adaptive_shopping_workflow(self, product_query: str = "wireless headphones") -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Adaptive e-commerce workflow that changes strategy based on site type
        - Analyzes each site's layout and adapts navigation strategy
        - Applies user preferences dynamically
        - Switches between different shopping approaches
        """
        print(f"🛒 Adaptive Shopping Workflow for: {product_query}")
        
        workflow_results = {
            "product_query": product_query,
            "sites_visited": [],
            "adaptation_strategies": [],
            "decisions_made": [],
            "final_recommendations": [],
            "workflow_efficiency": {}
        }
        
        # Start with Google Shopping for overview
        print("\n🔍 Phase 1: Market Research & Strategy Planning")
        try:
            with NovaAct(starting_page="https://www.google.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Research the market for "{product_query}" and develop an adaptive shopping strategy.
                
                Steps:
                1. Search for "{product_query}" on Google Shopping
                2. Analyze the market landscape:
                   - Price ranges available
                   - Popular brands and models
                   - Key features to compare
                   - Best-rated options
                
                3. Based on these user preferences, develop a strategy:
                   - Budget: ${self.user_preferences['budget_range']['min']}-${self.user_preferences['budget_range']['max']}
                   - Preferred brands: {', '.join(self.user_preferences['preferred_brands'])}
                   - Priority factors: {', '.join(self.user_preferences['priority_factors'])}
                   - Shopping style: {self.user_preferences['shopping_style']}
                
                4. Recommend which sites to visit and what strategy to use for each:
                   - Amazon: Focus on reviews and variety
                   - Best Buy: Focus on specs and in-store availability
                   - Specialized retailers: Focus on expert reviews
                
                5. Identify the top 3-5 specific products to research further
                
                Provide a strategic shopping plan adapted to the user's preferences.
                """, max_steps=8, timeout=60)
                
                if result and hasattr(result, 'response'):
                    strategy_data = {
                        'phase': 'Market Research',
                        'strategy_plan': str(result.response),
                        'adaptations_made': ['Budget-aware filtering', 'Brand preference application']
                    }
                    workflow_results['sites_visited'].append(strategy_data)
                    print("✅ Strategic planning completed")
                
        except Exception as e:
            print(f"❌ Error in market research: {e}")
        
        # Adaptive Amazon navigation
        print("\n🛒 Phase 2: Adaptive Amazon Navigation")
        try:
            with NovaAct(starting_page="https://www.amazon.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Navigate Amazon with an adaptive strategy for "{product_query}".
                
                Adaptive Approach:
                1. First, analyze Amazon's current layout and search interface
                2. Search for "{product_query}" and adapt to the results page layout
                3. Apply intelligent filtering based on user preferences:
                   - Set price range: ${self.user_preferences['budget_range']['min']}-${self.user_preferences['budget_range']['max']}
                   - Filter by preferred brands if available: {', '.join(self.user_preferences['preferred_brands'])}
                   - Sort by user priority: {self.user_preferences['priority_factors'][0]}
                
                4. Analyze the top results and adapt selection criteria:
                   - If user is "research_heavy", read detailed reviews
                   - If budget-conscious, compare price-to-value ratios
                   - If brand-loyal, prioritize preferred brands
                
                5. For the top 2-3 products, extract:
                   - Detailed specifications
                   - Customer review sentiment and key points
                   - Price history if visible
                   - Availability and shipping options
                
                6. Make intelligent decisions about which products warrant deeper investigation
                
                Adapt your approach based on what you find - if Amazon has limited selection,
                note this for strategy adjustment. If reviews are sparse, focus on specs.
                """, max_steps=10, timeout=75)
                
                if result and hasattr(result, 'response'):
                    amazon_data = {
                        'phase': 'Amazon Adaptive Navigation',
                        'site_analysis': str(result.response),
                        'adaptations_made': ['Layout-aware navigation', 'Preference-based filtering', 'Review-depth adjustment']
                    }
                    workflow_results['sites_visited'].append(amazon_data)
                    print("✅ Amazon adaptive navigation completed")
                
        except Exception as e:
            print(f"❌ Error in Amazon navigation: {e}")
        
        return workflow_results
    
    def demo_context_aware_research(self, research_topic: str = "best programming languages 2024") -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Context-aware research that adapts methodology based on topic type
        - Analyzes topic to determine best research approach
        - Adapts source selection based on topic domain
        - Switches between different research methodologies
        """
        print(f"🔬 Context-Aware Research on: {research_topic}")
        
        research_results = {
            "topic": research_topic,
            "context_analysis": {},
            "methodology_adaptations": [],
            "sources_selected": [],
            "synthesis_approach": "",
            "confidence_assessment": {}
        }
        
        try:
            with NovaAct(starting_page="https://www.google.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Conduct context-aware research on "{research_topic}" with adaptive methodology.
                
                Phase 1: Context Analysis
                1. Analyze the research topic to determine:
                   - Domain type (technical, business, academic, opinion-based)
                   - Recency requirements (how current must info be?)
                   - Expertise level needed (beginner, intermediate, expert)
                   - Controversy level (factual vs. opinion-heavy)
                
                Phase 2: Adaptive Source Selection
                Based on context analysis, intelligently select sources:
                - For technical topics: Stack Overflow, GitHub, official docs
                - For trends/opinions: Reddit, Twitter, industry blogs
                - For academic: Research papers, university sites
                - For business: Industry reports, company blogs
                - For current events: News sites, real-time sources
                
                Phase 3: Methodology Adaptation
                Adapt research approach based on topic:
                - If highly technical: Focus on code examples and documentation
                - If trend-based: Look for surveys, polls, community discussions
                - If controversial: Seek multiple perspectives and balanced views
                - If rapidly changing: Prioritize recent sources and updates
                
                Phase 4: Intelligent Synthesis
                1. Visit 3-4 carefully selected sources
                2. Extract information using topic-appropriate methods
                3. Cross-reference findings for consistency
                4. Note any conflicting information or biases
                5. Assess confidence level of findings
                
                Provide a comprehensive research report that demonstrates how you
                adapted your methodology based on the topic's characteristics.
                """, max_steps=12, timeout=90)
                
                if result and hasattr(result, 'response'):
                    research_results['comprehensive_analysis'] = str(result.response)
                    print("✅ Context-aware research completed")
                
        except Exception as e:
            print(f"❌ Error in context-aware research: {e}")
            research_results['error'] = str(e)
        
        return research_results
    
    def demo_intelligent_fallback_system(self) -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Intelligent fallback and error recovery system
        - Detects when primary strategies fail
        - Automatically switches to alternative approaches
        - Learns from failures to improve future attempts
        """
        print("🔄 Intelligent Fallback & Error Recovery System")
        
        fallback_results = {
            "primary_attempts": [],
            "fallback_strategies": [],
            "recovery_actions": [],
            "learning_outcomes": [],
            "final_success_rate": 0
        }
        
        try:
            with NovaAct(starting_page="https://www.google.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Demonstrate intelligent fallback systems by attempting a challenging task
                with multiple potential failure points.
                
                Challenge: Find and compare laptop prices on a site that might have issues
                
                Primary Strategy:
                1. Search for "laptop deals" and try to access a shopping site
                2. If the first site has issues (slow loading, popups, etc.), note the problem
                3. Implement intelligent fallback:
                   - Try alternative search terms
                   - Switch to a different site
                   - Adapt navigation approach
                
                Fallback Strategies to demonstrate:
                1. Site Accessibility Issues:
                   - If site won't load: Try alternative sites
                   - If popups block access: Find ways around them
                   - If search doesn't work: Try browsing categories
                
                2. Content Issues:
                   - If prices aren't visible: Look for alternative price indicators
                   - If product info is limited: Seek additional sources
                   - If site layout is confusing: Adapt navigation strategy
                
                3. Data Extraction Issues:
                   - If structured data fails: Fall back to text extraction
                   - If specific elements aren't found: Use alternative selectors
                   - If information is incomplete: Combine multiple sources
                
                For each fallback used:
                - Explain why the primary approach failed
                - Describe the alternative strategy chosen
                - Show how the system adapted and recovered
                - Assess the success of the fallback approach
                
                Demonstrate resilient, adaptive behavior that doesn't give up easily.
                """, max_steps=15, timeout=100)
                
                if result and hasattr(result, 'response'):
                    fallback_results['demonstration'] = str(result.response)
                    print("✅ Fallback system demonstration completed")
                
        except Exception as e:
            print(f"❌ Error in fallback demonstration: {e}")
            fallback_results['error'] = str(e)
        
        return fallback_results
    
    def demo_preference_learning_system(self) -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Dynamic preference learning and application
        - Observes user behavior patterns
        - Adapts strategies based on inferred preferences
        - Improves performance through learning
        """
        print("🧠 Preference Learning & Adaptive Behavior System")
        
        learning_results = {
            "initial_preferences": self.user_preferences.copy(),
            "observed_behaviors": [],
            "preference_updates": [],
            "strategy_adaptations": [],
            "performance_improvements": []
        }
        
        try:
            with NovaAct(starting_page="https://www.google.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Demonstrate preference learning by simulating user behavior analysis.
                
                Scenario: User is shopping for tech products with these stated preferences:
                {json.dumps(self.user_preferences, indent=2)}
                
                Simulation Process:
                1. Initial Behavior Observation:
                   - Search for "smartphone deals" and observe which results get attention
                   - Note if user gravitates toward certain price ranges
                   - Track which product features are examined most
                
                2. Pattern Recognition:
                   - If user consistently clicks on mid-range options, update budget preference
                   - If user spends time reading reviews, increase "research_heavy" weight
                   - If user avoids certain brands, add to "avoid_brands" list
                
                3. Preference Inference:
                   - Based on observed behavior, infer hidden preferences:
                     * Color preferences (if user clicks on specific colors)
                     * Feature priorities (if user focuses on certain specs)
                     * Brand loyalty strength (how much brand affects decisions)
                
                4. Strategy Adaptation:
                   - Modify search strategies based on learned preferences
                   - Adjust filtering and sorting based on observed priorities
                   - Change information presentation based on user attention patterns
                
                5. Performance Optimization:
                   - Show how learned preferences improve recommendation accuracy
                   - Demonstrate faster task completion through better targeting
                   - Reduce irrelevant information based on user patterns
                
                Simulate this learning process and show how the system becomes more
                effective at serving the user's actual (vs. stated) preferences.
                """, max_steps=10, timeout=75)
                
                if result and hasattr(result, 'response'):
                    learning_results['learning_simulation'] = str(result.response)
                    print("✅ Preference learning demonstration completed")
                
        except Exception as e:
            print(f"❌ Error in preference learning demo: {e}")
            learning_results['error'] = str(e)
        
        return learning_results
    
    def run_complete_adaptive_demo(self) -> Dict[str, Any]:
        """Run the complete adaptive workflow demonstration"""
        print("🚀 WOW DEMO #4: Adaptive Workflows & Intelligent Decision Making")
        print("=" * 80)
        print("Demonstrating advanced AI-powered workflow adaptation...")
        
        complete_results = {
            "demo_suite": "Adaptive Workflows & Intelligent Decision Making",
            "demonstrations_completed": [],
            "adaptation_strategies_shown": [],
            "intelligence_factors": [],
            "overall_success": True
        }
        
        # Run all demonstrations
        demonstrations = [
            ("Adaptive Shopping Workflow", lambda: self.demo_adaptive_shopping_workflow("wireless headphones")),
            ("Context-Aware Research", lambda: self.demo_context_aware_research("best programming languages 2024")),
            ("Intelligent Fallback System", self.demo_intelligent_fallback_system),
            ("Preference Learning System", self.demo_preference_learning_system)
        ]
        
        for demo_name, demo_func in demonstrations:
            print(f"\n{'='*60}")
            print(f"Running: {demo_name}")
            print('='*60)
            
            try:
                result = demo_func()
                result['demonstration_name'] = demo_name
                complete_results['demonstrations_completed'].append(result)
                
                if 'error' not in result:
                    print(f"✅ {demo_name} completed successfully!")
                else:
                    print(f"⚠️ {demo_name} completed with issues")
                    complete_results['overall_success'] = False
                    
            except Exception as e:
                print(f"❌ {demo_name} failed: {e}")
                complete_results['demonstrations_completed'].append({
                    'demonstration_name': demo_name,
                    'error': str(e)
                })
                complete_results['overall_success'] = False
        
        # Generate comprehensive summary
        print("\n" + "="*80)
        print("🧠 ADAPTIVE WORKFLOW DEMONSTRATION RESULTS")
        print("="*80)
        
        successful_demos = [d for d in complete_results['demonstrations_completed'] if 'error' not in d]
        print(f"✅ Successful Demonstrations: {len(successful_demos)}/{len(demonstrations)}")
        
        print("\n✨ WOW FACTORS DEMONSTRATED:")
        wow_factors = [
            "🧠 Dynamic strategy adaptation based on page analysis",
            "🎯 Context-aware decision making and methodology switching",
            "🔄 Intelligent fallback mechanisms and error recovery",
            "📊 User preference learning and behavioral adaptation",
            "⚡ Real-time strategy optimization and performance tuning",
            "🎨 Layout-aware navigation and interface adaptation",
            "🔍 Content-type recognition and approach modification",
            "🛡️ Robust error handling with multiple recovery strategies",
            "📈 Continuous improvement through experience learning",
            "🎪 Multi-modal workflow orchestration and coordination"
        ]
        
        for factor in wow_factors:
            print(f"   {factor}")
        
        print(f"\n🎯 Key Intelligence Capabilities:")
        intelligence_capabilities = [
            "Contextual understanding and situation assessment",
            "Dynamic strategy formulation and execution",
            "Pattern recognition and preference inference",
            "Adaptive problem-solving and creative solutions",
            "Multi-objective optimization and trade-off management",
            "Failure prediction and proactive mitigation",
            "Experience-based learning and improvement"
        ]
        
        for capability in intelligence_capabilities:
            print(f"   • {capability}")
        
        print(f"\n🕒 Complete demonstration finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return complete_results


if __name__ == "__main__":
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        exit(1)
    
    demo = AdaptiveWorkflowDemo(api_key)
    demo.run_complete_adaptive_demo()
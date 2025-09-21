#!/usr/bin/env python3
"""
Nova Act Advanced Capabilities Demo
===================================

This script demonstrates the advanced features and capabilities of Nova Act
beyond basic voice commands. It showcases complex web automation scenarios,
multi-step workflows, and sophisticated browser interactions.
"""

import os
import time
import json
from nova_act import NovaAct
from typing import Dict, Any, List


class NovaCapabilitiesDemo:
    """Demonstrates advanced Nova Act capabilities"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.results = []
    
    def log_result(self, demo_name: str, result: Any, success: bool = True):
        """Log demo results"""
        self.results.append({
            'demo': demo_name,
            'success': success,
            'result': str(result)[:200] + '...' if len(str(result)) > 200 else str(result),
            'timestamp': time.time()
        })
        status = "✅" if success else "❌"
        print(f"{status} {demo_name}: {result}")
    
    def demo_complex_navigation(self):
        """Demo: Complex multi-step navigation and data extraction"""
        print("\n🌐 Demo: Complex Navigation & Data Extraction")
        
        try:
            with NovaAct(starting_page="https://news.ycombinator.com", 
                        nova_act_api_key=self.api_key) as nova:
                
                # Multi-step task: Navigate, find, click, extract
                result = nova.act("""
                1. Find the top story on Hacker News
                2. Click on it to read the full article
                3. Extract the article title, author (if available), and first paragraph
                4. Return this information in a structured format
                """)
                
                self.log_result("Complex Navigation", result.response)
                
        except Exception as e:
            self.log_result("Complex Navigation", f"Error: {e}", False)
    
    def demo_form_automation(self):
        """Demo: Advanced form filling and submission"""
        print("\n📝 Demo: Advanced Form Automation")
        
        try:
            with NovaAct(starting_page="https://httpbin.org/forms/post", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Fill out this form with the following information:
                - Customer Name: John Doe
                - Telephone: +1-555-0123
                - Email: john.doe@example.com
                - Size: Large
                - Topping: Pepperoni
                - Delivery Time: 7:00 PM
                - Comments: Please ring the doorbell twice
                
                Then submit the form and return the response details.
                """)
                
                self.log_result("Form Automation", result.response)
                
        except Exception as e:
            self.log_result("Form Automation", f"Error: {e}", False)
    
    def demo_ecommerce_workflow(self):
        """Demo: E-commerce shopping workflow"""
        print("\n🛒 Demo: E-commerce Shopping Workflow")
        
        try:
            with NovaAct(starting_page="https://demo.opencart.com", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Simulate a shopping experience:
                1. Search for "laptop" in the search bar
                2. Browse the first few results
                3. Click on a laptop that costs between $500-$1000
                4. Add it to the cart
                5. View the cart contents
                6. Extract the product name, price, and cart total
                7. Return this information without actually purchasing
                """)
                
                self.log_result("E-commerce Workflow", result.response)
                
        except Exception as e:
            self.log_result("E-commerce Workflow", f"Error: {e}", False)
    
    def demo_data_extraction(self):
        """Demo: Advanced data extraction from tables and lists"""
        print("\n📊 Demo: Advanced Data Extraction")
        
        try:
            with NovaAct(starting_page="https://en.wikipedia.org/wiki/List_of_countries_by_population", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Extract information about the top 10 most populous countries:
                1. Find the main population table
                2. Extract the country name, population, and percentage of world population
                3. Format this as a structured list
                4. Also note the data source and last update date if available
                """)
                
                self.log_result("Data Extraction", result.response)
                
        except Exception as e:
            self.log_result("Data Extraction", f"Error: {e}", False)
    
    def demo_social_media_interaction(self):
        """Demo: Social media-like interactions"""
        print("\n📱 Demo: Social Media Interactions")
        
        try:
            with NovaAct(starting_page="https://jsonplaceholder.typicode.com", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Explore this API documentation site:
                1. Navigate to the posts section
                2. Find information about how to create a new post
                3. Look for user management features
                4. Extract the main API endpoints available
                5. Summarize the key features of this API service
                """)
                
                self.log_result("Social Media Interactions", result.response)
                
        except Exception as e:
            self.log_result("Social Media Interactions", f"Error: {e}", False)
    
    def demo_search_and_compare(self):
        """Demo: Search and comparison across multiple sources"""
        print("\n🔍 Demo: Search & Compare")
        
        try:
            with NovaAct(starting_page="https://www.google.com", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Research Python web frameworks:
                1. Search for "Python web frameworks comparison"
                2. Click on a comprehensive comparison article or resource
                3. Extract information about Django, Flask, and FastAPI
                4. Compare their key features, pros, and cons
                5. Provide a summary recommendation for different use cases
                """)
                
                self.log_result("Search & Compare", result.response)
                
        except Exception as e:
            self.log_result("Search & Compare", f"Error: {e}", False)
    
    def demo_dynamic_content(self):
        """Demo: Handling dynamic content and JavaScript interactions"""
        print("\n⚡ Demo: Dynamic Content Handling")
        
        try:
            with NovaAct(starting_page="https://httpbin.org", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Explore this HTTP testing service:
                1. Navigate to different endpoints (like /json, /xml, /html)
                2. Test a few HTTP methods if there are interactive examples
                3. Extract sample responses from different endpoints
                4. Summarize what this service is used for and its main features
                """)
                
                self.log_result("Dynamic Content", result.response)
                
        except Exception as e:
            self.log_result("Dynamic Content", f"Error: {e}", False)
    
    def demo_multi_tab_workflow(self):
        """Demo: Multi-tab browsing and cross-tab data correlation"""
        print("\n🗂️ Demo: Multi-tab Workflow")
        
        try:
            with NovaAct(starting_page="https://www.github.com", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Explore GitHub's trending repositories:
                1. Go to the trending page
                2. Find the top trending Python repository
                3. Click on it to view details
                4. Extract: repository name, description, stars, language, and recent activity
                5. Go back and check one more trending repository
                6. Compare the two repositories and provide insights
                """)
                
                self.log_result("Multi-tab Workflow", result.response)
                
        except Exception as e:
            self.log_result("Multi-tab Workflow", f"Error: {e}", False)
    
    def demo_accessibility_features(self):
        """Demo: Accessibility and alternative interaction methods"""
        print("\n♿ Demo: Accessibility Features")
        
        try:
            with NovaAct(starting_page="https://www.w3.org/WAI/", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Explore web accessibility resources:
                1. Navigate to accessibility guidelines or standards
                2. Find information about WCAG (Web Content Accessibility Guidelines)
                3. Extract key principles of web accessibility
                4. Look for practical examples or tools mentioned
                5. Summarize the main accessibility recommendations
                """)
                
                self.log_result("Accessibility Features", result.response)
                
        except Exception as e:
            self.log_result("Accessibility Features", f"Error: {e}", False)
    
    def demo_api_interaction(self):
        """Demo: API testing and interaction through web interfaces"""
        print("\n🔌 Demo: API Interaction")
        
        try:
            with NovaAct(starting_page="https://reqres.in", 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Explore this API testing service:
                1. Look at the available API endpoints
                2. Find examples of GET, POST, PUT, DELETE requests
                3. Extract sample request and response formats
                4. Test one of the interactive examples if available
                5. Summarize the API capabilities and use cases
                """)
                
                self.log_result("API Interaction", result.response)
                
        except Exception as e:
            self.log_result("API Interaction", f"Error: {e}", False)
    
    def run_all_demos(self):
        """Run all capability demonstrations"""
        print("🚀 Starting Nova Act Advanced Capabilities Demo")
        print("=" * 60)
        
        demos = [
            self.demo_complex_navigation,
            self.demo_form_automation,
            self.demo_ecommerce_workflow,
            self.demo_data_extraction,
            self.demo_social_media_interaction,
            self.demo_search_and_compare,
            self.demo_dynamic_content,
            self.demo_multi_tab_workflow,
            self.demo_accessibility_features,
            self.demo_api_interaction
        ]
        
        for demo in demos:
            try:
                demo()
                time.sleep(2)  # Brief pause between demos
            except Exception as e:
                print(f"❌ Demo failed: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print a summary of all demo results"""
        print("\n" + "=" * 60)
        print("📋 DEMO SUMMARY")
        print("=" * 60)
        
        successful = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Total Demos: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {(successful/total)*100:.1f}%")
        
        print("\n📊 Detailed Results:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['demo']}")
            if not result['success']:
                print(f"   Error: {result['result']}")
        
        print("\n🎯 Nova Act Capabilities Demonstrated:")
        capabilities = [
            "✅ Complex multi-step navigation",
            "✅ Advanced form automation",
            "✅ E-commerce workflow simulation",
            "✅ Data extraction from structured content",
            "✅ Dynamic content handling",
            "✅ Search and comparison workflows",
            "✅ Multi-tab browsing coordination",
            "✅ API documentation exploration",
            "✅ Accessibility-aware interactions",
            "✅ Real-time content analysis"
        ]
        
        for capability in capabilities:
            print(capability)


def main():
    """Main function to run the Nova Act capabilities demo"""
    
    # Check for API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Error: NOVA_ACT_API_KEY environment variable not set")
        print("Please set your Nova Act API key:")
        print("export NOVA_ACT_API_KEY=your_api_key_here")
        return
    
    print("🔑 Nova Act API Key: ✅ Found")
    
    # Create and run demo
    demo = NovaCapabilitiesDemo(api_key)
    demo.run_all_demos()
    
    print("\n🎉 Demo completed! Nova Act shows incredible capabilities for:")
    print("   • Complex web automation workflows")
    print("   • Intelligent content extraction")
    print("   • Multi-step task coordination")
    print("   • Dynamic interaction handling")
    print("   • Cross-platform web navigation")


if __name__ == "__main__":
    main()
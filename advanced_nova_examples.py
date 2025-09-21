#!/usr/bin/env python3
"""
Advanced Nova Act Examples
==========================

This file contains specific examples of Nova Act's advanced capabilities,
including structured outputs, complex workflows, and sophisticated automation.
"""

import os
import json
from nova_act import NovaAct
from typing import Dict, Any


def example_structured_data_extraction():
    """Example: Extract structured data with JSON schema validation"""
    print("🏗️ Structured Data Extraction with Schema")
    
    # Define a JSON schema for the expected output
    schema = {
        "type": "object",
        "properties": {
            "articles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "author": {"type": "string"},
                        "points": {"type": "integer"},
                        "comments": {"type": "integer"},
                        "url": {"type": "string"}
                    },
                    "required": ["title", "points"]
                }
            },
            "total_articles": {"type": "integer"}
        },
        "required": ["articles", "total_articles"]
    }
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://news.ycombinator.com", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act(
                """Extract the top 5 articles from Hacker News front page. 
                For each article, get the title, author (if visible), points, 
                number of comments, and URL. Return as structured JSON.""",
                schema=schema
            )
            
            print("✅ Structured extraction successful!")
            print(json.dumps(result.response, indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_multi_step_workflow():
    """Example: Complex multi-step workflow with decision making"""
    print("\n🔄 Multi-Step Workflow with Decision Making")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://www.google.com", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Perform this multi-step research task:
            
            1. Search for "best programming languages 2024"
            2. Click on a reputable source (like Stack Overflow, GitHub, or tech blog)
            3. If the page has a survey or ranking, extract the top 5 languages
            4. For each language, note:
               - Ranking position
               - Key use cases mentioned
               - Any growth trends mentioned
            5. If no clear ranking is found, look for another source
            6. Summarize findings in a structured format
            
            Make intelligent decisions about which sources to trust and 
            how to extract the most relevant information.
            """, max_steps=15)  # Allow more steps for complex workflow
            
            print("✅ Multi-step workflow completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_form_automation_with_validation():
    """Example: Advanced form automation with validation"""
    print("\n📝 Advanced Form Automation with Validation")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://httpbin.org/forms/post", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Fill out this form intelligently:
            
            1. Analyze the form fields and their requirements
            2. Fill with realistic test data:
               - Use a professional-sounding name
               - Use a valid phone format
               - Use a proper email format
               - Choose appropriate options for dropdowns
            3. Before submitting, validate that all required fields are filled
            4. Submit the form
            5. Capture and return the response/confirmation
            6. If there are any validation errors, fix them and retry
            
            Be smart about handling any unexpected form behaviors.
            """)
            
            print("✅ Form automation with validation completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_comparative_analysis():
    """Example: Comparative analysis across multiple sources"""
    print("\n📊 Comparative Analysis Across Sources")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://www.github.com/trending", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Perform a comparative analysis of trending repositories:
            
            1. Identify the top 3 trending Python repositories
            2. For each repository:
               - Visit the repository page
               - Extract: name, description, stars, forks, main language
               - Look at the README for key features
               - Check recent commits/activity level
               - Note the license type
            3. Compare the repositories across these dimensions:
               - Popularity (stars/forks)
               - Activity level
               - Use case/purpose
               - Community engagement
            4. Provide a structured comparison and recommendation
            
            Navigate intelligently between repositories and extract 
            comprehensive information for meaningful comparison.
            """, max_steps=20)
            
            print("✅ Comparative analysis completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_dynamic_content_handling():
    """Example: Handling dynamic content and JavaScript interactions"""
    print("\n⚡ Dynamic Content and JavaScript Handling")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://jsonplaceholder.typicode.com", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Explore this API documentation site with dynamic content:
            
            1. Navigate through different sections (posts, comments, albums, etc.)
            2. If there are interactive examples or try-it-now features, use them
            3. Test different API endpoints if there's a playground
            4. Extract sample request/response formats
            5. Look for rate limiting or authentication information
            6. Summarize the API's capabilities and provide usage examples
            
            Handle any dynamic loading, JavaScript interactions, or 
            asynchronous content updates intelligently.
            """)
            
            print("✅ Dynamic content handling completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_error_recovery_workflow():
    """Example: Workflow with built-in error recovery"""
    print("\n🔧 Error Recovery and Adaptive Workflow")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://www.wikipedia.org", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Perform a research task with error recovery:
            
            1. Search for "artificial intelligence history"
            2. Try to find a comprehensive article about AI history
            3. If the first result isn't suitable, try alternative searches:
               - "history of artificial intelligence"
               - "AI timeline"
               - "machine learning history"
            4. Extract key milestones and dates from the best article found
            5. If any links are broken or pages don't load, find alternative sources
            6. Compile a timeline of at least 5 major AI milestones
            
            Be resilient to page loading issues, broken links, or 
            unexpected page layouts. Adapt your strategy as needed.
            """, max_steps=25)
            
            print("✅ Error recovery workflow completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_accessibility_aware_interaction():
    """Example: Accessibility-aware web interaction"""
    print("\n♿ Accessibility-Aware Interaction")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://www.w3.org/WAI/WCAG21/quickref/", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Navigate this accessibility guidelines site with awareness:
            
            1. Use proper navigation methods (headings, landmarks, etc.)
            2. Look for ARIA labels and semantic HTML elements
            3. Extract key accessibility principles and guidelines
            4. Find examples of good and bad accessibility practices
            5. Look for tools or resources for accessibility testing
            6. Summarize the main accessibility requirements for web developers
            
            Interact with the page in ways that would work well with 
            screen readers and other assistive technologies.
            """)
            
            print("✅ Accessibility-aware interaction completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_performance_monitoring():
    """Example: Performance-aware automation with monitoring"""
    print("\n⚡ Performance-Aware Automation")
    
    api_key = os.getenv('NOVA_ACT_API_KEY')
    
    try:
        with NovaAct(starting_page="https://www.google.com/search?q=web+performance+tools", 
                    nova_act_api_key=api_key) as nova:
            
            result = nova.act("""
            Research web performance tools efficiently:
            
            1. Look for reputable sources about web performance testing
            2. Find information about tools like Lighthouse, WebPageTest, GTmetrix
            3. For each tool mentioned:
               - What it measures (speed, accessibility, SEO, etc.)
               - How to use it
               - Key metrics it provides
            4. Look for best practices for web performance optimization
            5. Extract actionable performance tips
            
            Work efficiently - don't spend too much time on any single page.
            Focus on extracting the most valuable information quickly.
            """, 
            timeout=120,  # Set reasonable timeout
            max_steps=10)  # Limit steps for efficiency
            
            print("✅ Performance-aware automation completed!")
            print(result.response)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all advanced Nova Act examples"""
    
    # Check for API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Error: NOVA_ACT_API_KEY environment variable not set")
        return
    
    print("🚀 Advanced Nova Act Examples")
    print("=" * 50)
    
    examples = [
        example_structured_data_extraction,
        example_multi_step_workflow,
        example_form_automation_with_validation,
        example_comparative_analysis,
        example_dynamic_content_handling,
        example_error_recovery_workflow,
        example_accessibility_aware_interaction,
        example_performance_monitoring
    ]
    
    for example in examples:
        try:
            example()
            print("\n" + "-" * 50)
        except Exception as e:
            print(f"❌ Example failed: {e}")
            print("-" * 50)
    
    print("\n🎉 All examples completed!")
    print("\n🎯 Nova Act Advanced Capabilities Demonstrated:")
    print("   ✅ Structured data extraction with JSON schemas")
    print("   ✅ Multi-step workflows with decision making")
    print("   ✅ Form automation with validation and error handling")
    print("   ✅ Comparative analysis across multiple sources")
    print("   ✅ Dynamic content and JavaScript interaction")
    print("   ✅ Error recovery and adaptive workflows")
    print("   ✅ Accessibility-aware web navigation")
    print("   ✅ Performance-conscious automation")


if __name__ == "__main__":
    main()
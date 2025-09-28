#!/usr/bin/env python3
"""
Simple test script for EnhancedDemoAgent that shows the agent's thinking process
"""

import os
import sys
import json
import logging
from enhanced_demo_agent import EnhancedDemoAgent, EnhancedDemoAgentArgs

# Configure logging to show all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

# Set all loggers to DEBUG level
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.DEBUG)

# Set environment variables for maximum verbosity
os.environ['AGISDK_DEBUG'] = '3'
os.environ['AGISDK_VERBOSE'] = '3'
os.environ['AGISDK_LOG_LEVEL'] = 'DEBUG'
os.environ['AGISDK_SHOW_THINKING'] = '1'
os.environ['AGISDK_SHOW_ACTIONS'] = '1'
os.environ['AGISDK_SHOW_OBSERVATIONS'] = '1'

def main():
    """Run a simple test of EnhancedDemoAgent"""
    print("🚀 Starting Simple Test of EnhancedDemoAgent")
    print("=" * 60)
    
    # Create a simple observation for testing
    observation = {
        "html": "<html><body><h1>Omnizon</h1><div>Welcome to Omnizon</div><div class='product'>Samsung Galaxy S24 Ultra</div><div class='product'>Samsung Galaxy Z Fold 6</div></body></html>",
        "url": "https://omnizon.com/",
        "screenshot": None,
        "axtree": "[root] Omnizon\n  [heading] Omnizon\n  [text] Welcome to Omnizon\n  [text] Samsung Galaxy S24 Ultra\n  [text] Samsung Galaxy Z Fold 6",
        "action_set": ["click('Samsung Galaxy S24 Ultra')", "click('Samsung Galaxy Z Fold 6')", "type('search_box', 'phone')", "submit('search_form')"]
    }
    
    try:
        # Create a mock OpenAI class that will intercept calls
        from openai import OpenAI as RealOpenAI
        
        class MockOpenAI:
            def __init__(self, *args, **kwargs):
                print("MockOpenAI client initialized")
                self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
                self.api_key = kwargs.get('api_key', 'sk-mock')
                
            @property
            def chat(self):
                return self
                
            @property
            def completions(self):
                return self
                
            def create(self, model=None, messages=None, temperature=None, max_tokens=None):
                # Print the messages to show agent thinking
                print("\n🧠 AGENT THINKING - LLM REQUEST:")
                print("-" * 60)
                
                # Print system message
                system_msg = next((m for m in messages if m["role"] == "system"), None)
                if system_msg:
                    print(f"[SYSTEM MESSAGE]:\n{system_msg['content'][:500]}...\n")
                
                # Print user message
                user_msg = next((m for m in messages if m["role"] == "user"), None)
                if user_msg:
                    print(f"[USER MESSAGE]:\n{user_msg['content'][:500]}...\n")
                
                # Return a mock response
                class MockResponse:
                    @property
                    def choices(self):
                        return [self]
                        
                    @property
                    def message(self):
                        return self
                        
                    @property
                    def content(self):
                        return "**Analysis:** I can see we're on the Omnizon homepage with two Samsung products listed.\n\n**Strategy:** I should examine the Samsung Galaxy S24 Ultra first to understand its features and pricing.\n\n**Action:** I'll click on Samsung Galaxy S24 Ultra to view its product details."
                
                return MockResponse()
        
        # Patch the OpenAI module
        import sys
        import types
        
        # Create a mock openai module
        mock_openai = types.ModuleType('openai')
        mock_openai.OpenAI = MockOpenAI
        
        # Save the original module
        original_openai = sys.modules.get('openai')
        
        # Replace with our mock
        sys.modules['openai'] = mock_openai
        
        # Create agent arguments
        agent_args = EnhancedDemoAgentArgs(
            model_name="gpt-4o",
            chat_mode=False,
            demo_mode=False,
            use_html=True,
            use_axtree=True,
            use_screenshot=True,
            system_message_handling="default",
            thinking_budget=1000,
            openai_api_key="sk-mock-api-key-for-testing-purposes-only",
            openrouter_api_key="sk-mock-openrouter-key-for-testing"
        )
        
        # Create the agent
        print("Creating EnhancedDemoAgent...")
        agent = agent_args.make_agent()
        
        # Get action from agent
        print("\n📝 Getting action from agent...")
        print("-" * 60)
        
        # Call get_action
        action = agent.get_action(observation)
        
        # Print the action
        print("\n🤖 AGENT ACTION:")
        print("-" * 60)
        # Handle StepInfo objects that aren't JSON serializable
        if hasattr(action, '__dict__'):
            action_dict = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v 
                          for k, v in action.__dict__.items()}
            print(json.dumps(action_dict, indent=2))
        else:
            print(str(action))
        
        # Restore original module
        if original_openai:
            sys.modules['openai'] = original_openai
            
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
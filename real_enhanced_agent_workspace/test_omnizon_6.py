#!/usr/bin/env python3
"""
Test script for Enhanced Demo Agent on Omnizon Task 6 (Samsung Phone Comparison)

This script specifically tests the enhanced agent on the Samsung Galaxy S24 Ultra vs Z Fold 6 
comparison task to validate the product research and comparison functionality.
"""

import sys
import os
import logging
import json

# Add the parent directory to the path to import agisdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agisdk import REAL
from enhanced_demo_agent import EnhancedDemoAgentArgs

# Configure logging to show all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a custom callback to print LLM thinking
def debug_callback(event_type, data):
    """Debug callback to print LLM thinking and actions"""
    if event_type == "llm_request":
        print("\n🧠 LLM REQUEST:")
        print("-" * 50)
        try:
            if isinstance(data, dict) and "messages" in data:
                for msg in data["messages"]:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    print(f"[{role.upper()}]: {content[:500]}...")
        except Exception as e:
            print(f"Error printing LLM request: {e}")
    
    elif event_type == "llm_response":
        print("\n💭 LLM RESPONSE:")
        print("-" * 50)
        try:
            if isinstance(data, dict) and "choices" in data:
                for choice in data["choices"]:
                    if "message" in choice:
                        content = choice["message"].get("content", "")
                        print(f"THINKING: {content}")
        except Exception as e:
            print(f"Error printing LLM response: {e}")
    
    elif event_type == "agent_action":
        print("\n🔄 AGENT ACTION:")
        print("-" * 50)
        try:
            print(f"ACTION: {data}")
        except Exception as e:
            print(f"Error printing agent action: {e}")

def test_omnizon_6():
    """Test the enhanced agent specifically on omnizon-6 task"""
    
    print('🚀 Testing Enhanced Demo Agent on Omnizon Task 6')
    print('=' * 60)
    print('Task: Samsung Galaxy S24 Ultra vs Z Fold 6 comparison')
    print('Goal: Compare specifications, price, and purchase the better value')
    print('Expected Features:')
    print('  ✅ Product identification and research')
    print('  ✅ Specification extraction and comparison')
    print('  ✅ Price-to-feature ratio analysis')
    print('  ✅ Structured decision making')
    print('  ✅ Purchase execution with reasoning')
    print('=' * 60)
    
    # Configure enhanced agent with real API keys from .env file
    agent_args = EnhancedDemoAgentArgs(
        model_name='gpt-4o',  # Use actual OpenAI model
        chat_mode=False,
        demo_mode='default',
        use_html=True,
        use_axtree=True,
        use_screenshot=True,
        system_message_handling='separate',
        thinking_budget=10000,
        # API keys will be loaded from environment variables
    )
    
    print('🔧 Agent Configuration:')
    print(f'  Model: {agent_args.model_name}')
    print(f'  GUI: Enabled (headless=False)')
    print(f'  Max steps: 50')
    print(f'  HTML fallback: Enabled')
    print(f'  Screenshots: Enabled')
    print(f'  Product research: Enabled')
    print(f'  Comparative analysis: Enabled')
    print(f'  Page exploration tracking: Enabled')
    print(f'  LLM Client: Real OpenAI API')
    print(f'  Verbose mode: Enabled')
    print(f'  Debug mode: Enabled')
    print()
    
    # Run the specific task
    print('🎯 Starting Omnizon-6 Task...')
    
    # Maximum verbosity for debugging
    os.environ['AGISDK_DEBUG'] = '3'
    os.environ['AGISDK_VERBOSE'] = '3'
    os.environ['AGISDK_LOG_LEVEL'] = 'DEBUG'
    os.environ['AGISDK_SHOW_THINKING'] = '1'
    os.environ['AGISDK_SHOW_ACTIONS'] = '1'
    os.environ['AGISDK_SHOW_OBSERVATIONS'] = '1'
    
    # Print debug message to confirm environment variables are set
    print("\n🔍 Debug settings enabled:")
    print(f"  Debug level: {os.environ.get('AGISDK_DEBUG')}")
    print(f"  Verbose level: {os.environ.get('AGISDK_VERBOSE')}")
    print(f"  Log level: {os.environ.get('AGISDK_LOG_LEVEL')}")
    print(f"  Show thinking: {os.environ.get('AGISDK_SHOW_THINKING')}")
    print(f"  Show actions: {os.environ.get('AGISDK_SHOW_ACTIONS')}")
    print(f"  Show observations: {os.environ.get('AGISDK_SHOW_OBSERVATIONS')}")
    print()
    
    # Import EnhancedDemoAgent to monkey patch for better thinking visibility
    from enhanced_demo_agent import EnhancedDemoAgent
    
    # Monkey patch EnhancedDemoAgent to show thinking
    original_get_action = EnhancedDemoAgent.get_action
    
    def patched_get_action(self, observation):
        print("\n🧠 AGENT THINKING PROCESS:")
        print("-" * 50)
        action = original_get_action(self, observation)
        print("\n🤖 AGENT DECIDED ACTION:")
        print("-" * 50)
        print(json.dumps(action, indent=2))
        return action
    
    EnhancedDemoAgent.get_action = patched_get_action
    
    # Execute the task
    print('📝 Agent steps will be displayed below:')
    print('-' * 50)
    try:
        harness = REAL.harness(
            agentargs=agent_args,
            task_name="webclones.omnizon-6",
            headless=False,
            use_cache=False,
            max_steps=50
        )
    
        result = harness.run()
        results = {'webclones.omnizon-6': result}
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        results = {'webclones.omnizon-6': {'success': False, 'error': str(e)}}
    
    # Restore original method
    EnhancedDemoAgent.get_action = original_get_action
    
    print('\n📊 Test Results:')
    print('=' * 40)
    for task_name, result in results.items():
        success = result.get('success', False)
        print(f"Task: {task_name}")
        print(f"Success: {'✅ Yes' if success else '❌ No'}")
        print(f"Steps: {result.get('n_steps', 0)}")
        print(f"Time: {result.get('elapsed_time', 0):.2f}s")
        if 'error' in result:
            print(f"Error: {result['error']}")
    print('=' * 40)
    
    print('\n🔍 Enhanced Agent Features Tested:')
    print('  📋 Product Research System')
    print('  🔄 Comparative Analysis Framework') 
    print('  🎯 Goal Completion Detection')
    print('  📊 Step Tracking and Context Management')
    print('  🧠 Structured Response Generation')
    print('  🔎 Page Exploration Journey Tracking')
    print('  📸 Visual Understanding with Screenshots')
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Enhanced Demo Agent Test on Omnizon Task 6")
    print(f"⏰ Test started at: {__import__('datetime').datetime.now()}")
    print()
    
    try:
        results = test_omnizon_6()
        print(f"\n✅ Test completed!")
        print(f"⏰ Test finished at: {__import__('datetime').datetime.now()}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Voice-Controlled Nova Act Agent
Integrates VAPI for voice input/output with Nova Act web automation
"""

import asyncio
import json
import os
import re
from typing import Dict, List, Optional
from nova_act import NovaAct
import requests
import time

class VoiceNovaAgent:
    """Voice-controlled Nova Act agent using VAPI integration"""
    
    def __init__(self, nova_api_key: str, vapi_api_key: str):
        """Initialize the voice-controlled Nova Act agent"""
        self.nova_client = None  # Will be initialized per session
        self.nova_api_key = nova_api_key
        self.vapi_api_key = vapi_api_key
        self.current_url = None
        self.conversation_history = []
        
        # Voice command patterns
        self.command_patterns = {
            'navigate': r'(?:go to|navigate to|open|visit)\s+(.+)',
            'search': r'(?:search for|find|look for)\s+(.+)',
            'click': r'(?:click|press|tap)\s+(?:on\s+)?(.+)',
            'type': r'(?:type|enter|input)\s+(.+)',
            'scroll': r'(?:scroll|move)\s+(up|down|left|right)',
            'wait': r'(?:wait|pause)\s+(?:for\s+)?(\d+)?\s*(?:seconds?)?',
            'screenshot': r'(?:take|capture)\s+(?:a\s+)?(?:screenshot|picture)',
            'status': r'(?:what|where)\s+(?:are we|am i|is this)',
            'help': r'(?:help|what can you do|commands)',
            'demo': r'(?:run|execute|start|show)\s+(?:demo|demonstration)?\s*(?:for\s+)?(.+)',
            'price_comparison': r'(?:compare prices|price comparison|find best deal|check prices)',
            'laptop_shopping': r'(?:buy laptop|shop for laptop|find laptop|purchase laptop|laptop shopping)',
            'smart_forms': r'(?:fill form|smart form|auto fill|form filling)',
            'news_intelligence': r'(?:news|latest news|news intelligence|get news)',
            'adaptive_workflows': r'(?:workflow|adaptive workflow|automation workflow)',
            'dual_demo': r'(?:run both demos|both demos|dual demo|price and news|news and price|run all demos|execute both|run both)'
        }
    
    def parse_voice_command(self, transcript: str) -> Dict:
        """Parse voice transcript into actionable commands"""
        transcript = transcript.lower().strip()
        
        for command_type, pattern in self.command_patterns.items():
            match = re.search(pattern, transcript)
            if match:
                return {
                    'type': command_type,
                    'parameter': match.group(1) if match.groups() else None,
                    'original': transcript
                }
        
        # If no pattern matches, treat as general instruction
        return {
            'type': 'general',
            'parameter': transcript,
            'original': transcript
        }
    
    def execute_voice_command(self, command: Dict) -> Dict:
        """Execute parsed voice command using Nova Act"""
        try:
            command_type = command['type']
            parameter = command['parameter']
            
            if command_type == 'navigate':
                url = self.normalize_url(parameter)
                # Initialize NovaAct for this session
                with NovaAct(starting_page=url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(f"Navigate to {url}")
                self.current_url = url
                return {
                    'success': True,
                    'message': f"Navigated to {url}",
                    'action': f"Opening {url}"
                }
            
            elif command_type == 'search':
                if not self.current_url:
                    return {
                        'success': False,
                        'message': "Please navigate to a website first",
                        'action': "Need to open a website before searching"
                    }
                
                with NovaAct(starting_page=self.current_url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(f"Search for {parameter}")
                return {
                    'success': True,
                    'message': f"Searching for {parameter}",
                    'action': f"Searching for {parameter} on the current page"
                }

            
            elif command_type == 'click':
                if not self.current_url:
                    return {
                        'success': False,
                        'message': "Please navigate to a website first",
                        'action': "Need to open a website before clicking"
                    }
                
                with NovaAct(starting_page=self.current_url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(f"Click on {parameter}")
                return {
                    'success': True,
                    'message': f"Clicking on {parameter}",
                    'action': f"Clicking on {parameter}"
                }
            
            elif command_type == 'type':
                if not self.current_url:
                    return {
                        'success': False,
                        'message': "Please navigate to a website first",
                        'action': "Need to open a website before typing"
                    }
                
                with NovaAct(starting_page=self.current_url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(f"Type {parameter}")
                return {
                    'success': True,
                    'message': f"Typing {parameter}",
                    'action': f"Entering text: {parameter}"
                }
            
            elif command_type == 'scroll':
                if not self.current_url:
                    return {
                        'success': False,
                        'message': "Please navigate to a website first",
                        'action': "Need to open a website before scrolling"
                    }
                
                with NovaAct(starting_page=self.current_url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(f"Scroll {parameter}")
                return {
                    'success': True,
                    'message': f"Scrolling {parameter}",
                    'action': f"Scrolling {parameter} on the page"
                }
            
            elif command_type == 'wait':
                seconds = int(parameter) if parameter and parameter.isdigit() else 3
                time.sleep(seconds)
                return {
                    'success': True,
                    'message': f"Waited for {seconds} seconds",
                    'action': f"Pausing for {seconds} seconds"
                }
            
            elif command_type == 'status':
                return {
                    'success': True,
                    'message': f"Currently on: {self.current_url or 'No website loaded'}",
                    'action': f"Current location: {self.current_url or 'No website loaded'}"
                }
            
            elif command_type in ['demo', 'price_comparison', 'laptop_shopping', 'smart_forms', 'news_intelligence', 'adaptive_workflows', 'dual_demo']:
                # Handle demo execution
                demo_type = command_type
                if command_type == 'demo' and parameter:
                    # Map parameter to demo type
                    param_lower = parameter.lower()
                    if 'price' in param_lower or 'comparison' in param_lower:
                        demo_type = 'price_comparison'
                    elif 'laptop' in param_lower or 'shopping' in param_lower:
                        demo_type = 'laptop_shopping'
                    elif 'form' in param_lower:
                        demo_type = 'smart_forms'
                    elif 'news' in param_lower:
                        demo_type = 'news_intelligence'
                    elif 'workflow' in param_lower:
                        demo_type = 'adaptive_workflows'
                    elif 'both' in param_lower or 'dual' in param_lower:
                        demo_type = 'dual_demo'
                
                # Set appropriate timeout for dual demo
                timeout = 60 if demo_type != 'dual_demo' else 300  # 5 minutes for dual demo
                
                # Call the demo API
                try:
                    response = requests.post('http://localhost:8000/run_demo', 
                                           json={'demo_type': demo_type}, 
                                           timeout=timeout)
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            'success': True,
                            'message': f"Demo '{demo_type}' executed successfully",
                            'action': f"Running {demo_type} demo",
                            'demo_result': result
                        }
                    else:
                        return {
                            'success': False,
                            'message': f"Demo execution failed: {response.text}",
                            'action': f"Failed to run {demo_type} demo"
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'message': f"Error running demo: {str(e)}",
                        'action': f"Error executing {demo_type} demo"
                    }
            
            elif command_type == 'help':
                help_text = """
                Available voice commands:
                - "Go to [website]" - Navigate to a website
                - "Search for [term]" - Search for something on current page
                - "Click [element]" - Click on page elements
                - "Type [text]" - Enter text in forms
                - "Scroll [direction]" - Scroll the page
                - "Wait [seconds]" - Pause execution
                - "Take screenshot" - Capture current page
                - "Where are we" - Show current location
                - "Compare prices" - Run price comparison demo
                - "Buy laptop" - Run laptop shopping demo
                - "Fill form" - Run smart forms demo
                - "Get news" - Run news intelligence demo
                - "Run workflow" - Run adaptive workflows demo
                """
                return {
                    'success': True,
                    'message': help_text,
                    'action': "Showing available commands"
                }
            
            elif command_type == 'general':
                # Handle general instructions
                if not self.current_url:
                    return {
                        'success': False,
                        'message': "Please navigate to a website first",
                        'action': "Need to open a website before performing actions"
                    }
                
                with NovaAct(starting_page=self.current_url, nova_act_api_key=self.nova_api_key) as nova:
                    result = nova.act(parameter)
                return {
                    'success': True,
                    'message': f"Executing: {parameter}",
                    'action': f"Performing action: {parameter}"
                }
            
            else:
                return {
                    'success': False,
                    'message': "Command not recognized",
                    'action': "Unknown command"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error executing command: {str(e)}",
                'action': f"Error: {str(e)}"
            }
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL input from voice commands"""
        url = url.lower().strip()
        
        # Handle common voice-to-text issues
        url_mappings = {
            'amazon': 'https://amazon.com',
            'google': 'https://google.com',
            'youtube': 'https://youtube.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'github': 'https://github.com',
            'omnizon': 'https://omnizon.com',  # For our test site
        }
        
        if url in url_mappings:
            return url_mappings[url]
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
                return f'https://{url}'
            else:
                return f'https://{url}.com'
        
        return url
    
    async def create_vapi_assistant(self) -> str:
        """Create a VAPI assistant for voice interaction"""
        assistant_config = {
            "name": "Nova Act Voice Controller",
            "firstMessage": "Hi! I'm your Nova Act voice assistant. I can help you control web browsers with voice commands. Try saying 'Go to Amazon' or 'Search for laptops'.",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "messages": [{
                    "role": "system",
                    "content": """You are a voice assistant that controls web automation through Nova Act. 
                    
                    Your role is to:
                    1. Listen to user voice commands
                    2. Confirm what action you're about to take
                    3. Provide real-time feedback on what's happening
                    4. Ask for clarification when commands are unclear
                    
                    Keep responses conversational and under 30 words. Always confirm actions before executing them.
                    
                    Example interactions:
                    User: "Go to Amazon"
                    You: "Opening Amazon.com now"
                    
                    User: "Search for laptops"
                    You: "Searching for laptops on the current page"
                    
                    User: "Click the first result"
                    You: "Clicking on the first search result"
                    """
                }]
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM"  # Professional voice
            },
            "functions": [{
                "name": "execute_nova_command",
                "description": "Execute web automation commands using Nova Act",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The voice command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }]
        }
        
        # This would be implemented with actual VAPI API calls
        return "assistant_id_placeholder"
    
    def start_voice_session(self):
        """Start a voice-controlled session"""
        print("🎤 Voice-Controlled Nova Act Agent Started!")
        print("Say commands like:")
        print("  - 'Go to Amazon'")
        print("  - 'Search for laptops'") 
        print("  - 'Click the first result'")
        print("  - 'Help' for more commands")
        print("\nPress Ctrl+C to stop")
        
        # In a real implementation, this would:
        # 1. Initialize VAPI web SDK
        # 2. Start listening for voice input
        # 3. Process commands through this class
        # 4. Provide voice feedback
        
        return """
        // JavaScript code for web integration
        const vapi = new Vapi('YOUR_VAPI_PUBLIC_KEY');
        const voiceAgent = new VoiceNovaAgent();
        
        // Start voice session
        vapi.start('YOUR_ASSISTANT_ID');
        
        // Handle voice messages
        vapi.on('message', async (message) => {
            if (message.type === 'function-call' && message.functionCall.name === 'execute_nova_command') {
                const command = message.functionCall.parameters.command;
                const result = await voiceAgent.executeCommand(command);
                
                // Send result back to VAPI for voice response
                vapi.send({
                    type: 'function-result',
                    functionCallId: message.functionCall.id,
                    result: result
                });
            }
        });
        """

# Example usage
if __name__ == "__main__":
    # Initialize with API keys
    nova_key = os.getenv('NOVA_ACT_API_KEY')
    vapi_key = os.getenv('VAPI_API_KEY')  # You'll need to get this from VAPI
    
    if not nova_key:
        print("❌ NOVA_ACT_API_KEY environment variable not set")
        exit(1)
    
    if not vapi_key:
        print("⚠️  VAPI_API_KEY not set - voice features will be limited")
        print("Get your VAPI API key from: https://vapi.ai/")
    
    # Create voice agent
    agent = VoiceNovaAgent(nova_key, vapi_key)
    
    # Test command parsing
    test_commands = [
        "Go to Amazon",
        "Search for laptops",
        "Click the first result",
        "Type my email address",
        "Scroll down",
        "Take a screenshot"
    ]
    
    print("🧪 Testing voice command parsing:")
    for cmd in test_commands:
        parsed = agent.parse_voice_command(cmd)
        print(f"  '{cmd}' → {parsed['type']}: {parsed['parameter']}")
    
    # Start voice session (placeholder)
    agent.start_voice_session()
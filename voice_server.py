#!/usr/bin/env python3
"""
Voice Nova Agent Server
Flask server that bridges web interface with Nova Act agent
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import asyncio
import json
import os
import logging
import subprocess
import sys
from voice_nova_agent import VoiceNovaAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Global agent instance
voice_agent = None

def initialize_agent():
    """Initialize the voice Nova agent"""
    global voice_agent
    
    nova_key = os.getenv('NOVA_ACT_API_KEY')
    vapi_key = os.getenv('VAPI_API_KEY', 'placeholder')
    
    if not nova_key:
        logger.error("NOVA_ACT_API_KEY environment variable not set")
        return False
    
    try:
        voice_agent = VoiceNovaAgent(nova_key, vapi_key)
        logger.info("Voice Nova Agent initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Voice Nova Agent: {e}")
        return False

@app.route('/')
def index():
    """Serve the voice interface"""
    try:
        with open('voice_web_interface.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Voice Nova Agent Server</h1>
        <p>Web interface file not found. Please ensure voice_web_interface.html is in the same directory.</p>
        <p>Available endpoints:</p>
        <ul>
            <li><code>/api/execute</code> - Execute voice commands</li>
            <li><code>/api/status</code> - Get agent status</li>
            <li><code>/api/webhook</code> - VAPI webhook endpoint</li>
        </ul>
        """

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a voice command"""
    if not voice_agent:
        return jsonify({
            'success': False,
            'message': 'Voice agent not initialized',
            'error': 'Agent not available'
        }), 500
    
    try:
        data = request.get_json()
        command_text = data.get('command', '')
        
        if not command_text:
            return jsonify({
                'success': False,
                'message': 'No command provided',
                'error': 'Missing command'
            }), 400
        
        # Parse the voice command
        parsed_command = voice_agent.parse_voice_command(command_text)
        logger.info(f"Parsed command: {parsed_command}")
        
        # Execute the command asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(voice_agent.execute_voice_command(parsed_command))
        loop.close()
        
        logger.info(f"Command result: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({
            'success': False,
            'message': f'Error executing command: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get agent status"""
    if not voice_agent:
        return jsonify({
            'initialized': False,
            'current_url': None,
            'message': 'Agent not initialized'
        })
    
    return jsonify({
        'initialized': True,
        'current_url': voice_agent.current_url,
        'message': 'Agent ready',
        'commands_available': list(voice_agent.command_patterns.keys())
    })

@app.route('/api/webhook', methods=['POST'])
def vapi_webhook():
    """Handle VAPI webhook events"""
    try:
        data = request.get_json()
        logger.info(f"VAPI webhook received: {data}")
        
        message = data.get('message', {})
        message_type = message.get('type')
        
        if message_type == 'function-call':
            function_call = message.get('functionCall', {})
            function_name = function_call.get('name')
            
            if function_name == 'execute_nova_command':
                # Extract command from function parameters
                parameters = function_call.get('parameters', {})
                command = parameters.get('command', '')
                
                if command and voice_agent:
                    # Parse and execute the command
                    parsed_command = voice_agent.parse_voice_command(command)
                    
                    # Execute asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(voice_agent.execute_voice_command(parsed_command))
                    loop.close()
                    
                    # Return result for VAPI
                    return jsonify({
                        'result': result
                    })
            
            elif function_name == 'run_demo':
                # Extract demo type from function parameters
                parameters = function_call.get('parameters', {})
                demo_type = parameters.get('demo_type', '')
                
                if demo_type:
                    # Call the run_demo endpoint internally
                    try:
                        from flask import current_app
                        with current_app.test_client() as client:
                            response = client.post('/run_demo', json={'demo_type': demo_type})
                            result = response.get_json()
                            
                            return jsonify({
                                'result': result
                            })
                    except Exception as e:
                        logger.error(f"Demo execution error: {e}")
                        return jsonify({
                            'result': {
                                'success': False,
                                'message': f"Demo execution failed: {str(e)}"
                            }
                        })
        
        # For other message types, just acknowledge
        return jsonify({'received': True})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            'error': str(e),
            'received': False
        }), 500

@app.route('/api/test', methods=['GET'])
def test_commands():
    """Test endpoint to verify command parsing"""
    if not voice_agent:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    test_commands = [
        "Go to Amazon",
        "Search for laptops", 
        "Click the first result",
        "Type hello world",
        "Scroll down",
        "Help"
    ]
    
    results = []
    for cmd in test_commands:
        parsed = voice_agent.parse_voice_command(cmd)
        results.append({
            'original': cmd,
            'parsed': parsed
        })
    
    return jsonify({
        'test_results': results,
        'agent_status': 'ready'
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration information"""
    return jsonify({
        'nova_api_configured': bool(os.getenv('NOVA_ACT_API_KEY')),
        'vapi_api_configured': bool(os.getenv('VAPI_API_KEY')),
        'server_running': True,
        'endpoints': {
            'execute': '/api/execute',
            'status': '/api/status',
            'webhook': '/api/webhook',
            'test': '/api/test',
            'config': '/api/config',
            'run_demo': '/run_demo'
        }
    })

@app.route('/run_demo', methods=['POST'])
def run_demo():
    """Execute a specific demo script"""
    try:
        data = request.get_json()
        demo_type = data.get('demo_type')
        
        if not demo_type:
            return jsonify({'error': 'demo_type is required'}), 400
        
        # Map demo types to their corresponding files
        demo_files = {
            'price_comparison': 'wow_demo_1_price_comparison.py',
            'smart_forms': 'wow_demo_2_smart_forms.py', 
            'news_intelligence': 'wow_demo_3_news_intelligence.py',
            'adaptive_workflows': 'wow_demo_4_adaptive_workflows.py',
            'laptop_shopping': 'wow_demo_5_omnizon_laptop_shopping.py',
            'dual_demo': 'dual_demo_runner.py'  # New dual demo option
        }
        
        if demo_type not in demo_files:
            return jsonify({'error': f'Unknown demo type: {demo_type}'}), 400
        
        demo_file = demo_files[demo_type]
        demo_path = os.path.join(os.path.dirname(__file__), demo_file)
        
        if not os.path.exists(demo_path):
            return jsonify({'error': f'Demo file not found: {demo_file}'}), 404
        
        logger.info(f"Executing demo: {demo_type} ({demo_file})")
        
        # Set timeout based on demo type - browser automation demos need more time
        if demo_type == 'news_intelligence':
            timeout_seconds = 300  # 5 minutes for comprehensive news analysis
        elif demo_type in ['laptop_shopping', 'price_comparison']:
            timeout_seconds = 120
        elif demo_type == 'dual_demo':
            timeout_seconds = 600  # 10 minutes for dual demo execution
        else:
            timeout_seconds = 30
        
        # Execute the demo in a subprocess
        result = subprocess.run(
            [sys.executable, demo_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'demo_type': demo_type,
                'output': result.stdout,
                'message': f'Demo {demo_type} executed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'demo_type': demo_type,
                'error': result.stderr,
                'message': f'Demo {demo_type} failed to execute'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Demo execution timed out',
            'message': 'Demo took too long to execute'
        }), 408
    except Exception as e:
        logger.error(f"Demo execution error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Internal server error during demo execution'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Voice Nova Agent Server...")
    
    # Check environment variables
    nova_key = os.getenv('NOVA_ACT_API_KEY')
    vapi_key = os.getenv('VAPI_API_KEY')
    
    print(f"Nova Act API Key: {'✅ Set' if nova_key else '❌ Not set'}")
    print(f"VAPI API Key: {'✅ Set' if vapi_key else '❌ Not set'}")
    
    if not nova_key:
        print("\n⚠️  Warning: NOVA_ACT_API_KEY not set")
        print("   Export your Nova Act API key: export NOVA_ACT_API_KEY=your_key_here")
    
    if not vapi_key:
        print("\n⚠️  Warning: VAPI_API_KEY not set")
        print("   Get your VAPI API key from: https://vapi.ai/")
        print("   Export it: export VAPI_API_KEY=your_key_here")
    
    # Initialize the agent
    if initialize_agent():
        print("\n✅ Voice Nova Agent initialized successfully!")
    else:
        print("\n❌ Failed to initialize Voice Nova Agent")
        print("   Server will still start but voice commands may not work")
    
    print("\n🌐 Server starting on http://localhost:5000")
    print("   Open this URL in your browser to use the voice interface")
    print("   API endpoints available at /api/*")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the Flask server
    # Change port to 8000 to match the frontend fetch request
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False  # Disable reloader to prevent double initialization
    )
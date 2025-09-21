# 🎤 Voice-Controlled Nova Act Agent

Transform your Nova Act web automation into a voice-controlled experience using VAPI (Voice AI Platform).

## 🌟 Features

- **Voice Commands**: Control web automation with natural speech
- **Real-time Feedback**: Get audio responses for all actions
- **Web Interface**: Beautiful browser-based control panel
- **Command Recognition**: Supports navigation, searching, clicking, typing, and more
- **Activity Logging**: Track all voice commands and results
- **Error Handling**: Graceful handling of failed commands

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_voice.txt
```

### 2. Set Up API Keys

```bash
# Nova Act API Key (already set)
export NOVA_ACT_API_KEY=your_nova_act_key

# VAPI API Key (get from https://vapi.ai/)
export VAPI_API_KEY=your_vapi_key
```

### 3. Create VAPI Assistant

1. Go to [VAPI Dashboard](https://vapi.ai/)
2. Create a new assistant with these settings:
   - **Name**: "Nova Act Voice Controller"
   - **Model**: OpenAI GPT-4o
   - **Voice**: ElevenLabs (professional voice)
   - **First Message**: "Hi! I'm your Nova Act voice assistant..."

3. Add this function to your assistant:

```json
{
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
}
```

### 4. Update Configuration

Edit `voice_web_interface.html` and replace:
- `YOUR_VAPI_PUBLIC_KEY` with your VAPI public key
- `YOUR_ASSISTANT_ID` with your assistant ID

### 5. Start the Server

```bash
python voice_server.py
```

### 6. Open Web Interface

Navigate to `http://localhost:5000` in your browser.

## 🎯 Voice Commands

### Navigation Commands
- "Go to Amazon" / "Open Google" / "Visit GitHub"
- "Navigate to [website]"

### Search Commands  
- "Search for laptops"
- "Find smartphones"
- "Look for books"

### Interaction Commands
- "Click the first result"
- "Press the login button" 
- "Tap the menu"

### Input Commands
- "Type hello world"
- "Enter my email"
- "Input the password"

### Navigation Commands
- "Scroll down" / "Move up"
- "Scroll to bottom"

### Utility Commands
- "Help" - Show available commands
- "Where are we" - Show current page
- "Wait 5 seconds" - Pause execution

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Browser   │    │ VAPI Service │    │  Nova Act API   │
│                 │    │              │    │                 │
│ Voice Interface │◄──►│ Speech-to-   │◄──►│ Web Automation  │
│ (HTML/JS)       │    │ Text & TTS   │    │ Engine          │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │                       │                    │
         ▼                       ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                Flask Server (voice_server.py)              │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ Voice Commands  │    │     Nova Act Integration        │ │
│  │ Parser          │◄──►│                                 │ │
│  │                 │    │ - Command Execution             │ │
│  └─────────────────┘    │ - Browser Automation            │ │
│                         │ - Result Processing             │ │
│                         └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
agisdk/
├── voice_nova_agent.py      # Core voice agent logic
├── voice_server.py          # Flask server for web interface
├── voice_web_interface.html # Browser-based voice control UI
├── requirements_voice.txt   # Python dependencies
└── README_VOICE.md         # This documentation
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
NOVA_ACT_API_KEY=your_nova_act_api_key

# Required for voice features
VAPI_API_KEY=your_vapi_api_key

# Optional
FLASK_ENV=development
FLASK_DEBUG=1
```

### VAPI Assistant Configuration

```json
{
  "name": "Nova Act Voice Controller",
  "firstMessage": "Hi! I'm your Nova Act voice assistant. I can help you control web browsers with voice commands. Try saying 'Go to Amazon' or 'Search for laptops'.",
  "model": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "messages": [{
      "role": "system",
      "content": "You are a voice assistant that controls web automation through Nova Act. Keep responses conversational and under 30 words. Always confirm actions before executing them."
    }]
  },
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM"
  }
}
```

## 🧪 Testing

### Test Command Parsing

```bash
curl -X GET http://localhost:5000/api/test
```

### Test Command Execution

```bash
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "Go to Amazon"}'
```

### Check Server Status

```bash
curl -X GET http://localhost:5000/api/status
```

## 🔍 Troubleshooting

### Common Issues

1. **"VAPI not initialized"**
   - Check your VAPI API key is set correctly
   - Verify the assistant ID in the web interface

2. **"Nova Act API key not set"**
   - Export your Nova Act API key: `export NOVA_ACT_API_KEY=your_key`

3. **Voice commands not recognized**
   - Check microphone permissions in browser
   - Ensure stable internet connection
   - Try speaking more clearly

4. **Commands execute but no browser action**
   - Verify Nova Act API key is valid
   - Check the target website is accessible
   - Review server logs for errors

### Debug Mode

Start the server with debug logging:

```bash
FLASK_DEBUG=1 python voice_server.py
```

### Browser Console

Open browser developer tools (F12) to see JavaScript logs and errors.

## 🚀 Advanced Usage

### Custom Voice Commands

Add new command patterns in `voice_nova_agent.py`:

```python
self.command_patterns.update({
    'custom_action': r'(?:do|perform)\s+(.+)',
    'complex_task': r'(?:complete|finish)\s+(.+)\s+task'
})
```

### Webhook Integration

Set up VAPI webhook to point to your server:
```
https://your-domain.com/api/webhook
```

### Production Deployment

1. Use a production WSGI server (gunicorn)
2. Set up HTTPS for secure voice transmission
3. Configure proper CORS settings
4. Add authentication if needed

## 📚 API Reference

### REST Endpoints

- `GET /` - Web interface
- `POST /api/execute` - Execute voice command
- `GET /api/status` - Get agent status
- `POST /api/webhook` - VAPI webhook endpoint
- `GET /api/test` - Test command parsing
- `GET /api/config` - Get configuration info

### Voice Command Format

```json
{
  "command": "Go to Amazon"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Navigated to https://amazon.com",
  "action": "Opening Amazon"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add voice command patterns or improve recognition
4. Test with various voice inputs
5. Submit a pull request

## 📄 License

This voice integration extends the existing AGI SDK license.

## 🆘 Support

- **VAPI Documentation**: https://docs.vapi.ai/
- **Nova Act Issues**: Check Nova Act documentation
- **Voice Integration**: Create an issue in this repository

---

**Ready to control the web with your voice? Start speaking to your browser! 🎤✨**
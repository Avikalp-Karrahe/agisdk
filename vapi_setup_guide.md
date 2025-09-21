# VAPI Voice Agent Setup Guide for Voice Coach RL Dashboard

## Prerequisites

1. **VAPI Account**: Sign up at [vapi.ai](https://vapi.ai/)
2. **Nova Act API Key**: Get from [Nova Act dashboard](https://nova-act.com/)
3. **Running Services**: Ensure both servers are running:
   - Voice Coach RL Dashboard: `http://localhost:8080`
   - Voice Server Backend: `http://localhost:5000`

## Step 1: Create VAPI Assistant

### 1.1 Login to VAPI Dashboard
- Go to [vapi.ai](https://vapi.ai/) and login
- Navigate to "Assistants" section
- Click "Create New Assistant"

### 1.2 Basic Configuration
```json
{
  "name": "Voice Coach RL Agent",
  "model": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "maxTokens": 150
  },
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM"
  }
}
```

### 1.3 System Message
Copy the entire content from `vapi_system_prompt.md` into the "System Message" field.

### 1.4 Functions Configuration
Copy the JSON from `vapi_functions_config.json` into the "Functions" section.

## Step 2: Configure Webhook

### 2.1 Set Webhook URL
In your VAPI assistant settings, set the webhook URL to:
```
http://localhost:5000/api/webhook
```

### 2.2 Enable Function Calling
- Enable "Function Calling" in assistant settings
- Set "Function Calling Mode" to "Auto"

## Step 3: Update Frontend Configuration

### 3.1 Get Your Keys
From VAPI dashboard, copy:
- **Public Key**: Found in "API Keys" section
- **Assistant ID**: Found in your assistant's settings

### 3.2 Update Voice Interface
Edit `voice-coach-rl/src/components/ui/voice-interface.tsx`:

```typescript
// Add VAPI integration
const VAPI_PUBLIC_KEY = 'your_vapi_public_key_here';
const ASSISTANT_ID = 'your_assistant_id_here';

// Initialize VAPI in useEffect
useEffect(() => {
  if (typeof window !== 'undefined' && window.Vapi) {
    const vapi = new window.Vapi(VAPI_PUBLIC_KEY);
    
    vapi.on('call-start', () => {
      setIsListening(true);
    });
    
    vapi.on('call-end', () => {
      setIsListening(false);
    });
    
    vapi.on('message', (message) => {
      if (message.type === 'transcript' && message.role === 'user') {
        setTranscript(message.transcript);
      }
    });
  }
}, []);
```

### 3.3 Add VAPI SDK
Add to `voice-coach-rl/index.html`:
```html
<script src="https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/dist/index.js"></script>
```

## Step 4: Backend Integration

### 4.1 Update Environment Variables
Create/update `.env` file:
```bash
NOVA_ACT_API_KEY=your_nova_act_key_here
VAPI_API_KEY=your_vapi_private_key_here
```

### 4.2 Update Voice Server
The `voice_server.py` already includes webhook handling. Ensure these endpoints work:
- `POST /api/webhook` - Receives VAPI function calls
- `POST /api/execute` - Executes Nova Act commands
- `GET /api/status` - Returns agent status

## Step 5: Test the Integration

### 5.1 Start All Services
```bash
# Terminal 1: Start Voice Server
cd /path/to/agisdk
python voice_server.py

# Terminal 2: Start React Dashboard
cd /path/to/agisdk/voice-coach-rl
npm run dev
```

### 5.2 Test Voice Commands
Try these commands:
- "How is the agent performing?"
- "Increase exploration rate to 0.4"
- "Go to Amazon and search for laptops"
- "Take a screenshot"
- "Reset the training parameters"

## Step 6: Advanced Configuration

### 6.1 Voice Settings
Optimize for your use case:
```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.5,
    "similarityBoost": 0.8,
    "style": 0.2,
    "useSpeakerBoost": true
  }
}
```

### 6.2 Model Fine-tuning
```json
{
  "model": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "maxTokens": 150,
    "frequencyPenalty": 0.1,
    "presencePenalty": 0.1
  }
}
```

### 6.3 Conversation Settings
```json
{
  "firstMessage": "Hello! I'm your Voice Coach RL assistant. I can help you control the RL agent, monitor performance, and execute web automation commands. What would you like me to do?",
  "endCallMessage": "Training session ended. Great work!",
  "recordingEnabled": false,
  "hipaaEnabled": false
}
```

## Troubleshooting

### Common Issues

1. **"VAPI not initialized"**
   - Check API keys are correct
   - Ensure VAPI SDK is loaded
   - Verify assistant ID is valid

2. **"Function calls not working"**
   - Check webhook URL is accessible
   - Verify function definitions match
   - Ensure backend server is running

3. **"Voice not responding"**
   - Check microphone permissions
   - Verify voice provider settings
   - Test with simple commands first

4. **"Nova Act commands failing"**
   - Verify Nova Act API key
   - Check internet connection
   - Ensure target websites are accessible

### Debug Mode
Enable debug logging in voice server:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **API Keys**: Never expose private keys in frontend code
2. **Webhook Security**: Consider adding authentication to webhook endpoint
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Input Validation**: Validate all voice commands before execution

## Performance Optimization

1. **Response Time**: Keep system prompts concise
2. **Function Calls**: Minimize function call complexity
3. **Voice Quality**: Use high-quality voice models for better UX
4. **Error Handling**: Implement robust error recovery

Your VAPI voice agent is now ready to control the Voice Coach RL dashboard with natural voice commands!
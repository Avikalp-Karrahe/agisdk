# 🎯 AGI SDK Demo Cheat Sheet

## 🚀 Quick Start Commands

### Voice Triggers (Say these to Ava)
| **Demo Type** | **Voice Commands** | **What It Does** |
|---------------|-------------------|------------------|
| **Price Comparison** | "price comparison", "compare prices", "find best price", "price check", "shopping comparison" | Searches Amazon & Best Buy for wireless headphones, compares prices |
| **Smart Forms** | "fill form", "form automation", "complete form", "form filling", "auto fill" | Automatically fills out web forms |
| **News Intelligence** | "news analysis", "trending topics", "sentiment analysis", "news intelligence", "analyze news" | Analyzes current news and trends |
| **Adaptive Workflows** | "adaptive workflow", "smart automation", "intelligent workflow", "dynamic workflow", "workflow adaptation" | Demonstrates intelligent task automation |
| **Laptop Shopping** | "buy laptop", "shop for laptop", "find laptop", "purchase laptop", "laptop shopping" | Searches Omnizon for laptops, adds to cart, proceeds to checkout |

---

## 🖥️ Dashboard Layout

```
┌─────────────────┬─────────────────┬─────────────────┐
│   LEFT COLUMN   │  MIDDLE COLUMN  │  RIGHT COLUMN   │
│                 │                 │                 │
│ • Voice Interface│ • Agent Thinking│ • RealBench     │
│ • RL Controls   │ • Demo Results  │   Dashboard     │
│ • Parameters    │ • Execution Log │ • Metrics       │
│                 │                 │ • Leaderboard   │
└─────────────────┴─────────────────┴─────────────────┘
```

### Middle Column Features
- **Real-time execution status** with animated indicators
- **Demo results display** with structured data
- **Price comparison breakdown** with savings calculations
- **Screenshot indicators** showing captured evidence
- **Error handling** with clear failure messages

---

## 🎤 Voice Interface Features

### Ava's Voice Feedback
When demos complete, Ava automatically speaks results:
- **Price Comparison**: *"I found prices for wireless headphones. On Amazon, the best price is $37.33. On Best Buy, the best price is $45.99. Amazon has the better deal, saving you $8.66."*
- **Other Demos**: *"Demo [type] completed successfully."*

### Voice Settings
- **Rate**: 0.9 (slightly slower for clarity)
- **Pitch**: 1.1 (slightly higher for female voice)
- **Volume**: 0.8 (comfortable listening level)
- **Voice**: Automatically selects female voice if available

---

## 🔧 API Endpoints

### Direct API Calls
```bash
# Price Comparison Demo
curl -X POST http://localhost:8000/run_demo \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "price_comparison"}'

# Smart Forms Demo
curl -X POST http://localhost:8000/run_demo \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "smart_forms"}'

# News Intelligence Demo
curl -X POST http://localhost:8000/run_demo \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "news_intelligence"}'

# Adaptive Workflows Demo
curl -X POST http://localhost:8000/run_demo \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "adaptive_workflows"}'

# Laptop Shopping Demo
curl -X POST http://localhost:8000/run_demo \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "laptop_shopping"}'
```

---

## 🎮 Manual Demo Execution

### Command Line Execution
```bash
# Set API Key
export NOVA_ACT_API_KEY=36ce9fc1-6d75-4955-929f-260cc66c3c28

# Run Price Comparison Demo
python wow_demo_1_price_comparison.py

# Run Smart Forms Demo
python wow_demo_2_smart_forms.py

# Run News Intelligence Demo
python wow_demo_3_news_intelligence.py

# Run Adaptive Workflows Demo
python wow_demo_4_adaptive_workflows.py

# Run Laptop Shopping Demo
python wow_demo_5_omnizon_laptop_shopping.py
```

---

## 📊 Demo Results Structure

### Price Comparison Response
```json
{
  "success": true,
  "data": {
    "comparison_results": {
      "amazon": {
        "price": "37.33",
        "product_name": "Wireless Headphones",
        "url": "https://amazon.com/..."
      },
      "bestbuy": {
        "price": "45.99",
        "product_name": "Wireless Headphones",
        "url": "https://bestbuy.com/..."
      }
    },
    "screenshots": [
      "screenshot_amazon_1234567890.png",
      "screenshot_bestbuy_1234567890.png"
    ],
    "execution_time": 45.2
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Demo execution timed out",
  "message": "Demo took too long to execute"
}
```

---

## 🔍 Troubleshooting

### Common Issues & Solutions

| **Issue** | **Solution** |
|-----------|--------------|
| Demo timeout | Demos take 30-60 seconds; be patient |
| Voice not working | Check browser permissions for microphone |
| No voice feedback | Ensure speakers/headphones are connected |
| API key error | Verify `NOVA_ACT_API_KEY` is set correctly |
| Server not responding | Check if `python voice_server.py` is running |
| Frontend not loading | Check if `npm run dev` is running in voice-coach-rl/ |

### Server Status Check
```bash
# Check voice server (should show port 8000)
curl http://localhost:8000/health

# Check frontend (should show React app)
curl http://localhost:5173
```

---

## 🌐 URLs & Ports

| **Service** | **URL** | **Purpose** |
|-------------|---------|-------------|
| **Frontend Dashboard** | http://localhost:5173 | Main UI with voice interface |
| **Voice Server API** | http://localhost:8000 | Demo execution backend |
| **Health Check** | http://localhost:8000/health | Server status |

---

## 🎯 Demo Flow Sequence

1. **Voice Input** → User says trigger phrase
2. **Detection** → Agent Thinking Panel detects demo type
3. **API Call** → Frontend calls voice server API
4. **Execution** → Browser automation runs (30-60 seconds)
5. **Display** → Results appear in middle column
6. **Voice Output** → Ava speaks the results

---

## 🔑 Environment Setup

### Required Environment Variables
```bash
export NOVA_ACT_API_KEY=36ce9fc1-6d75-4955-929f-260cc66c3c28
```

### Required Services
- **Voice Server**: `python voice_server.py` (port 8000)
- **Frontend**: `npm run dev` in voice-coach-rl/ (port 5173)

---

## 🎨 Visual Indicators

### Execution States
- 🟡 **Running**: Yellow pulsing dot with "Running..." text
- 🟢 **Success**: Green dot with structured results
- 🔴 **Failed**: Red dot with error message
- 📸 **Screenshots**: Camera emoji with count

### Price Comparison Display
- **Amazon**: Orange text with price
- **Best Buy**: Blue text with price
- **Best Deal**: Green highlight with savings amount

---

## 💡 Pro Tips

1. **Wait for completion**: Demos take time due to real browser automation
2. **Check middle column**: All results appear in the Agent Thinking Panel
3. **Listen for Ava**: Voice feedback confirms successful completion
4. **Use voice commands**: More natural than manual API calls
5. **Monitor console**: Check browser dev tools for detailed logs

---

## 🚨 Emergency Commands

```bash
# Kill all processes if stuck
pkill -f "python voice_server.py"
pkill -f "npm run dev"

# Restart services
cd /path/to/agisdk
python voice_server.py &

cd voice-coach-rl
npm run dev &
```

---

*Last updated: $(date)*
*AGI SDK Version: 0.2.0*
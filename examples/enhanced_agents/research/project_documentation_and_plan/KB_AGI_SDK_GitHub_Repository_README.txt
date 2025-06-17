# GitHub - agi-inc/agisdk: AGI SDK

🚀 AGI SDK


  📄 Paper • 
  📝 Blog • 
  🏢 AGI Inc • 
  🏆 Leaderboard


  
  
  
  


  Build, evaluate, and level up your AI agents — for the real web.


  
      
        
          
            
          
        
        
        
          
          
            
          
        
      

✨ What is AGI SDK?
AGI SDK is a toolkit for building and evaluating AI browser agents in real-world environments.
It powers REAL Bench — the first high-fidelity benchmark for AI agents navigating modern websites like Amazon, DoorDash, Airbnb, and more.
🔹 Train agents to browse and interact with real apps
🔹 Benchmark agents with robust, standardized tasks
🔹 Submit to the leaderboard and see how your agents stack up!

TL;DR: Go from “idea” to “benchmarked agent” in <60 seconds

🛠️ Installation (30 s)
# Install the SDK
pip install agisdk

# Install Playwright browser dependencies
playwright install --force

# Set your LLM API key (for evaluation)
export OPENAI_API_KEY="your-api-key"   # any supported provider key works
✅ Supports OpenAI, Anthropic, OpenRouter, and custom models! 
On Apple Silicon run brew install --cask playwright first.
⏱️ 60-second Quick-Start
Here's a minimal example to get you started for benchmarking an AI agent on the REAL Bench environment:
from agisdk import REAL

harness = REAL.harness(
    model="gpt-4o",       # any LLM tag
    task_type="omnizon",  # Amazon-like store
    headless=False        # watch it click in real-time!
)

print(harness.run())      # 🎉
Need more control? See full examples ›
🔥 Features

Full-stack web replicas of top real-world apps (Amazon, Uber, Gmail, Airbnb, etc.)
Robust agent API: Observations, Actions, Memory, Errors
Leaderboard integration (REAL Bench)
Customizable harness: plug your own agents
Multi-model support: OpenAI, Anthropic, OpenRouter, or your own model
Parallel evaluation for faster experiments

Running Custom Agents
Checkout the README.md in the example folder. There are three examples of custom agents in the example directory:

example/starter.py: A simple example to get you started
example/custom.py: A more complex example with a custom agent
example/nova.py: For running custom agents which already have browsers running (in this case, Amazon NovaAct)

Additionally, there is a hackable example in example/hackable.py which is a can be configured for better performance and starting of.
Local Development
Only if you want to develop locally, you can install from source:
# Clone the repository
git clone https://github.com/agi-inc/agisdk.git
cd agisdk

# Install in development mode
pip install -e .
🌐 Available Tasks
The AGI SDK includes high-fidelity, fully-deterministic websites for agents to explore. These are modern web stack sites (React + Next.js) with rich functionality for core user flows, realistic mock data, and consistent behavior for testing and evaluation.
The benchmark includes these environments:



App Clone
Task Prefix
Example Use Case




🛒 Amazon → Omnizon
webclones.omnizon-*
Buy a laptop, find a gift


🍔 DoorDash → DashDish
webclones.dashdish-*
Order dinner


✈️ United → FlyUnified
webclones.fly-unified-*
Book a flight


🏡 Airbnb → Staynb
webclones.staynb-*
Reserve accommodation


📅 Google Calendar → GoCalendar
webclones.gocalendar-*
Schedule a meeting


📬 Gmail → GoMail
webclones.gomail-*
Compose an email


🍽️ OpenTable → OpenDining
webclones.opendining-*
Book a restaurant


👔 LinkedIn → NetworkIn
webclones.networkin-*
Accept a connection


🚗 Uber → Udriver
webclones.udriver-*
Book a ride


💼 UpWork → TopWork
webclones.topwork-*
Find a freelance gig


🏠 Zillow → Zilloft
webclones.zilloft-*
Browse houses



Each task comes with human-written goals designed to stress-test agent capabilities.
🔑 API Keys
To use models from other providers, set their respective API keys:
# For Anthropic models (like sonnet-3.7)
export ANTHROPIC_API_KEY="your-anthropic-api-key"
👁️ Observation Structure
Your agent gets access to the following observation structure:
{
    'chat_messages': [...],          # History of chat messages
    'goal': "...",                   # Text description of the goal
    'goal_object': [...],            # Structured goal object with text and images
    'open_pages_urls': [...],        # List of open page URLs
    'active_page_index': 0,          # Index of the active page
    'url': "...",                    # Current URL
    'screenshot': np.array(...),     # Screenshot as numpy array
    'dom_object': {...},             # DOM structure
    'axtree_object': {...},          # Accessibility tree
    'extra_element_properties': {...}, # Additional element properties
    'focused_element_bid': "...",    # ID of the focused element
    'last_action': "...",            # Last action performed
    'last_action_error': "...",      # Error from last action (if any)
    'elapsed_time': 0.0,             # Time elapsed in the episode
    'browser': {...}                 # Playwright browser object (for direct control)
}
🎯 Action
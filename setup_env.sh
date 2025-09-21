#!/bin/bash
# Nova Act Environment Setup Script
# Usage: source setup_env.sh

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Nova Act API key loaded successfully!"
    echo "🚀 You can now run any Nova Act demo:"
    echo "   python wow_demo_1_price_comparison.py"
    echo "   python wow_demo_2_smart_forms.py"
    echo "   python wow_demo_3_news_intelligence.py"
    echo "   python wow_demo_4_adaptive_workflows.py"
else
    echo "❌ .env file not found. Please create it with your NOVA_ACT_API_KEY."
fi
#!/usr/bin/env python3
"""
Claude 3.5 Sonnet REAL Benchmark Submission

This script submits Claude 3.5 Sonnet's performance to the REAL benchmark leaderboard.
Make sure to set both REAL_API_KEY and ANTHROPIC_API_KEY environment variables.
"""

import os
from agisdk import REAL

def submit_claude_to_leaderboard():
    """Submit Claude 3.5 Sonnet results to the REAL benchmark leaderboard"""
    
    # Check for Anthropic API key (REAL API key not needed with existing run_id)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not anthropic_api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set!")
        print("Please get your Anthropic API key and set it:")
        print("export ANTHROPIC_API_KEY='your-anthropic-api-key-here'")
        return
    
    print("🚀 Starting Claude 3.5 Sonnet REAL Benchmark Submission...")
    print(f"🆔 Using Run ID: f1a58d7a-d697-414c-8d04-7431894011d6")
    print(f"🤖 Using Anthropic API Key: {anthropic_api_key[:8]}...")
    
    # Configure harness for Claude 3.5 Sonnet leaderboard submission
    harness = REAL.harness(
        # Model configuration - Claude 3.5 Sonnet (Latest Available)
        model="claude-3-5-sonnet-20241022",      # Claude 3.5 Sonnet v2 (Latest)
        
        # Leaderboard submission with your specific run ID
        run_id="f1a58d7a-d697-414c-8d04-7431894011d6",  # Your specific run ID
        leaderboard=True,                         # Enable leaderboard submission
        
        # Task configuration - run all tasks for complete evaluation
        # task_type="omnizon",                    # Uncomment to run specific task type
        # task_name="webclones.omnizon-1",        # Uncomment to run specific task
        
        # Execution options
        num_workers=4,                            # Parallel execution for speed
        headless=True,                            # Run without browser GUI
        max_steps=25,                             # Maximum steps per task
        
        # Browser configuration
        browser_dimensions=(1280, 720),           # Standard browser size
        
        # Observation options (optimized for Claude)
        use_html=False,                           # Disable HTML for speed
        use_axtree=True,                          # Keep accessibility tree
        use_screenshot=True,                      # Keep screenshots for Claude's vision
        
        # Results configuration
        results_dir="./claude_leaderboard_results", # Separate results directory
        use_cache=True,                           # Use cached results when available
        force_refresh=False                       # Don't force re-run
    )
    
    print("⚙️  Claude 3.5 Sonnet harness configured successfully!")
    print("📝 Submission Details:")
    print(f"   • Model: Claude 3.5 Sonnet v2 (Latest Available)")
    print(f"   • Run ID: f1a58d7a-d697-414c-8d04-7431894011d6")
    print(f"   • Tasks: All 112 REAL benchmark tasks")
    print(f"   • Workers: 4 parallel")
    print(f"   • Results Dir: ./claude_leaderboard_results")
    print(f"   • Vision: Enabled (screenshots + accessibility tree)")
    
    # Run the evaluation
    print("\n🏃 Starting Claude 3.5 Sonnet benchmark evaluation...")
    print("This will take approximately 2-4 hours depending on your setup.")
    print("Claude's multimodal capabilities should help with visual tasks!")
    print("Results will be automatically submitted to the leaderboard during execution.")
    
    try:
        results = harness.run()
        
        print("\n✅ Claude 3.5 Sonnet leaderboard submission completed successfully!")
        print("🎉 Your Claude results have been submitted to the REAL benchmark leaderboard!")
        print("📊 Check your results at: https://realevals.xyz")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during Claude submission: {e}")
        print("Please check your API keys and internet connection.")
        print("Make sure both REAL_API_KEY and ANTHROPIC_API_KEY are set correctly.")
        return None

if __name__ == "__main__":
    # Set your API keys here or use environment variables
    # os.environ["REAL_API_KEY"] = "your-real-api-key-here"        # Uncomment and add your key
    # os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key-here"  # Uncomment and add your key
    
    results = submit_claude_to_leaderboard()
    
    if results:
        print(f"\n📈 Claude 3.5 Sonnet Final Results Summary:")
        print(f"   • Total tasks completed: {len(results) if results else 'N/A'}")
        print(f"   • Check detailed results at: https://realevals.xyz")
        print(f"   • Claude 3.5 Sonnet's advanced capabilities should show excellent performance!")
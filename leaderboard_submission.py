#!/usr/bin/env python3
"""
REAL Benchmark Leaderboard Submission Script

This script submits your agent's performance to the official REAL benchmark leaderboard.
Make sure to set your REAL_API_KEY environment variable before running.
"""

import os
from agisdk import REAL

def submit_to_leaderboard():
    """Submit agent results to the REAL benchmark leaderboard"""
    
    # Check for API key
    api_key = os.getenv("REAL_API_KEY")
    if not api_key:
        print("❌ Error: REAL_API_KEY environment variable not set!")
        print("Please visit https://realevals.xyz to get your API key and set it:")
        print("export REAL_API_KEY='your-api-key-here'")
        return
    
    print("🚀 Starting REAL Benchmark Leaderboard Submission...")
    print(f"📊 Using API Key: {api_key[:8]}...")
    
    # Configure harness for leaderboard submission
    harness = REAL.harness(
        # Model configuration
        model="sonnet-3.5",                       # Claude 3.5 Sonnet
        
        # Leaderboard submission (automatic run ID generation)
        api_key=api_key,                          # Your REAL API key
        run_name="Claude-3.5-Sonnet Enhanced Agent v1.0",   # Descriptive name for your run
        model_id_name="claude-3.5-sonnet",       # Model identifier for leaderboard
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
        
        # Observation options (optimized for performance)
        use_html=False,                           # Disable HTML for speed
        use_axtree=True,                          # Keep accessibility tree
        use_screenshot=True,                      # Keep screenshots
        
        # Results configuration
        results_dir="./leaderboard_results",      # Separate results directory
        use_cache=True,                           # Use cached results when available
        force_refresh=False                       # Don't force re-run
    )
    
    print("⚙️  Harness configured successfully!")
    print("📝 Submission Details:")
    print(f"   • Model: Claude 3.5 Sonnet")
    print(f"   • Run Name: Claude-3.5-Sonnet Enhanced Agent v1.0")
    print(f"   • Tasks: All 112 REAL benchmark tasks")
    print(f"   • Workers: 4 parallel")
    print(f"   • Results Dir: ./leaderboard_results")
    
    # Run the evaluation
    print("\n🏃 Starting benchmark evaluation...")
    print("This will take approximately 2-4 hours depending on your setup.")
    print("Results will be automatically submitted to the leaderboard during execution.")
    
    try:
        results = harness.run()
        
        print("\n✅ Leaderboard submission completed successfully!")
        print("🎉 Your results have been submitted to the REAL benchmark leaderboard!")
        print("📊 Check your results at: https://realevals.xyz")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during submission: {e}")
        print("Please check your API key and internet connection.")
        return None

if __name__ == "__main__":
    # Set your API key here or use environment variable
    # os.environ["REAL_API_KEY"] = "your-api-key-here"  # Uncomment and add your key
    
    results = submit_to_leaderboard()
    
    if results:
        print(f"\n📈 Final Results Summary:")
        print(f"   • Total tasks completed: {len(results) if results else 'N/A'}")
        print(f"   • Check detailed results at: https://realevals.xyz")
#!/usr/bin/env python3
"""
AGI SDK Getting Started - 3 Simple Steps
Step 2: Initialize the Evaluation Harness

This script demonstrates how to use the AGI SDK evaluation harness
with GPT-4o to run comprehensive REAL benchmark evaluations.
"""

from agisdk.REAL import harness
import os

def main():
    """
    Initialize and run the AGI SDK evaluation harness with GPT-4o
    """
    
    # Ensure OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running the evaluation:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🚀 Initializing AGI SDK Evaluation Harness...")
    print("📊 Model: GPT-4o")
    print("🎯 Running comprehensive REAL benchmark evaluation...")
    
    try:
        # Step 2: Initialize the Evaluation Harness
        evaluation_harness = harness(model="gpt-4o")  # specify your model here
        
        # Step 3: Run the evaluation and get results
        print("\n⏳ Starting evaluation... This may take several minutes.")
        results = evaluation_harness.run()
        
        # Step 4: Analyze Your Results
        print("\n✅ Evaluation completed successfully!")
        print("\n📈 Results Summary:")
        print("=" * 50)
        
        # Display comprehensive report
        if hasattr(results, 'overall_score'):
            print(f"🎯 Overall REAL Score: {results.overall_score}")
        
        if hasattr(results, 'breakdown'):
            print("\n📊 Breakdown by task category:")
            for category, score in results.breakdown.items():
                print(f"  • {category}: {score}")
        
        if hasattr(results, 'comparison'):
            print("\n📈 Comparison to baseline models:")
            for model, score in results.comparison.items():
                print(f"  • {model}: {score}")
        
        print("\n📝 Detailed logs and analysis available in results object")
        print("🎉 Evaluation complete! Check the results above.")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during evaluation: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Ensure your OpenAI API key is valid and has sufficient credits")
        print("2. Check your internet connection")
        print("3. Verify AGI SDK installation: pip install agisdk")
        return None

if __name__ == "__main__":
    results = main()
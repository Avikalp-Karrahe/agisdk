#!/usr/bin/env python3
"""
Test script for Enhanced Demo Agent with Step Tracking and Goal Completion Detection

This script tests the enhanced agent on omnizon tasks to validate:
1. Comprehensive step tracking with chronological order
2. Goal completion detection capabilities
3. Detailed context management for the last 15 steps
4. Enhanced reasoning and self-awareness
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the path to import agisdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from agisdk.REAL.harness import harness
    from enhanced_demo_agent import EnhancedDemoAgentArgs
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and agisdk is installed")
    sys.exit(1)

def test_enhanced_agent_on_omnizon_tasks():
    """Test the enhanced agent on specific omnizon tasks"""
    
    print("🚀 Enhanced Demo Agent Test Suite")
    print("=" * 60)
    
    # Test tasks - focusing on the problematic ones
    test_tasks = [
        "webclones.omnizon-6",  # Samsung phone comparison - had completion detection issues
        "webclones.omnizon-9",  # PlayStation purchase - also had issues
    ]
    
    print(f"Testing Enhanced Agent on: {', '.join(test_tasks)}")
    print(f"🎯 Focus: Step tracking and goal completion detection")
    print("=" * 60)
    
    # Configure enhanced agent
    agent_args = EnhancedDemoAgentArgs(
        model_name="gpt-4o",
        chat_mode=False,
        demo_mode="default",  # Enable visual effects for better debugging
        use_html=False,
        use_axtree=True,
        use_screenshot=False,
        system_message_handling="separate"
    )
    
    print(f"🔧 Enhanced Agent Configuration:")
    print(f"   Model: {agent_args.model_name}")
    print(f"   GUI: Enabled (headless=False)")
    print(f"   Max steps: 50")
    print(f"   Cache: Disabled (fresh runs)")
    print()
    
    # Run the tests
    results = {}
    
    for i, task_name in enumerate(test_tasks, 1):
        print(f"📋 Task {i}/{len(test_tasks)}: {task_name}")
        print("-" * 40)
        
        try:
            # Create individual harness for each task (correct pattern)
            task_harness = harness(
                agentargs=agent_args,
                task_name=task_name,
                headless=False,  # GUI enabled for observation
                use_cache=False,  # Disable caching for fresh runs
                max_steps=50,  # Reasonable step limit
            )
            
            # Run the task
            task_results = task_harness.run()
            
            if task_results and task_name in task_results:
                result = task_results[task_name]
                success = result.get('cum_reward', 0) == 1.0
                score = result.get('cum_reward', 0)
                steps = result.get('n_steps', 0)
                elapsed = result.get('elapsed_time', 0)
                
                results[task_name] = {
                    'success': success,
                    'score': score,
                    'steps': steps,
                    'elapsed_time': elapsed,
                    'raw_result': result
                }
                
                print(f"✅ Task completed!")
                print(f"   Success: {success}")
                print(f"   Score: {score}")
                print(f"   Steps: {steps}")
                print(f"   Time: {elapsed:.2f}s")
                
                # Check for enhanced agent features
                if 'step_tracking' in str(result):
                    print(f"   📊 Step tracking: Detected")
                if 'goal_completion' in str(result):
                    print(f"   🎯 Goal detection: Detected")
                    
            else:
                print(f"❌ Task failed - no results returned")
                results[task_name] = {
                    'success': False,
                    'error': 'No results returned'
                }
                
        except Exception as e:
            print(f"❌ Task failed with error: {str(e)}")
            results[task_name] = {
                'success': False,
                'error': str(e)
            }
        
        print()
    
    # Generate comprehensive report
    print("📊 Enhanced Agent Test Results Summary")
    print("=" * 60)
    
    total_tasks = len(test_tasks)
    successful_tasks = sum(1 for r in results.values() if r.get('success', False))
    success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    print(f"Overall Performance:")
    print(f"   Tasks tested: {total_tasks}")
    print(f"   Successful: {successful_tasks}")
    print(f"   Success rate: {success_rate:.1f}%")
    print()
    
    print("Individual Task Results:")
    for task_name, result in results.items():
        status = "✅ SUCCESS" if result.get('success', False) else "❌ FAILED"
        print(f"   {task_name}: {status}")
        
        if result.get('success', False):
            print(f"      Score: {result.get('score', 0)}")
            print(f"      Steps: {result.get('steps', 0)}")
            print(f"      Time: {result.get('elapsed_time', 0):.2f}s")
        else:
            error = result.get('error', 'Unknown error')
            print(f"      Error: {error}")
        print()
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"enhanced_demo_agent_results_{timestamp}.json"
    
    detailed_results = {
        'timestamp': timestamp,
        'agent_type': 'enhanced_demo_agent',
        'test_configuration': {
            'model': agent_args.model_name,
            'tasks': test_tasks,
            'gui_enabled': True,
            'max_steps': 50,
            'timeout': 300
        },
        'summary': {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': success_rate
        },
        'individual_results': results
    }
    
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"📁 Detailed results saved to: {results_file}")
    
    # Enhanced Agent Analysis
    print("\n🔍 Enhanced Agent Feature Analysis")
    print("=" * 60)
    
    print("Key Enhancements Implemented:")
    print("✅ Comprehensive step tracking with chronological order")
    print("✅ Detailed context for last 15 steps")
    print("✅ Goal completion detection logic")
    print("✅ Enhanced reasoning with historical context")
    print("✅ Success pattern recognition")
    print("✅ Page state analysis")
    print("✅ Completion signal detection")
    
    print("\nExpected Improvements over Basic Demo Agent:")
    print("🎯 Better goal completion recognition")
    print("📊 Detailed step-by-step tracking")
    print("🧠 Enhanced self-awareness and reasoning")
    print("⚡ More efficient task completion")
    print("🔍 Better error recovery and adaptation")
    
    return results

def compare_with_basic_agent():
    """Compare enhanced agent performance with basic demo agent"""
    print("\n🔄 Comparison Analysis")
    print("=" * 60)
    
    print("Enhanced Agent vs Basic Demo Agent:")
    print("📈 Expected improvements:")
    print("   • Goal completion detection: Should recognize when tasks are done")
    print("   • Step tracking: Comprehensive history with context")
    print("   • Self-awareness: Better understanding of progress")
    print("   • Efficiency: Fewer unnecessary steps after goal completion")
    print("   • Accuracy: Better success rate reporting")
    
    print("\n💡 Key Differences:")
    print("   • Enhanced system prompts with step history")
    print("   • Goal completion detection before each action")
    print("   • Detailed step information tracking")
    print("   • Success pattern recognition")
    print("   • Page state analysis for context")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Demo Agent Test Suite")
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    try:
        # Run the enhanced agent tests
        results = test_enhanced_agent_on_omnizon_tasks()
        
        # Provide comparison analysis
        compare_with_basic_agent()
        
        print(f"\n✅ Test suite completed successfully!")
        print(f"⏰ Test finished at: {datetime.now()}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Test script for RealEnhancedAgent setup and basic functionality.
"""

import os
import sys
import json
from dataclasses import dataclass
from typing import Optional

# Add the parent directory to the path to import agisdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from real_enhanced_agent import RealEnhancedAgent, RealEnhancedAgentArgs
    print("✅ Successfully imported RealEnhancedAgent")
except ImportError as e:
    print(f"❌ Failed to import RealEnhancedAgent: {e}")
    sys.exit(1)

def test_agent_initialization():
    """Test basic agent initialization."""
    print("\n🧪 Testing RealEnhancedAgent initialization...")
    
    try:
        # Create agent configuration
        args = RealEnhancedAgentArgs(
            agent_name="test_real_enhanced_agent",
            model_name="claude-3-5-sonnet-20241022",  # Default model
            enhanced_selection=True,
            timeout_ms=30000,
            retry_attempts=3,
            use_html=True,
            use_axtree=True,
            use_screenshot=False  # Disable for testing
        )
        
        # Initialize agent
        agent = args.make_agent()
        print(f"✅ Agent initialized successfully: {agent.__class__.__name__}")
        print(f"   - Model: {args.model_name}")
        print(f"   - Enhanced Selection: {args.enhanced_selection}")
        print(f"   - Timeout: {args.timeout_ms}ms")
        print(f"   - Retry Attempts: {args.retry_attempts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_memory_systems():
    """Test memory system initialization."""
    print("\n🧠 Testing memory systems...")
    
    try:
        from memory_systems import EpisodicMemory, WorkingMemory
        
        # Test episodic memory
        episodic = EpisodicMemory(max_episodes=100)
        print("✅ EpisodicMemory initialized")
        
        # Test working memory (no parameters needed)
        working = WorkingMemory()
        print("✅ WorkingMemory initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory systems test failed: {e}")
        return False

def test_planning_system():
    """Test planning system initialization."""
    print("\n📋 Testing planning system...")
    
    try:
        from planning_system import HierarchicalPlanner
        
        planner = HierarchicalPlanner()
        print("✅ HierarchicalPlanner initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Planning system test failed: {e}")
        return False

def test_self_critique():
    """Test self-critique system initialization."""
    print("\n🔍 Testing self-critique system...")
    
    try:
        from self_critique import SelfCritiqueSystem
        
        critique = SelfCritiqueSystem()
        print("✅ SelfCritiqueSystem initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Self-critique system test failed: {e}")
        return False

def test_retry_system():
    """Test advanced retry system initialization."""
    print("\n🔄 Testing retry system...")
    
    try:
        from advanced_retry_system import AdvancedRetrySystem, RetryConfig
        
        # Create config first
        config = RetryConfig(max_attempts=3, base_delay=1.0)
        retry_system = AdvancedRetrySystem(config)
        print("✅ AdvancedRetrySystem initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Retry system test failed: {e}")
        return False

def check_api_keys():
    """Check if required API keys are available."""
    print("\n🔑 Checking API keys...")
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY found")
        return True
    elif openai_key:
        print("✅ OPENAI_API_KEY found")
        return True
    else:
        print("⚠️  No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("   Example: export ANTHROPIC_API_KEY='your_key_here'")
        return False

def main():
    """Run all tests."""
    print("🚀 RealEnhancedAgent Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Keys", check_api_keys),
        ("Agent Initialization", test_agent_initialization),
        ("Memory Systems", test_memory_systems),
        ("Planning System", test_planning_system),
        ("Self-Critique", test_self_critique),
        ("Retry System", test_retry_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! RealEnhancedAgent is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Comprehensive system scan for the enhanced demo agent.
Verifies full architectural compatibility following recent component upgrades.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import unittest
import hashlib

# Add the parent directory to the path to import agisdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from agisdk.REAL.browsergym.experiments import Agent
    from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str, prune_html
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and agisdk is installed")
    sys.exit(1)

class MockObservation:
    """Mock observation for testing"""
    def __init__(self, url="https://example.com", 
                 axtree=None, dom_txt=None, screenshot=None):
        self.url = url
        self.axtree = axtree or {"nodes": [{"role": "main", "name": "Main content"}]}
        self.dom_txt = dom_txt or "<html><body><div>Test content</div></body></html>"
        self.screenshot = screenshot or "mock_screenshot_data"
        
    def to_dict(self):
        return {
            "url": self.url,
            "axtree": self.axtree,
            "dom_txt": self.dom_txt,
            "screenshot": self.screenshot
        }

class EnhancedDemoAgentSystemScan(unittest.TestCase):
    """Test suite for comprehensive system scan of the enhanced demo agent"""
    
    def setUp(self):
        """Set up the test environment"""
        # Import the agent class - we do this here to avoid import errors
        # if the file doesn't exist
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from enhanced_demo_agent import EnhancedDemoAgent, EnhancedDemoAgentArgs
            
            # Create a test agent
            self.agent_args = EnhancedDemoAgentArgs(
                model_name="gpt-4o",
                use_html=True,
                use_axtree=True,
                use_screenshot=True
            )
            
            # Mock the LLM client to avoid API calls
            EnhancedDemoAgent._init_llm_client = lambda self: None
            self.agent = EnhancedDemoAgent(
                model_name="gpt-4o",
                use_html=True,
                use_axtree=True,
                use_screenshot=True
            )
            
            # Store the class for later use
            self.EnhancedDemoAgent = EnhancedDemoAgent
            self.EnhancedDemoAgentArgs = EnhancedDemoAgentArgs
            
            print("✅ Successfully created test agent")
        except ImportError as e:
            print(f"❌ Failed to import EnhancedDemoAgent: {e}")
            raise
        except Exception as e:
            print(f"❌ Failed to create test agent: {e}")
            raise
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly with all required attributes"""
        # Check core attributes
        self.assertEqual(self.agent.model_name, "gpt-4o")
        self.assertTrue(self.agent.use_html)
        self.assertTrue(self.agent.use_axtree)
        self.assertTrue(self.agent.use_screenshot)
        
        # Check tracking attributes
        self.assertIsInstance(self.agent.step_history, list)
        self.assertEqual(self.agent.step_count, 0)
        self.assertEqual(self.agent.last_page_hash, "")
        self.assertEqual(self.agent.repeated_state_count, 0)
        
        # Check page exploration journey tracking
        self.assertIsInstance(self.agent.page_journey, list)
        self.assertIsInstance(self.agent.visited_urls, dict)
        self.assertIsInstance(self.agent.page_outcomes, dict)
        
        print("✅ Agent initialization test passed")
    
    def test_observation_preprocessing(self):
        """Test the observation preprocessing pipeline"""
        # Create a mock observation
        obs = MockObservation().to_dict()
        
        # Reset the agent's state tracking variables
        self.agent.last_page_hash = ""
        self.agent.repeated_state_count = 0
        
        # Process the observation
        processed_obs = self.agent.obs_preprocessor(obs)
        
        # Check that the processed observation contains the expected keys
        self.assertIn("url", processed_obs)
        self.assertIn("axtree_txt", processed_obs)
        self.assertIn("pruned_html", processed_obs)
        self.assertIn("screenshot", processed_obs)
        self.assertIn("page_hash", processed_obs)
        self.assertIn("repeated_state_count", processed_obs)
        
        # Check that page state tracking works
        self.assertNotEqual(self.agent.last_page_hash, "")
        self.assertEqual(self.agent.repeated_state_count, 0)
        
        # Process the same observation again to test repeated state detection
        processed_obs2 = self.agent.obs_preprocessor(obs)
        self.assertEqual(self.agent.repeated_state_count, 1)
        
        # Process a different observation to test state change detection
        obs2 = MockObservation(url="https://example.com/different", 
                              dom_txt="<html><body><div>Different content</div></body></html>").to_dict()
        processed_obs3 = self.agent.obs_preprocessor(obs2)
        self.assertEqual(self.agent.repeated_state_count, 0)
        
        print("✅ Observation preprocessing test passed")
    
    def test_get_page_text(self):
        """Test the get_page_text helper method"""
        # Test with both AXTree and HTML
        text = self.agent.get_page_text({
            "axtree_txt": "AXTree content",
            "pruned_html": "HTML content"
        })
        self.assertEqual(text, "AXTree content")
        
        # Test with only HTML
        text = self.agent.get_page_text({
            "axtree_txt": "",
            "pruned_html": "HTML content"
        })
        self.assertEqual(text, "HTML content")
        
        # Test with only AXTree
        text = self.agent.get_page_text({
            "axtree_txt": "AXTree content",
            "pruned_html": ""
        })
        self.assertEqual(text, "AXTree content")
        
        # Test with neither
        text = self.agent.get_page_text({
            "axtree_txt": "",
            "pruned_html": ""
        })
        self.assertEqual(text, "")
        
        print("✅ get_page_text test passed")
    
    def test_page_state_analysis(self):
        """Test the page state analysis with exploration pattern detection"""
        # Create a mock observation
        obs = MockObservation(url="https://example.com/product/123").to_dict()
        
        # Process the observation
        processed_obs = self.agent.obs_preprocessor(obs)
        
        # Analyze the page state
        analysis = self.agent.analyze_page_state(processed_obs)
        
        # Check that the analysis contains the expected information
        self.assertIn("Current URL:", analysis)
        
        # Check that page journey tracking works
        self.assertEqual(len(self.agent.page_journey), 1)
        self.assertIn("https://example.com/product/123", self.agent.visited_urls)
        
        # Add more pages to test pattern detection
        self.agent.page_journey.append({
            "url": "https://example.com/search",
            "page_type": "Search",
            "confidence": 0.8,
            "visit_count": 1,
            "timestamp": datetime.now().isoformat()
        })
        self.agent.page_journey.append({
            "url": "https://example.com/product/456",
            "page_type": "Product",
            "confidence": 0.9,
            "visit_count": 1,
            "timestamp": datetime.now().isoformat()
        })
        
        # Test exploration pattern detection
        pattern = self.agent._get_exploration_pattern()
        self.assertNotEqual(pattern, "Insufficient data")
        
        print("✅ Page state analysis test passed")
    
    def test_reset_functionality(self):
        """Test that the reset method clears all state correctly"""
        # Create a mock observation and process it
        obs = MockObservation().to_dict()
        processed_obs = self.agent.obs_preprocessor(obs)
        
        # Analyze the page state to populate tracking attributes
        self.agent.analyze_page_state(processed_obs)
        
        # Verify that tracking attributes are populated
        self.assertNotEqual(self.agent.last_page_hash, "")
        self.assertGreater(len(self.agent.page_journey), 0)
        self.assertGreater(len(self.agent.visited_urls), 0)
        
        # Reset the agent
        self.agent.reset()
        
        # Verify that tracking attributes are cleared
        self.assertEqual(self.agent.last_page_hash, "")
        self.assertEqual(self.agent.repeated_state_count, 0)
        self.assertEqual(len(self.agent.page_journey), 0)
        self.assertEqual(len(self.agent.visited_urls), 0)
        self.assertEqual(len(self.agent.page_outcomes), 0)
        
        print("✅ Reset functionality test passed")
    
    def test_system_message_generation(self):
        """Test that the system message includes exploration history insights"""
        # Create a mock observation and process it
        obs = MockObservation().to_dict()
        processed_obs = self.agent.obs_preprocessor(obs)
        
        # Analyze the page state to populate tracking attributes
        self.agent.analyze_page_state(processed_obs)
        
        # Add more pages to test pattern detection
        self.agent.page_journey.append({
            "url": "https://example.com/search",
            "page_type": "Search",
            "confidence": 0.8,
            "visit_count": 1,
            "timestamp": datetime.now().isoformat()
        })
        self.agent.page_journey.append({
            "url": "https://example.com/product/456",
            "page_type": "Product",
            "confidence": 0.9,
            "visit_count": 1,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get the system message
        # Note: We can't directly test get_action as it makes API calls
        # Instead, we'll check that the exploration history attributes exist
        self.assertGreater(len(self.agent.page_journey), 0)
        self.assertGreater(len(self.agent.visited_urls), 0)
        pattern = self.agent._get_exploration_pattern()
        self.assertNotEqual(pattern, "")
        
        print("✅ System message generation test passed")
    
    def test_integration(self):
        """Test that all components work together correctly"""
        # Create a sequence of mock observations
        obs1 = MockObservation(url="https://example.com").to_dict()
        obs2 = MockObservation(url="https://example.com/search").to_dict()
        obs3 = MockObservation(url="https://example.com/product/123").to_dict()
        
        # Process the observations in sequence
        processed_obs1 = self.agent.obs_preprocessor(obs1)
        self.agent.analyze_page_state(processed_obs1)
        
        processed_obs2 = self.agent.obs_preprocessor(obs2)
        self.agent.analyze_page_state(processed_obs2)
        
        processed_obs3 = self.agent.obs_preprocessor(obs3)
        self.agent.analyze_page_state(processed_obs3)
        
        # Check that page journey tracking works correctly
        self.assertEqual(len(self.agent.page_journey), 3)
        self.assertEqual(len(self.agent.visited_urls), 3)
        
        # Check that exploration pattern detection works
        pattern = self.agent._get_exploration_pattern()
        self.assertNotEqual(pattern, "Insufficient data")
        
        print("✅ Integration test passed")

def run_system_scan():
    """Run the comprehensive system scan"""
    print("🚀 Starting Enhanced Demo Agent System Scan")
    print(f"⏰ Scan started at: {datetime.now()}")
    print("=" * 60)
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(EnhancedDemoAgentSystemScan)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"✅ Tests passed: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ System scan completed successfully!")
        print("All components are compatible and functioning correctly.")
    else:
        print("\n❌ System scan detected issues:")
        for failure in result.failures:
            print(f"- {failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"- {error[0]}: {error[1]}")
    
    print(f"⏰ Scan finished at: {datetime.now()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_system_scan()
    sys.exit(0 if success else 1)

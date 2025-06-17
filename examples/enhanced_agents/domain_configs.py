#!/usr/bin/env python3
"""
Domain-Specific Configurations for AGI SDK Agent

This module provides optimized configurations for different task domains
based on benchmark analysis and performance patterns.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Domain-specific configurations based on benchmark analysis
DOMAIN_CONFIGURATIONS = {
    'webclones.omnizon': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 25,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 180,
        'wait_times': {'page_load': 2, 'element_load': 1},
        'retry_attempts': 2,
        'browser_timeouts': {
            'page_load': 35000,  # 35 seconds for Omnizon page loads
            'element_wait': 20000,  # 20 seconds for element visibility
            'click_timeout': 15000,  # 15 seconds for click operations
            'navigation_timeout': 30000  # 30 seconds for navigation
        },
        'retry_config': {
            'max_retries': 4,  # More retries for e-commerce
            'retry_delay': 2.5,
            'backoff_multiplier': 1.6
        },
        'description': 'E-commerce platform - product browsing and cart operations'
    },
    'webclones.dashdish': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 25,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 200,
        'wait_times': {'page_load': 2, 'element_load': 1},
        'retry_attempts': 2,
        'description': 'Food delivery platform - restaurant browsing and ordering'
    },
    'webclones.gocalendar': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 35,  # More steps for complex calendar operations
        'model_preference': 'gpt-4-turbo',
        'timeout': 300,
        'wait_times': {'calendar_load': 5, 'date_picker': 3, 'page_load': 3},
        'retry_attempts': 3,
        'description': 'Calendar application - scheduling and event management'
    },
    'webclones.gomail': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 30,
        'model_preference': 'gpt-4-turbo',
        'timeout': 250,
        'wait_times': {'page_load': 3, 'email_load': 2},
        'retry_attempts': 3,
        'description': 'Email platform - message composition and management'
    },
    'webclones.networkin': {
        'chat_mode': True,  # Enable for social interactions
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 30,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 280,
        'wait_times': {'page_load': 3, 'social_load': 2},
        'retry_attempts': 3,
        'description': 'Social networking platform - connections and interactions'
    },
    'webclones.opendining': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 30,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 250,
        'wait_times': {'page_load': 2, 'reservation_load': 3},
        'retry_attempts': 3,
        'description': 'Restaurant reservation platform - booking and management'
    },
    'webclones.fly-unified': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 40,  # Complex flight booking requires more steps
        'model_preference': 'gpt-4-turbo',
        'timeout': 400,
        'wait_times': {'search_load': 5, 'results_load': 4, 'booking_load': 3},
        'retry_attempts': 4,
        'description': 'Flight booking platform - search and reservation'
    },
    'webclones.topwork': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 35,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 300,
        'wait_times': {'page_load': 3, 'job_load': 2},
        'retry_attempts': 3,
        'description': 'Job platform - search and application management'
    },
    'webclones.staynb': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 35,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 300,
        'wait_times': {'page_load': 3, 'booking_load': 4},
        'retry_attempts': 3,
        'description': 'Accommodation booking platform - search and reservation'
    },
    'webclones.udriver': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 25,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 200,
        'wait_times': {'page_load': 2, 'ride_load': 3},
        'retry_attempts': 2,
        'description': 'Ride-sharing platform - booking and management'
    },
    'webclones.zilloft': {
        'chat_mode': False,
        'use_html': True,
        'use_screenshot': True,
        'max_steps': 35,
        'model_preference': 'claude-3-5-sonnet-20241022',
        'timeout': 300,
        'wait_times': {'page_load': 3, 'property_load': 4},
        'retry_attempts': 3,
        'description': 'Real estate platform - property search and management'
    }
}

# Default configuration for unknown domains
DEFAULT_CONFIG = {
    'chat_mode': False,
    'use_html': True,
    'use_screenshot': True,
    'max_steps': 25,
    'model_preference': 'claude-3-5-sonnet-20241022',
    'timeout': 200,
    'wait_times': {'page_load': 2},
    'retry_attempts': 2,
    'browser_timeouts': {
        'page_load': 30000,  # 30 seconds for page loads
        'element_wait': 15000,  # 15 seconds for element visibility
        'click_timeout': 10000,  # 10 seconds for click operations
        'navigation_timeout': 25000  # 25 seconds for navigation
    },
    'retry_config': {
        'max_retries': 3,
        'retry_delay': 2.0,
        'backoff_multiplier': 1.5
    },
    'description': 'Default configuration for unknown domains'
}

def get_domain_config(task_name: str) -> Dict[str, Any]:
    """Get optimal configuration for a specific domain.
    
    Args:
        task_name: The task name (e.g., 'webclones.omnizon-1')
        
    Returns:
        Dictionary containing domain-specific configuration
    """
    # Extract domain from task name
    for domain in DOMAIN_CONFIGURATIONS.keys():
        if domain in task_name:
            config = DOMAIN_CONFIGURATIONS[domain].copy()
            logger.info(f"Using {domain} configuration for task {task_name}")
            return config
    
    # Return default configuration if no match found
    logger.warning(f"No specific configuration found for {task_name}, using default")
    return DEFAULT_CONFIG.copy()

def get_all_domains() -> list:
    """Get list of all configured domains."""
    return list(DOMAIN_CONFIGURATIONS.keys())

def get_domain_description(domain: str) -> str:
    """Get description for a specific domain."""
    config = DOMAIN_CONFIGURATIONS.get(domain, DEFAULT_CONFIG)
    return config.get('description', 'No description available')

def update_domain_config(domain: str, updates: Dict[str, Any]) -> None:
    """Update configuration for a specific domain.
    
    Args:
        domain: Domain name to update
        updates: Dictionary of configuration updates
    """
    if domain in DOMAIN_CONFIGURATIONS:
        DOMAIN_CONFIGURATIONS[domain].update(updates)
        logger.info(f"Updated configuration for {domain}: {updates}")
    else:
        logger.warning(f"Domain {domain} not found in configurations")

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    required_keys = ['chat_mode', 'use_html', 'use_screenshot', 'max_steps', 'model_preference']
    
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            return False
    
    # Validate data types
    if not isinstance(config['chat_mode'], bool):
        logger.error("chat_mode must be boolean")
        return False
    
    if not isinstance(config['max_steps'], int) or config['max_steps'] <= 0:
        logger.error("max_steps must be positive integer")
        return False
    
    return True

if __name__ == "__main__":
    # Test the configuration system
    print("Domain Configurations Test:")
    print("=" * 50)
    
    test_tasks = [
        "webclones.omnizon-1",
        "webclones.gocalendar-2",
        "webclones.networkin-3",
        "unknown.domain-1"
    ]
    
    for task in test_tasks:
        config = get_domain_config(task)
        print(f"\nTask: {task}")
        print(f"Config: {config}")
        print(f"Valid: {validate_config(config)}")
    
    print(f"\nTotal configured domains: {len(get_all_domains())}")
    print(f"Domains: {', '.join(get_all_domains())}")
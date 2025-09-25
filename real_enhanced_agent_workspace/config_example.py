#!/usr/bin/env python3
"""
Example configurations for RealEnhancedAgent.

This file demonstrates different ways to configure the RealEnhancedAgent
for various use cases and performance requirements.
"""

from real_enhanced_agent import RealEnhancedAgentArgs

# Configuration 1: High Performance with Claude
def get_high_performance_config():
    """
    High-performance configuration using Claude 3.5 Sonnet.
    Best for complex tasks requiring maximum reasoning capability.
    """
    return RealEnhancedAgentArgs(
        agent_name="high_performance_real_agent",
        model_name="claude-3-5-sonnet-20241022",
        enhanced_selection=True,
        timeout_ms=60000,  # 60 seconds
        retry_attempts=5,
        use_html=True,
        use_axtree=True,
        use_screenshot=True,  # Full multi-modal
        enable_memory=True,
        enable_planning=True,
        enable_critique=True,
        max_episodes=1000,
        persistence_dir="./agent_data/high_performance"
    )

# Configuration 2: Fast and Efficient with GPT-4o-mini
def get_efficient_config():
    """
    Efficient configuration using GPT-4o-mini.
    Optimized for speed and cost-effectiveness.
    """
    return RealEnhancedAgentArgs(
        agent_name="efficient_real_agent",
        model_name="gpt-4o-mini",
        enhanced_selection=True,
        timeout_ms=30000,  # 30 seconds
        retry_attempts=3,
        use_html=True,
        use_axtree=True,
        use_screenshot=False,  # Reduce API costs
        enable_memory=True,
        enable_planning=False,  # Disable for speed
        enable_critique=False,  # Disable for speed
        max_episodes=500,
        persistence_dir="./agent_data/efficient"
    )

# Configuration 3: REAL Benchmark Optimized
def get_real_benchmark_config():
    """
    Configuration optimized specifically for REAL benchmark evaluation.
    Balanced performance and reliability.
    """
    return RealEnhancedAgentArgs(
        agent_name="real_benchmark_agent",
        model_name="claude-3-5-sonnet-20241022",
        enhanced_selection=True,
        timeout_ms=45000,  # 45 seconds
        retry_attempts=4,
        use_html=True,
        use_axtree=True,
        use_screenshot=True,
        enable_memory=True,
        enable_planning=True,
        enable_critique=True,
        max_episodes=200,  # Focused on current session
        persistence_dir="./agent_data/benchmark"
    )

# Configuration 4: Minimal Resource Usage
def get_minimal_config():
    """
    Minimal configuration for resource-constrained environments.
    Basic functionality with minimal overhead.
    """
    return RealEnhancedAgentArgs(
        agent_name="minimal_real_agent",
        model_name="gpt-4o-mini",
        enhanced_selection=False,  # Disable enhanced features
        timeout_ms=20000,  # 20 seconds
        retry_attempts=2,
        use_html=True,
        use_axtree=False,  # Reduce processing
        use_screenshot=False,  # Reduce processing
        enable_memory=False,  # Disable memory
        enable_planning=False,  # Disable planning
        enable_critique=False,  # Disable critique
        max_episodes=50,
        persistence_dir=None  # No persistence
    )

# Configuration 5: Research and Development
def get_research_config():
    """
    Configuration for research and development purposes.
    Maximum features enabled for experimentation.
    """
    return RealEnhancedAgentArgs(
        agent_name="research_real_agent",
        model_name="claude-3-5-sonnet-20241022",
        enhanced_selection=True,
        timeout_ms=90000,  # 90 seconds for complex tasks
        retry_attempts=6,
        use_html=True,
        use_axtree=True,
        use_screenshot=True,
        enable_memory=True,
        enable_planning=True,
        enable_critique=True,
        max_episodes=2000,  # Large memory for learning
        persistence_dir="./agent_data/research",
        # Additional research parameters
        learning_rate=0.1,
        exploration_factor=0.2
    )

def create_agent_from_config(config_name: str):
    """
    Create an agent instance from a named configuration.
    
    Args:
        config_name: One of 'high_performance', 'efficient', 'benchmark', 'minimal', 'research'
    
    Returns:
        RealEnhancedAgent instance
    """
    configs = {
        'high_performance': get_high_performance_config,
        'efficient': get_efficient_config,
        'benchmark': get_real_benchmark_config,
        'minimal': get_minimal_config,
        'research': get_research_config
    }
    
    if config_name not in configs:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(configs.keys())}")
    
    config = configs[config_name]()
    return config.make_agent()

# Example usage
if __name__ == "__main__":
    print("RealEnhancedAgent Configuration Examples")
    print("=" * 50)
    
    configs = [
        ("High Performance", get_high_performance_config),
        ("Efficient", get_efficient_config),
        ("REAL Benchmark", get_real_benchmark_config),
        ("Minimal", get_minimal_config),
        ("Research", get_research_config)
    ]
    
    for name, config_func in configs:
        config = config_func()
        print(f"\n{name} Configuration:")
        print(f"  Model: {config.model_name}")
        print(f"  Timeout: {config.timeout_ms}ms")
        print(f"  Retries: {config.retry_attempts}")
        print(f"  Enhanced: {config.enhanced_selection}")
        print(f"  Memory: {getattr(config, 'enable_memory', 'N/A')}")
        print(f"  Planning: {getattr(config, 'enable_planning', 'N/A')}")
        print(f"  Critique: {getattr(config, 'enable_critique', 'N/A')}")
    
    print("\nTo use a configuration:")
    print("  agent = create_agent_from_config('benchmark')")
    print("  # or")
    print("  config = get_real_benchmark_config()")
    print("  agent = config.make_agent()")
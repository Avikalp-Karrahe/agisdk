# RealEnhancedAgent Workspace

This workspace contains the **RealEnhancedAgent** - a REAL benchmark-optimized AI agent with enhanced cognitive capabilities.

## Overview

The RealEnhancedAgent is specifically designed for the REAL benchmark framework, featuring:

- **Native REAL Integration**: Optimized for REAL benchmark tasks
- **Enhanced Element Selection**: Advanced DOM and AXTree analysis
- **Memory Systems**: Episodic and working memory for learning
- **Self-Critique**: Continuous improvement through self-assessment
- **Advanced Retry Logic**: Intelligent error recovery mechanisms
- **Multi-Modal Support**: HTML, AXTree, and screenshot observations

## Files in this Workspace

- `real_enhanced_agent.py` - Main RealEnhancedAgent implementation
- `memory_systems.py` - Episodic and working memory components
- `planning_system.py` - Hierarchical planning system
- `self_critique.py` - Self-critique and improvement mechanisms
- `advanced_retry_system.py` - Robust retry and error recovery
- `run_real_benchmark.py` - REAL benchmark runner script
- `requirements.txt` - Python dependencies

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your API keys (Anthropic Claude or OpenAI):
   ```bash
   export ANTHROPIC_API_KEY="your_key_here"
   # or
   export OPENAI_API_KEY="your_key_here"
   ```

3. Run a test:
   ```bash
   python test_real_enhanced_agent.py
   ```

4. Run REAL benchmark:
   ```bash
   python run_real_benchmark.py
   ```

## Configuration

The RealEnhancedAgent can be configured with:

- **Model Selection**: `claude-3-5-sonnet-20241022`, `gpt-4o-mini`, etc.
- **Enhanced Features**: Enable/disable memory, planning, critique
- **Observation Modes**: HTML, AXTree, screenshot combinations
- **Timeout Settings**: Customizable timeout values
- **Retry Parameters**: Configurable retry attempts and delays

## Performance

This agent is optimized for REAL benchmark compatibility and has shown excellent performance in:
- Element detection and interaction
- Multi-step task execution
- Error recovery and adaptation
- Resource efficiency

## Next Steps

- Customize configuration for your specific use case
- Run benchmarks to evaluate performance
- Extend with domain-specific optimizations
- Integrate with your existing workflows
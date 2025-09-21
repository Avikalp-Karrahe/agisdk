# Enhanced AI Agent System v2.0

> **A comprehensive cognitive architecture for autonomous web agents with advanced learning, planning, and self-critique capabilities.**

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-orange.svg)]()

## 🚀 Overview

The Enhanced AI Agent System v2.0 represents a breakthrough in autonomous web agent technology, implementing a sophisticated cognitive architecture that enables agents to learn, plan, and adapt in complex web environments. Built on the foundation of our comprehensive Product Requirements Document (PRD) and Technical Architecture, this system delivers enterprise-grade performance with human-like reasoning capabilities.

### Key Features

🧠 **Multi-Layered Memory Systems**
- **Episodic Memory**: Stores and retrieves successful action patterns
- **Working Memory**: Maintains context during task execution
- **Semantic Memory**: Domain-specific knowledge and strategies

🔍 **Self-Critique & Learning**
- Real-time action evaluation and confidence scoring
- Alternative action suggestions for failed attempts
- Continuous learning from experience

📋 **Hierarchical Planning**
- Goal decomposition into manageable sub-tasks
- Adaptive replanning when strategies fail
- Context-aware strategy selection

🔄 **Advanced Retry Logic**
- Intelligent error classification and handling
- Exponential backoff with jitter
- Learning-based retry strategies

🎯 **Domain Optimization**
- Specialized strategies for e-commerce (Omnizon)
- Email and calendar task optimization
- Extensible domain-specific modules

📊 **Real-Time Monitoring**
- Comprehensive performance metrics
- Learning progress tracking
- Cognitive state visualization

## 📁 Project Structure

```
enhanced_agents/
├── docs/                           # Comprehensive documentation
│   ├── PRD_Enhanced_Agent_System.md      # Product Requirements Document
│   ├── Technical_Architecture.md         # System architecture design
│   ├── Implementation_Roadmap.md         # Development roadmap
│   ├── Testing_Strategy.md              # Quality assurance strategy
│   └── Project_Plan_Enhanced_Agent.md   # Project management plan
├── 
├── enhanced_agent_v2.py              # Main enhanced agent implementation
├── memory_systems.py                 # Memory subsystems (episodic, working)
├── self_critique.py                  # Self-evaluation and learning
├── planning_system.py                # Hierarchical task planning
├── advanced_retry_system.py          # Intelligent retry mechanisms
├── domain_configs.py                 # Domain-specific configurations
├── 
├── run_enhanced_benchmark.py         # Comprehensive benchmark runner
├── run_real_benchmark.py             # REAL benchmark integration
├── 
├── config_010_enhanced_agent.py      # Legacy configuration (v1.0)
├── real_enhanced_agent.py            # REAL-specific agent wrapper
├── 
├── requirements.txt                  # Python dependencies
└── README.md                        # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for GPT-4 integration)
- Sufficient disk space for memory persistence (recommended: 1GB+)

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd /path/to/agisdk/examples/enhanced_agents
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set API Key**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Install Playwright (for web automation)**
   ```bash
   playwright install
   ```

5. **Test Installation**
   ```bash
   python enhanced_agent_v2.py
   ```

### Advanced Setup

For production deployments or advanced development:

```bash
# Create virtual environment
python -m venv venv_enhanced
source venv_enhanced/bin/activate  # On Windows: venv_enhanced\Scripts\activate

# Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # Development tools

# Configure persistence directory
mkdir -p ./agent_data
mkdir -p ./benchmark_results
```

## 🎯 Usage Examples

### Basic Agent Usage

```python
from enhanced_agent_v2 import EnhancedAgentV2Args, EnhancedAgentV2

# Create agent with full cognitive architecture
config = {
    'max_steps': 50,
    'enable_learning': True,
    'enable_planning': True,
    'enable_critique': True,
    'persistence_dir': './agent_data'
}

agent_args = EnhancedAgentV2Args(config=config)
agent = agent_args.make_agent()

# The agent is now ready for task execution
print(f"Agent initialized: {agent.get_stats()}")
```

### REAL Benchmark Integration

```python
from run_enhanced_benchmark import EnhancedBenchmarkRunner

# Configure comprehensive benchmark
config = {
    'agent_config': {
        'enable_learning': True,
        'enable_planning': True,
        'enable_critique': True,
        'max_episodes': 10000
    },
    'monitoring': {
        'log_interval': 10,
        'save_interval': 50,
        'enable_real_time_metrics': True
    }
}

# Run benchmark with enhanced monitoring
runner = EnhancedBenchmarkRunner(config)
results = runner.run_benchmark(num_episodes=100)

print(f"Success Rate: {results['performance_metrics']['success_rate']:.1f}%")
```

### Memory System Usage

```python
from memory_systems import EpisodicMemory, WorkingMemory, StateHasher

# Initialize memory systems
episodic = EpisodicMemory(max_episodes=5000)
working = WorkingMemory()

# Store successful experience
state_hash = StateHasher.hash_state(observation)
episodic.store_episode(
    state_hash=state_hash,
    action="click(text='Submit')",
    outcome="success",
    success=True,
    domain="webclones.omnizon",
    execution_time=1.2,
    confidence=0.9
)

# Retrieve best action for similar state
best_action = episodic.get_best_action_for_state(state_hash, "webclones.omnizon")
print(f"Recommended action: {best_action}")
```

### Planning System Usage

```python
from planning_system import HierarchicalPlanner

# Initialize planner
planner = HierarchicalPlanner()

# Create plan for complex goal
goal = "Purchase a laptop on Omnizon with specific requirements"
domain = "webclones.omnizon"
current_state = {'url': 'https://omnizon.com', 'elements': ['search_box']}

plan = planner.create_plan(goal, domain, current_state)

for i, sub_goal in enumerate(plan):
    print(f"{i+1}. {sub_goal.description} (Priority: {sub_goal.priority})")
```

### Self-Critique System Usage

```python
from self_critique import SelfCritiqueSystem

# Initialize critique system
critic = SelfCritiqueSystem()

# Evaluate action outcome
before_state = {'url': 'page1.com', 'elements': ['button1']}
after_state = {'url': 'page2.com', 'elements': ['success_msg']}

critique = critic.evaluate_action_outcome(
    action="click(button[id='submit'])",
    before_state=before_state,
    after_state=after_state,
    execution_time=1.5
)

print(f"Effectiveness: {critique.effectiveness_score:.2f}")
print(f"Confidence: {critique.confidence_score:.2f}")
print(f"Recommendations: {critique.recommendations}")
```

## 🏃‍♂️ Running Benchmarks

### Quick Benchmark Run

```bash
# Run enhanced benchmark with default settings
python run_enhanced_benchmark.py
```

### Custom Benchmark Configuration

```bash
# Run with specific parameters
python run_enhanced_benchmark.py --episodes 200 --domain omnizon --learning-enabled
```

### Legacy REAL Integration

```bash
# Run original REAL benchmark integration
python run_real_benchmark.py
```

## 📊 Performance Metrics

The Enhanced Agent v2.0 provides comprehensive performance tracking:

### Core Metrics
- **Success Rate**: Percentage of successfully completed tasks
- **Average Steps**: Mean number of actions per task
- **Response Time**: Average time to select actions
- **Learning Rate**: Rate of performance improvement over time

### Cognitive Metrics
- **Memory Utilization**: Episodic memory usage and effectiveness
- **Planning Efficiency**: Success rate of planned vs. heuristic actions
- **Critique Accuracy**: Self-assessment accuracy compared to actual outcomes
- **Adaptation Speed**: Time to learn new patterns

### Domain-Specific Metrics
- **E-commerce Success**: Omnizon task completion rates
- **Email Efficiency**: Email composition and sending success
- **Calendar Management**: Meeting scheduling accuracy
- **Cross-Domain Transfer**: Knowledge transfer between domains

## 🔧 Configuration Options

### Agent Configuration

```python
config = {
    # Core settings
    'max_steps': 50,                    # Maximum steps per episode
    'timeout_ms': 3000,                 # Action timeout in milliseconds
    
    # Cognitive features
    'enable_learning': True,            # Enable episodic memory learning
    'enable_planning': True,            # Enable hierarchical planning
    'enable_critique': True,            # Enable self-critique system
    
    # Memory settings
    'max_episodes': 10000,              # Maximum episodic memory size
    'persistence_dir': './agent_data',  # Data persistence directory
    
    # Retry settings
    'max_retries': 5,                   # Maximum retry attempts
    'base_delay': 1.0,                  # Base retry delay in seconds
    
    # Performance settings
    'batch_size': 32,                   # Batch size for memory operations
    'memory_cleanup_interval': 1000,    # Memory cleanup frequency
}
```

### Benchmark Configuration

```python
benchmark_config = {
    # Execution settings
    'max_steps': 50,
    'headless': True,                   # Run browser in headless mode
    'record_video': False,              # Record execution videos
    'enable_screenshots': True,         # Capture screenshots
    
    # Monitoring settings
    'log_interval': 10,                 # Progress logging frequency
    'save_interval': 50,                # Results saving frequency
    'performance_window': 100,          # Performance trend window
    
    # Output settings
    'results_dir': './benchmark_results',
    'save_detailed_logs': True,
    'generate_reports': True,
}
```

## 🧪 Testing & Quality Assurance

### Running Tests

```bash
# Run unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test categories
python -m pytest tests/test_memory_systems.py -v
python -m pytest tests/test_planning_system.py -v
python -m pytest tests/test_self_critique.py -v
```

### Memory System Tests

```bash
# Test memory systems independently
python memory_systems.py
```

### Planning System Tests

```bash
# Test planning system
python planning_system.py
```

### Self-Critique Tests

```bash
# Test self-critique system
python self_critique.py
```

## 📈 Performance Optimization

### Memory Optimization

1. **Episodic Memory Tuning**
   ```python
   # Optimize memory size based on available resources
   config['max_episodes'] = 5000  # Reduce for limited memory
   config['memory_cleanup_interval'] = 500  # More frequent cleanup
   ```

2. **Working Memory Efficiency**
   ```python
   # Configure working memory limits
   working_memory.set_context_limit(100)  # Limit context size
   working_memory.enable_compression(True)  # Enable data compression
   ```

### Planning Optimization

1. **Plan Complexity Management**
   ```python
   # Limit planning depth for faster execution
   planner.set_max_depth(5)
   planner.enable_parallel_planning(True)
   ```

2. **Strategy Caching**
   ```python
   # Enable strategy caching for repeated patterns
   planner.enable_strategy_cache(True)
   planner.set_cache_size(1000)
   ```

### Critique System Optimization

1. **Evaluation Frequency**
   ```python
   # Adjust critique frequency based on performance needs
   critic.set_evaluation_frequency(0.5)  # Evaluate 50% of actions
   critic.enable_batch_evaluation(True)  # Batch evaluations
   ```

## 🔍 Troubleshooting

### Common Issues

#### Memory Issues

**Problem**: Agent runs out of memory during long sessions

**Solution**:
```python
# Reduce memory limits and enable cleanup
config['max_episodes'] = 2000
config['memory_cleanup_interval'] = 100

# Enable memory compression
episodic_memory.enable_compression(True)
```

#### Performance Issues

**Problem**: Slow action selection

**Solution**:
```python
# Disable expensive features for speed
config['enable_planning'] = False  # Temporarily disable planning
config['enable_critique'] = False  # Disable critique for speed

# Reduce memory lookup complexity
episodic_memory.set_similarity_threshold(0.8)  # Higher threshold
```

#### Planning Issues

**Problem**: Plans are too complex or fail frequently

**Solution**:
```python
# Simplify planning parameters
planner.set_max_sub_goals(5)  # Limit plan complexity
planner.set_confidence_threshold(0.7)  # Higher confidence requirement

# Enable fallback strategies
planner.enable_fallback_planning(True)
```

### Debug Mode

```python
# Enable comprehensive debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable agent debug mode
config['debug_mode'] = True
config['verbose_logging'] = True

# Save debug information
config['save_debug_info'] = True
config['debug_dir'] = './debug_logs'
```

### Performance Monitoring

```python
# Monitor real-time performance
from enhanced_agent_v2 import EnhancedAgentV2

agent = EnhancedAgentV2(config)

# Get real-time stats
stats = agent.get_stats()
print(f"Memory usage: {stats['performance_metrics']['memory_usage_mb']:.1f}MB")
print(f"Success rate: {stats['performance_metrics']['success_rate']:.1%}")
print(f"Response time: {stats['performance_metrics']['avg_response_time']:.3f}s")
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Product Requirements Document](docs/PRD_Enhanced_Agent_System.md)**: Complete feature specifications and requirements
- **[Technical Architecture](docs/Technical_Architecture.md)**: Detailed system design and component interactions
- **[Implementation Roadmap](docs/Implementation_Roadmap.md)**: Development timeline and milestones
- **[Testing Strategy](docs/Testing_Strategy.md)**: Quality assurance and testing approaches
- **[Project Plan](docs/Project_Plan_Enhanced_Agent.md)**: Project management and resource allocation

## 🤝 Contributing

We welcome contributions to the Enhanced Agent System! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/enhanced-agents.git
cd enhanced-agents

# Create development environment
python -m venv venv_dev
source venv_dev/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Standards

- Follow PEP 8 style guidelines
- Maintain 95%+ test coverage
- Add comprehensive docstrings
- Include type hints for all functions
- Write meaningful commit messages

### Testing Requirements

```bash
# Run full test suite
python -m pytest tests/ --cov=. --cov-report=html

# Ensure all tests pass
python -m pytest tests/ -x

# Check code quality
flake8 .
black --check .
mypy .
```

### Submitting Changes

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes and add tests
3. Ensure all tests pass and code quality checks succeed
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AGI SDK Team**: For providing the foundational framework
- **REAL Benchmark**: For comprehensive evaluation capabilities
- **OpenAI**: For GPT-4 integration and API support
- **BrowserGym**: For web automation infrastructure
- **Contributors**: All developers who have contributed to this project

## 📞 Support

For support, questions, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/your-repo/enhanced-agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/enhanced-agents/discussions)
- **Email**: enhanced-agents@yourorg.com
- **Documentation**: [Full Documentation](https://enhanced-agents.readthedocs.io)

## 🔮 Roadmap

See our [Implementation Roadmap](docs/Implementation_Roadmap.md) for detailed future plans:

### Q2 2025 - Enhancement Phase
- [ ] Advanced retry mechanisms with ML-based error prediction
- [ ] Multi-modal input processing (vision + text)
- [ ] Distributed memory systems for scalability
- [ ] Real-time collaboration between multiple agents

### Q3 2025 - Production Phase
- [ ] Enterprise security and compliance features
- [ ] Cloud deployment and auto-scaling
- [ ] Advanced analytics and business intelligence
- [ ] Integration with popular enterprise tools

### Q4 2025 - Ecosystem Phase
- [ ] Plugin marketplace and third-party integrations
- [ ] Advanced research tools and experiment tracking
- [ ] Community-driven domain extensions
- [ ] Academic research partnerships

---

**Enhanced AI Agent System v2.0** - *Redefining autonomous web agent capabilities*

*Built with ❤️ by the Enhanced Agent Development Team*
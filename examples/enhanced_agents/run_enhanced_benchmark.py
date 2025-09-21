#!/usr/bin/env python3
"""
Enhanced Agent REAL Benchmark Integration
Demonstrating the complete cognitive architecture in action

This script showcases:
- Enhanced Agent v2.0 with full cognitive architecture
- REAL benchmark integration with comprehensive metrics
- Real-time performance monitoring
- Learning and adaptation capabilities
- Advanced error handling and recovery

Author: Enhanced Agent Development Team
Version: 2.0
Date: January 2025
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_agent_v2 import EnhancedAgentV2Args, EnhancedAgentV2
    from agisdk import REAL
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed and the enhanced agent is available.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_benchmark.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBenchmarkRunner:
    """
    Comprehensive benchmark runner for the Enhanced Agent v2.0.
    
    Features:
    - Real-time performance monitoring
    - Detailed metrics collection
    - Learning progress tracking
    - Error analysis and reporting
    - Adaptive configuration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.results = []
        self.session_metrics = {
            'start_time': time.time(),
            'total_episodes': 0,
            'successful_episodes': 0,
            'failed_episodes': 0,
            'total_steps': 0,
            'total_execution_time': 0.0,
            'learning_improvements': [],
            'error_patterns': {},
            'performance_trends': []
        }
        
        # Create results directory
        self.results_dir = Path(self.config.get('results_dir', './benchmark_results'))
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info("Enhanced Benchmark Runner initialized")
        logger.info(f"Configuration: {json.dumps(self.config, indent=2)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the benchmark runner."""
        return {
            # Agent configuration
            'agent_config': {
                'max_steps': 50,
                'timeout_ms': 3000,
                'enable_learning': True,
                'enable_planning': True,
                'enable_critique': True,
                'max_episodes': 10000,
                'max_retries': 5,
                'base_delay': 1.0,
                'persistence_dir': './agent_data'
            },
            
            # Benchmark configuration
            'benchmark_config': {
                'max_steps': 50,
                'action_space': 'browsergym',
                'observation_space': 'browsergym',
                'headless': True,
                'record_video': False,
                'enable_screenshots': True
            },
            
            # Monitoring configuration
            'monitoring': {
                'log_interval': 10,  # Log progress every N episodes
                'save_interval': 50,  # Save results every N episodes
                'performance_window': 100,  # Window for performance trend analysis
                'enable_real_time_metrics': True
            },
            
            # Output configuration
            'results_dir': './benchmark_results',
            'save_detailed_logs': True,
            'generate_reports': True
        }
    
    def run_benchmark(self, num_episodes: int = None, task_filter: str = None) -> Dict[str, Any]:
        """
        Run the REAL benchmark with the enhanced agent.
        
        Args:
            num_episodes: Number of episodes to run (None for all available)
            task_filter: Filter tasks by domain (e.g., 'omnizon', 'email')
        
        Returns:
            Comprehensive results dictionary
        """
        logger.info("Starting Enhanced Agent REAL Benchmark")
        logger.info("=" * 60)
        
        try:
            # Initialize enhanced agent
            agent_args = EnhancedAgentV2Args(
                config=self.config['agent_config'],
                model_name="gpt-4"
            )
            agent = agent_args.make_agent()
            
            # Initialize REAL harness
            harness = REAL.harness(
                agent_args=agent_args,
                **self.config['benchmark_config']
            )
            
            logger.info(f"Agent initialized: {type(agent).__name__}")
            logger.info(f"Harness configured with {len(harness.tasks) if hasattr(harness, 'tasks') else 'unknown'} tasks")
            
            # Run benchmark episodes
            episode_count = 0
            start_time = time.time()
            
            for episode_result in harness.run_episodes(num_episodes=num_episodes):
                episode_count += 1
                
                # Process episode result
                self._process_episode_result(episode_result, agent, episode_count)
                
                # Log progress
                if episode_count % self.config['monitoring']['log_interval'] == 0:
                    self._log_progress(episode_count, time.time() - start_time)
                
                # Save intermediate results
                if episode_count % self.config['monitoring']['save_interval'] == 0:
                    self._save_intermediate_results(episode_count)
                
                # Update performance trends
                self._update_performance_trends(agent)
            
            # Generate final results
            final_results = self._generate_final_results(agent, time.time() - start_time)
            
            # Save comprehensive results
            self._save_final_results(final_results)
            
            # Generate reports if enabled
            if self.config.get('generate_reports', True):
                self._generate_reports(final_results)
            
            logger.info("Benchmark completed successfully!")
            return final_results
            
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _process_episode_result(self, episode_result: Dict[str, Any], agent: EnhancedAgentV2, episode_num: int):
        """
        Process individual episode results and update metrics.
        """
        try:
            # Extract episode information
            task_name = episode_result.get('task_name', 'unknown')
            success = episode_result.get('success', False)
            steps = episode_result.get('steps', 0)
            execution_time = episode_result.get('execution_time', 0.0)
            error_msg = episode_result.get('error_msg')
            
            # Update session metrics
            self.session_metrics['total_episodes'] += 1
            self.session_metrics['total_steps'] += steps
            self.session_metrics['total_execution_time'] += execution_time
            
            if success:
                self.session_metrics['successful_episodes'] += 1
            else:
                self.session_metrics['failed_episodes'] += 1
                
                # Track error patterns
                if error_msg:
                    error_key = self._categorize_error(error_msg)
                    self.session_metrics['error_patterns'][error_key] = \
                        self.session_metrics['error_patterns'].get(error_key, 0) + 1
            
            # Get agent statistics
            agent_stats = agent.get_stats()
            
            # Create detailed episode record
            episode_record = {
                'episode_number': episode_num,
                'task_name': task_name,
                'success': success,
                'steps': steps,
                'execution_time': execution_time,
                'error_msg': error_msg,
                'timestamp': datetime.now().isoformat(),
                'agent_stats': agent_stats,
                'cognitive_state': {
                    'goal': agent.cognitive_state.current_goal,
                    'domain': agent.cognitive_state.current_domain,
                    'confidence': agent.cognitive_state.confidence_level,
                    'memory_load': agent.cognitive_state.working_memory_load
                }
            }
            
            self.results.append(episode_record)
            
            # Log episode completion
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"Episode {episode_num} ({task_name}): {status} in {steps} steps ({execution_time:.2f}s)")
            
            if not success and error_msg:
                logger.warning(f"  Error: {error_msg}")
            
        except Exception as e:
            logger.error(f"Error processing episode result: {e}")
    
    def _categorize_error(self, error_msg: str) -> str:
        """
        Categorize error messages for pattern analysis.
        """
        error_lower = error_msg.lower()
        
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'element not found' in error_lower or 'no such element' in error_lower:
            return 'element_not_found'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network_error'
        elif 'javascript' in error_lower or 'js' in error_lower:
            return 'javascript_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        else:
            return 'other'
    
    def _log_progress(self, episode_count: int, elapsed_time: float):
        """
        Log current progress and performance metrics.
        """
        success_rate = (self.session_metrics['successful_episodes'] / 
                       self.session_metrics['total_episodes']) * 100
        
        avg_steps = (self.session_metrics['total_steps'] / 
                    self.session_metrics['total_episodes'])
        
        episodes_per_minute = (episode_count / elapsed_time) * 60
        
        logger.info(f"Progress Update - Episode {episode_count}:")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        logger.info(f"  Average Steps: {avg_steps:.1f}")
        logger.info(f"  Episodes/min: {episodes_per_minute:.1f}")
        logger.info(f"  Elapsed Time: {elapsed_time:.1f}s")
    
    def _update_performance_trends(self, agent: EnhancedAgentV2):
        """
        Update performance trend analysis.
        """
        try:
            window_size = self.config['monitoring']['performance_window']
            
            if len(self.results) >= window_size:
                # Calculate performance metrics for the last window
                recent_results = self.results[-window_size:]
                
                success_rate = sum(1 for r in recent_results if r['success']) / len(recent_results)
                avg_steps = sum(r['steps'] for r in recent_results) / len(recent_results)
                avg_time = sum(r['execution_time'] for r in recent_results) / len(recent_results)
                
                # Get agent learning metrics
                agent_stats = agent.get_stats()
                memory_size = agent_stats.get('system_status', {}).get('episodic_memory_size', 0)
                
                trend_point = {
                    'episode': len(self.results),
                    'success_rate': success_rate,
                    'avg_steps': avg_steps,
                    'avg_time': avg_time,
                    'memory_size': memory_size,
                    'timestamp': time.time()
                }
                
                self.session_metrics['performance_trends'].append(trend_point)
                
                # Detect learning improvements
                if len(self.session_metrics['performance_trends']) >= 2:
                    prev_trend = self.session_metrics['performance_trends'][-2]
                    
                    if (trend_point['success_rate'] > prev_trend['success_rate'] + 0.05 or
                        trend_point['avg_steps'] < prev_trend['avg_steps'] - 1.0):
                        
                        improvement = {
                            'episode': len(self.results),
                            'type': 'performance_improvement',
                            'details': {
                                'success_rate_change': trend_point['success_rate'] - prev_trend['success_rate'],
                                'steps_change': trend_point['avg_steps'] - prev_trend['avg_steps']
                            },
                            'timestamp': time.time()
                        }
                        
                        self.session_metrics['learning_improvements'].append(improvement)
                        logger.info(f"Learning improvement detected at episode {len(self.results)}!")
        
        except Exception as e:
            logger.error(f"Error updating performance trends: {e}")
    
    def _save_intermediate_results(self, episode_count: int):
        """
        Save intermediate results for recovery and analysis.
        """
        try:
            intermediate_file = self.results_dir / f"intermediate_results_{episode_count}.json"
            
            intermediate_data = {
                'episode_count': episode_count,
                'session_metrics': self.session_metrics,
                'recent_results': self.results[-50:],  # Last 50 episodes
                'timestamp': datetime.now().isoformat()
            }
            
            with open(intermediate_file, 'w') as f:
                json.dump(intermediate_data, f, indent=2, default=str)
            
            logger.debug(f"Intermediate results saved to {intermediate_file}")
            
        except Exception as e:
            logger.error(f"Error saving intermediate results: {e}")
    
    def _generate_final_results(self, agent: EnhancedAgentV2, total_time: float) -> Dict[str, Any]:
        """
        Generate comprehensive final results.
        """
        try:
            # Calculate overall metrics
            total_episodes = len(self.results)
            successful_episodes = sum(1 for r in self.results if r['success'])
            success_rate = (successful_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            
            avg_steps = sum(r['steps'] for r in self.results) / total_episodes if total_episodes > 0 else 0
            avg_time = sum(r['execution_time'] for r in self.results) / total_episodes if total_episodes > 0 else 0
            
            # Get final agent statistics
            final_agent_stats = agent.get_stats()
            
            # Analyze task performance by domain
            domain_performance = self._analyze_domain_performance()
            
            # Analyze learning progression
            learning_analysis = self._analyze_learning_progression()
            
            # Generate error analysis
            error_analysis = self._analyze_errors()
            
            final_results = {
                'benchmark_info': {
                    'agent_type': 'EnhancedAgentV2',
                    'total_episodes': total_episodes,
                    'total_time': total_time,
                    'timestamp': datetime.now().isoformat(),
                    'config': self.config
                },
                
                'performance_metrics': {
                    'success_rate': success_rate,
                    'successful_episodes': successful_episodes,
                    'failed_episodes': total_episodes - successful_episodes,
                    'average_steps': avg_steps,
                    'average_execution_time': avg_time,
                    'episodes_per_hour': (total_episodes / total_time) * 3600 if total_time > 0 else 0
                },
                
                'agent_statistics': final_agent_stats,
                
                'domain_performance': domain_performance,
                
                'learning_analysis': learning_analysis,
                
                'error_analysis': error_analysis,
                
                'performance_trends': self.session_metrics['performance_trends'],
                
                'detailed_results': self.results if self.config.get('save_detailed_logs', True) else None
            }
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error generating final results: {e}")
            return {'error': str(e)}
    
    def _analyze_domain_performance(self) -> Dict[str, Any]:
        """
        Analyze performance by task domain.
        """
        domain_stats = {}
        
        for result in self.results:
            task_name = result.get('task_name', 'unknown')
            domain = self._extract_domain_from_task(task_name)
            
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'total': 0,
                    'successful': 0,
                    'total_steps': 0,
                    'total_time': 0.0
                }
            
            domain_stats[domain]['total'] += 1
            domain_stats[domain]['total_steps'] += result.get('steps', 0)
            domain_stats[domain]['total_time'] += result.get('execution_time', 0.0)
            
            if result.get('success', False):
                domain_stats[domain]['successful'] += 1
        
        # Calculate derived metrics
        for domain, stats in domain_stats.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['successful'] / stats['total']) * 100
                stats['avg_steps'] = stats['total_steps'] / stats['total']
                stats['avg_time'] = stats['total_time'] / stats['total']
            else:
                stats['success_rate'] = 0
                stats['avg_steps'] = 0
                stats['avg_time'] = 0
        
        return domain_stats
    
    def _extract_domain_from_task(self, task_name: str) -> str:
        """
        Extract domain from task name.
        """
        task_lower = task_name.lower()
        
        if 'omnizon' in task_lower:
            return 'omnizon'
        elif 'email' in task_lower or 'mail' in task_lower:
            return 'email'
        elif 'calendar' in task_lower:
            return 'calendar'
        elif 'social' in task_lower:
            return 'social'
        else:
            return 'other'
    
    def _analyze_learning_progression(self) -> Dict[str, Any]:
        """
        Analyze learning progression over time.
        """
        if len(self.session_metrics['performance_trends']) < 2:
            return {'status': 'insufficient_data'}
        
        trends = self.session_metrics['performance_trends']
        
        # Calculate learning metrics
        initial_success_rate = trends[0]['success_rate']
        final_success_rate = trends[-1]['success_rate']
        success_rate_improvement = final_success_rate - initial_success_rate
        
        initial_avg_steps = trends[0]['avg_steps']
        final_avg_steps = trends[-1]['avg_steps']
        steps_improvement = initial_avg_steps - final_avg_steps
        
        # Detect learning phases
        learning_phases = []
        for i in range(1, len(trends)):
            prev_trend = trends[i-1]
            curr_trend = trends[i]
            
            if curr_trend['success_rate'] > prev_trend['success_rate'] + 0.1:
                learning_phases.append({
                    'episode': curr_trend['episode'],
                    'type': 'success_rate_jump',
                    'improvement': curr_trend['success_rate'] - prev_trend['success_rate']
                })
        
        return {
            'status': 'analyzed',
            'success_rate_improvement': success_rate_improvement,
            'steps_improvement': steps_improvement,
            'learning_phases': learning_phases,
            'total_improvements': len(self.session_metrics['learning_improvements']),
            'memory_growth': trends[-1]['memory_size'] - trends[0]['memory_size'] if len(trends) > 1 else 0
        }
    
    def _analyze_errors(self) -> Dict[str, Any]:
        """
        Analyze error patterns and frequencies.
        """
        total_errors = sum(self.session_metrics['error_patterns'].values())
        
        if total_errors == 0:
            return {'status': 'no_errors'}
        
        # Calculate error percentages
        error_percentages = {}
        for error_type, count in self.session_metrics['error_patterns'].items():
            error_percentages[error_type] = (count / total_errors) * 100
        
        # Find most common error
        most_common_error = max(self.session_metrics['error_patterns'].items(), key=lambda x: x[1])
        
        return {
            'status': 'analyzed',
            'total_errors': total_errors,
            'error_types': self.session_metrics['error_patterns'],
            'error_percentages': error_percentages,
            'most_common_error': {
                'type': most_common_error[0],
                'count': most_common_error[1],
                'percentage': error_percentages[most_common_error[0]]
            }
        }
    
    def _save_final_results(self, results: Dict[str, Any]):
        """
        Save final results to file.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"enhanced_benchmark_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Final results saved to {results_file}")
            
            # Also save a latest results file
            latest_file = self.results_dir / "latest_results.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error saving final results: {e}")
    
    def _generate_reports(self, results: Dict[str, Any]):
        """
        Generate human-readable reports.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.results_dir / f"benchmark_report_{timestamp}.md"
            
            with open(report_file, 'w') as f:
                f.write(self._generate_markdown_report(results))
            
            logger.info(f"Benchmark report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive markdown report.
        """
        report = f"""
# Enhanced Agent v2.0 Benchmark Report

**Generated:** {results['benchmark_info']['timestamp']}  
**Agent Type:** {results['benchmark_info']['agent_type']}  
**Total Episodes:** {results['benchmark_info']['total_episodes']}  
**Total Time:** {results['benchmark_info']['total_time']:.2f} seconds  

## Performance Summary

- **Success Rate:** {results['performance_metrics']['success_rate']:.1f}%
- **Successful Episodes:** {results['performance_metrics']['successful_episodes']}
- **Failed Episodes:** {results['performance_metrics']['failed_episodes']}
- **Average Steps per Episode:** {results['performance_metrics']['average_steps']:.1f}
- **Average Execution Time:** {results['performance_metrics']['average_execution_time']:.2f}s
- **Episodes per Hour:** {results['performance_metrics']['episodes_per_hour']:.1f}

## Domain Performance

"""
        
        # Add domain performance table
        if 'domain_performance' in results:
            report += "| Domain | Episodes | Success Rate | Avg Steps | Avg Time |\n"
            report += "|--------|----------|--------------|-----------|----------|\n"
            
            for domain, stats in results['domain_performance'].items():
                report += f"| {domain} | {stats['total']} | {stats['success_rate']:.1f}% | {stats['avg_steps']:.1f} | {stats['avg_time']:.2f}s |\n"
        
        # Add learning analysis
        if 'learning_analysis' in results and results['learning_analysis']['status'] == 'analyzed':
            learning = results['learning_analysis']
            report += f"""

## Learning Analysis

- **Success Rate Improvement:** {learning['success_rate_improvement']:.1f}%
- **Steps Improvement:** {learning['steps_improvement']:.1f}
- **Learning Phases Detected:** {len(learning['learning_phases'])}
- **Total Improvements:** {learning['total_improvements']}
- **Memory Growth:** {learning['memory_growth']} episodes

"""
        
        # Add error analysis
        if 'error_analysis' in results and results['error_analysis']['status'] == 'analyzed':
            errors = results['error_analysis']
            report += f"""

## Error Analysis

- **Total Errors:** {errors['total_errors']}
- **Most Common Error:** {errors['most_common_error']['type']} ({errors['most_common_error']['percentage']:.1f}%)

### Error Breakdown

"""
            for error_type, percentage in errors['error_percentages'].items():
                report += f"- **{error_type}:** {percentage:.1f}%\n"
        
        # Add agent statistics
        if 'agent_statistics' in results:
            agent_stats = results['agent_statistics']
            report += f"""

## Agent Statistics

### Performance Metrics
- **Total Actions:** {agent_stats.get('performance_metrics', {}).get('total_actions', 'N/A')}
- **Success Rate:** {agent_stats.get('performance_metrics', {}).get('success_rate', 0):.1%}
- **Average Response Time:** {agent_stats.get('performance_metrics', {}).get('avg_response_time', 0):.3f}s

### System Status
- **Memory Enabled:** {agent_stats.get('system_status', {}).get('memory_enabled', 'N/A')}
- **Planning Enabled:** {agent_stats.get('system_status', {}).get('planning_enabled', 'N/A')}
- **Critique Enabled:** {agent_stats.get('system_status', {}).get('critique_enabled', 'N/A')}
- **Episodic Memory Size:** {agent_stats.get('system_status', {}).get('episodic_memory_size', 'N/A')}

"""
        
        report += """

## Configuration

```json
"""
        report += json.dumps(results['benchmark_info']['config'], indent=2)
        report += """
```

---

*Report generated by Enhanced Agent v2.0 Benchmark Runner*
"""
        
        return report

def main():
    """
    Main function to run the enhanced benchmark.
    """
    print("Enhanced Agent v2.0 REAL Benchmark")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not set. The agent may not function properly.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    
    try:
        # Create benchmark runner with enhanced configuration
        config = {
            'agent_config': {
                'max_steps': 50,
                'timeout_ms': 3000,
                'enable_learning': True,
                'enable_planning': True,
                'enable_critique': True,
                'max_episodes': 10000,
                'max_retries': 5,
                'base_delay': 1.0,
                'persistence_dir': './agent_data'
            },
            'benchmark_config': {
                'max_steps': 50,
                'action_space': 'browsergym',
                'observation_space': 'browsergym',
                'headless': True,
                'record_video': False,
                'enable_screenshots': True
            },
            'monitoring': {
                'log_interval': 5,
                'save_interval': 25,
                'performance_window': 50,
                'enable_real_time_metrics': True
            },
            'results_dir': './benchmark_results',
            'save_detailed_logs': True,
            'generate_reports': True
        }
        
        runner = EnhancedBenchmarkRunner(config)
        
        # Run benchmark
        print("\nStarting benchmark execution...")
        results = runner.run_benchmark(num_episodes=100)  # Run 100 episodes for demo
        
        # Display summary
        print("\n" + "=" * 50)
        print("BENCHMARK COMPLETED")
        print("=" * 50)
        print(f"Success Rate: {results['performance_metrics']['success_rate']:.1f}%")
        print(f"Total Episodes: {results['performance_metrics']['successful_episodes'] + results['performance_metrics']['failed_episodes']}")
        print(f"Average Steps: {results['performance_metrics']['average_steps']:.1f}")
        print(f"Average Time: {results['performance_metrics']['average_execution_time']:.2f}s")
        
        if 'learning_analysis' in results and results['learning_analysis']['status'] == 'analyzed':
            learning = results['learning_analysis']
            print(f"\nLearning Progress:")
            print(f"  Success Rate Improvement: {learning['success_rate_improvement']:.1f}%")
            print(f"  Steps Improvement: {learning['steps_improvement']:.1f}")
            print(f"  Learning Phases: {len(learning['learning_phases'])}")
        
        print(f"\nDetailed results saved to: {runner.results_dir}")
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
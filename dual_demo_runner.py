#!/usr/bin/env python3
"""
Dual Demo Runner: Execute Price Comparison and News Intelligence Demos Simultaneously
This script runs both demos in parallel using threading to demonstrate concurrent execution.
"""

import os
import time
import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the demo classes
from wow_demo_1_price_comparison import PriceComparisonDemo
from wow_demo_3_news_intelligence import NewsIntelligenceDemo


class DualDemoRunner:
    """Manages concurrent execution of multiple demos"""
    
    def __init__(self):
        # Load API key from environment
        self.api_key = os.getenv('NOVA_ACT_API_KEY')
        if not self.api_key:
            raise ValueError("NOVA_ACT_API_KEY not found in environment variables")
        
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def run_price_comparison_demo(self) -> Dict[str, Any]:
        """Run the price comparison demo in a separate thread"""
        try:
            print("🛒 [PRICE DEMO] Starting Price Comparison Demo...")
            demo = PriceComparisonDemo()
            result = demo.run_price_comparison()
            
            return {
                "demo": "price_comparison",
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ [PRICE DEMO] Error: {str(e)}")
            return {
                "demo": "price_comparison",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_news_intelligence_demo(self) -> Dict[str, Any]:
        """Run the news intelligence demo in a separate thread"""
        try:
            print("📰 [NEWS DEMO] Starting News Intelligence Demo...")
            demo = NewsIntelligenceDemo(self.api_key)
            result = demo.analyze_trending_topics("technology")
            
            return {
                "demo": "news_intelligence",
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ [NEWS DEMO] Error: {str(e)}")
            return {
                "demo": "news_intelligence",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_both_demos_concurrent(self) -> Dict[str, Any]:
        """Execute both demos simultaneously using ThreadPoolExecutor"""
        print("🚀 Starting Dual Demo Execution...")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Use ThreadPoolExecutor for better thread management
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both demos to the thread pool
            future_price = executor.submit(self.run_price_comparison_demo)
            future_news = executor.submit(self.run_news_intelligence_demo)
            
            # Collect results as they complete
            futures = {
                future_price: "price_comparison",
                future_news: "news_intelligence"
            }
            
            completed_demos = []
            
            for future in as_completed(futures):
                demo_name = futures[future]
                try:
                    result = future.result()
                    self.results[demo_name] = result
                    completed_demos.append(demo_name)
                    print(f"✅ [{demo_name.upper()}] Demo completed successfully!")
                except Exception as e:
                    print(f"❌ [{demo_name.upper()}] Demo failed: {str(e)}")
                    self.results[demo_name] = {
                        "demo": demo_name,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
        
        self.end_time = datetime.now()
        execution_time = (self.end_time - self.start_time).total_seconds()
        
        # Compile final results
        final_results = {
            "execution_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_execution_time_seconds": execution_time,
                "demos_completed": len(completed_demos),
                "success_rate": len([r for r in self.results.values() if r.get("status") == "success"]) / len(self.results) * 100
            },
            "demo_results": self.results
        }
        
        return final_results
    
    def run_both_demos_sequential(self) -> Dict[str, Any]:
        """Execute both demos one after another for comparison"""
        print("🔄 Starting Sequential Demo Execution...")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Run price comparison first
        price_result = self.run_price_comparison_demo()
        self.results["price_comparison"] = price_result
        
        # Run news intelligence second
        news_result = self.run_news_intelligence_demo()
        self.results["news_intelligence"] = news_result
        
        self.end_time = datetime.now()
        execution_time = (self.end_time - self.start_time).total_seconds()
        
        # Compile final results
        final_results = {
            "execution_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_execution_time_seconds": execution_time,
                "execution_mode": "sequential",
                "demos_completed": len(self.results),
                "success_rate": len([r for r in self.results.values() if r.get("status") == "success"]) / len(self.results) * 100
            },
            "demo_results": self.results
        }
        
        return final_results
    
    def print_results_summary(self, results: Dict[str, Any]):
        """Print a formatted summary of the execution results"""
        print("\n" + "=" * 60)
        print("🎯 DUAL DEMO EXECUTION SUMMARY")
        print("=" * 60)
        
        summary = results["execution_summary"]
        print(f"⏱️  Total Execution Time: {summary['total_execution_time_seconds']:.2f} seconds")
        print(f"✅ Success Rate: {summary['success_rate']:.1f}%")
        print(f"📊 Demos Completed: {summary['demos_completed']}")
        
        print("\n📋 Individual Demo Results:")
        for demo_name, demo_result in results["demo_results"].items():
            status_emoji = "✅" if demo_result["status"] == "success" else "❌"
            print(f"  {status_emoji} {demo_name.replace('_', ' ').title()}: {demo_result['status']}")
            if demo_result["status"] == "error":
                print(f"    Error: {demo_result.get('error', 'Unknown error')}")
        
        print("\n🔗 Full results saved to: dual_demo_results.json")


def main():
    """Main execution function"""
    try:
        runner = DualDemoRunner()
        
        # Ask user for execution mode
        print("🤖 Dual Demo Runner")
        print("Choose execution mode:")
        print("1. Concurrent (both demos run simultaneously)")
        print("2. Sequential (demos run one after another)")
        print("3. Both modes for comparison")
        
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == "1":
            results = runner.run_both_demos_concurrent()
            results["execution_summary"]["execution_mode"] = "concurrent"
        elif choice == "2":
            results = runner.run_both_demos_sequential()
        elif choice == "3":
            print("\n🔄 Running Sequential Mode First...")
            sequential_results = runner.run_both_demos_sequential()
            
            # Reset for concurrent run
            runner.results = {}
            print("\n🚀 Running Concurrent Mode...")
            concurrent_results = runner.run_both_demos_concurrent()
            concurrent_results["execution_summary"]["execution_mode"] = "concurrent"
            
            # Compare results
            results = {
                "comparison": {
                    "sequential": sequential_results,
                    "concurrent": concurrent_results,
                    "time_saved": sequential_results["execution_summary"]["total_execution_time_seconds"] - 
                                concurrent_results["execution_summary"]["total_execution_time_seconds"]
                }
            }
            
            print(f"\n⚡ Time Saved with Concurrent Execution: {results['comparison']['time_saved']:.2f} seconds")
        else:
            print("❌ Invalid choice. Running concurrent mode by default.")
            results = runner.run_both_demos_concurrent()
            results["execution_summary"]["execution_mode"] = "concurrent"
        
        # Print summary
        if choice != "3":
            runner.print_results_summary(results)
        
        # Save results to file
        with open("dual_demo_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results
        
    except Exception as e:
        print(f"❌ Fatal error in dual demo runner: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    result = main()
    print(f"\n🎯 Execution completed. Check dual_demo_results.json for detailed results.")
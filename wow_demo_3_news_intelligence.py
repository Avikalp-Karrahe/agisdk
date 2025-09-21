#!/usr/bin/env python3
"""
🚀 WOW DEMO #3: Real-Time News Intelligence & Sentiment Analysis
================================================================

This demo showcases Nova Act's ability to analyze news across multiple sources,
extract trending topics, perform sentiment analysis, and generate intelligent
insights about current events and public opinion.

WOW FACTORS:
- Multi-source news aggregation and analysis
- Real-time sentiment analysis of articles and comments
- Trending topic identification and correlation
- Intelligent news summarization and insights
- Cross-platform opinion analysis
"""

import os
import json
import time
from datetime import datetime
from nova_act import NovaAct
from typing import Dict, List, Any


class NewsIntelligenceDemo:
    """Real-time news analysis and sentiment intelligence"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.news_sources = [
            {"name": "Hacker News", "url": "https://news.ycombinator.com", "type": "tech"},
            {"name": "BBC News", "url": "https://www.bbc.com/news", "type": "general"},
            {"name": "Reddit WorldNews", "url": "https://www.reddit.com/r/worldnews", "type": "social"},
            {"name": "TechCrunch", "url": "https://techcrunch.com", "type": "tech"},
            {"name": "Reuters", "url": "https://www.reuters.com", "type": "general"}
        ]
        
    def analyze_trending_topics(self, topic_focus: str = "technology") -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Cross-platform trending topic analysis
        - Identifies trending topics across multiple news sources
        - Correlates stories between different platforms
        - Tracks topic evolution and sentiment shifts
        """
        print(f"📈 Analyzing trending topics in: {topic_focus}")
        
        analysis_results = {
            "focus_area": topic_focus,
            "sources_analyzed": [],
            "trending_topics": [],
            "sentiment_overview": {},
            "cross_platform_correlations": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Analyze Hacker News for tech trends
        print("\n🔍 Analyzing Hacker News...")
        try:
            with NovaAct(starting_page="https://news.ycombinator.com", nova_act_api_key=self.api_key) as nova:
                
                schema = {
                    "type": "object",
                    "properties": {
                        "trending_stories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "points": {"type": "integer"},
                                    "comments": {"type": "integer"},
                                    "topic_category": {"type": "string"},
                                    "sentiment_indicators": {"type": "string"},
                                    "key_themes": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "overall_trends": {"type": "array", "items": {"type": "string"}},
                        "sentiment_summary": {"type": "string"}
                    }
                }
                
                result = nova.act(f"""
                Analyze the current trending stories on Hacker News with focus on {topic_focus}.
                
                Extract the top 10 stories and for each one:
                1. Title and engagement metrics (points, comments)
                2. Categorize the topic (AI/ML, Web Dev, Startups, Hardware, etc.)
                3. Assess sentiment indicators from title and discussion
                4. Identify key themes or technologies mentioned
                
                Then provide:
                - Overall trending themes you observe
                - General sentiment of the community (positive, negative, mixed)
                - Any emerging patterns or hot topics
                
                Focus on stories related to {topic_focus} but include other significant trends.
                """, schema=schema, max_steps=6, timeout=45)
                
                if result and hasattr(result, 'response'):
                    hn_data = result.response
                    hn_data['source'] = 'Hacker News'
                    analysis_results['sources_analyzed'].append(hn_data)
                    print("✅ Hacker News analysis completed")
                
        except Exception as e:
            print(f"❌ Error analyzing Hacker News: {e}")
        
        # Analyze Reddit for social sentiment
        print("\n🔍 Analyzing Reddit WorldNews...")
        try:
            with NovaAct(starting_page="https://www.reddit.com/r/worldnews", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Analyze the current hot posts on r/worldnews for trending global topics.
                
                Look at the top 10 posts and extract:
                1. Post titles and upvote counts
                2. Main topics/countries/events mentioned
                3. Sentiment from titles and top comments (if visible)
                4. Identify any topics related to {topic_focus}
                5. Note any breaking news or developing stories
                
                Provide insights on:
                - What global events are trending
                - Public sentiment on major issues
                - Any technology-related global news
                - Correlation with other trending topics
                """, max_steps=6, timeout=45)
                
                if result and hasattr(result, 'response'):
                    reddit_data = {
                        'source': 'Reddit WorldNews',
                        'analysis': str(result.response),
                        'focus_area': 'global_events'
                    }
                    analysis_results['sources_analyzed'].append(reddit_data)
                    print("✅ Reddit analysis completed")
                
        except Exception as e:
            print(f"❌ Error analyzing Reddit: {e}")
        
        # Synthesize cross-platform insights
        self._synthesize_insights(analysis_results)
        return analysis_results
    
    def sentiment_deep_dive(self, specific_topic: str = "artificial intelligence") -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Deep sentiment analysis on specific topics
        - Analyzes sentiment across multiple platforms
        - Tracks opinion evolution and debate points
        - Identifies influencers and key discussions
        """
        print(f"🎭 Deep sentiment analysis on: {specific_topic}")
        
        sentiment_results = {
            "topic": specific_topic,
            "platforms_analyzed": [],
            "sentiment_breakdown": {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "mixed": 0
            },
            "key_opinion_points": [],
            "debate_themes": [],
            "influencer_voices": []
        }
        
        try:
            # Search Google for recent discussions on the topic
            with NovaAct(starting_page="https://www.google.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(f"""
                Search for recent discussions and news about "{specific_topic}" and analyze sentiment.
                
                Steps:
                1. Search for "{specific_topic} news 2024" or "{specific_topic} discussion"
                2. Visit 2-3 different sources (news sites, forums, social media)
                3. For each source, analyze:
                   - Overall sentiment toward the topic
                   - Main arguments for and against
                   - Key concerns or excitement points
                   - Notable quotes or opinions
                
                4. Synthesize findings:
                   - What's the general public sentiment?
                   - What are the main debate points?
                   - Are there any notable shifts in opinion?
                   - What are people most excited/worried about?
                
                Provide a comprehensive sentiment analysis with specific examples.
                """, max_steps=10, timeout=75)
                
                if result and hasattr(result, 'response'):
                    sentiment_results['detailed_analysis'] = str(result.response)
                    print("✅ Sentiment analysis completed")
                
        except Exception as e:
            print(f"❌ Error in sentiment analysis: {e}")
            sentiment_results['error'] = str(e)
        
        return sentiment_results
    
    def breaking_news_monitor(self) -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Real-time breaking news detection and analysis
        - Monitors multiple sources for breaking news
        - Identifies developing stories and their impact
        - Tracks story evolution across platforms
        """
        print("🚨 Monitoring for breaking news and developing stories...")
        
        breaking_news_results = {
            "scan_timestamp": datetime.now().isoformat(),
            "breaking_stories": [],
            "developing_stories": [],
            "impact_analysis": {},
            "cross_platform_coverage": []
        }
        
        try:
            # Check BBC News for breaking news
            with NovaAct(starting_page="https://www.bbc.com/news", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Scan BBC News for any breaking news or developing stories.
                
                Look for:
                1. Stories marked as "Breaking" or "Live"
                2. Recently updated articles (check timestamps)
                3. Stories with high engagement or prominence
                4. Any major global events or developments
                
                For each significant story found:
                - Extract headline and key details
                - Note the urgency level and scope
                - Identify potential impact areas
                - Check if it's a developing story with updates
                
                Also assess:
                - Are there any major tech/business stories?
                - Any stories that might affect markets or society?
                - Any stories trending across multiple sections?
                
                Provide a prioritized list of the most significant current stories.
                """, max_steps=8, timeout=60)
                
                if result and hasattr(result, 'response'):
                    bbc_data = {
                        'source': 'BBC News',
                        'breaking_news_scan': str(result.response),
                        'scan_time': datetime.now().isoformat()
                    }
                    breaking_news_results['sources_scanned'] = [bbc_data]
                    print("✅ Breaking news scan completed")
                
        except Exception as e:
            print(f"❌ Error in breaking news monitor: {e}")
            breaking_news_results['error'] = str(e)
        
        return breaking_news_results
    
    def news_correlation_analysis(self) -> Dict[str, Any]:
        """
        🎯 WOW FACTOR: Cross-platform story correlation and trend analysis
        - Identifies the same stories across different platforms
        - Analyzes how different sources cover the same events
        - Tracks narrative differences and bias patterns
        """
        print("🔗 Analyzing story correlations across platforms...")
        
        correlation_results = {
            "analysis_type": "Cross-Platform Story Correlation",
            "platforms_compared": [],
            "common_stories": [],
            "narrative_differences": [],
            "bias_indicators": [],
            "coverage_gaps": []
        }
        
        try:
            # Compare tech news coverage between different sources
            with NovaAct(starting_page="https://news.ycombinator.com", nova_act_api_key=self.api_key) as nova:
                
                result = nova.act("""
                Analyze the top stories on Hacker News, then search for how the same 
                stories are covered on other platforms.
                
                Process:
                1. Identify the top 5 most discussed stories on Hacker News
                2. For each story, search Google to find coverage on:
                   - Traditional news sites (BBC, Reuters, CNN)
                   - Tech publications (TechCrunch, Ars Technica)
                   - Social platforms (Reddit discussions)
                
                3. For stories found on multiple platforms, analyze:
                   - How headlines differ between sources
                   - What aspects each platform emphasizes
                   - Differences in tone or perspective
                   - Which platform has more detailed coverage
                   - Any notable omissions or additions
                
                4. Identify patterns:
                   - Which stories get universal coverage?
                   - Which are platform-specific?
                   - How do technical vs. general audiences get different info?
                
                Provide insights on media coverage patterns and information flow.
                """, max_steps=12, timeout=90)
                
                if result and hasattr(result, 'response'):
                    correlation_results['detailed_analysis'] = str(result.response)
                    print("✅ Correlation analysis completed")
                
        except Exception as e:
            print(f"❌ Error in correlation analysis: {e}")
            correlation_results['error'] = str(e)
        
        return correlation_results
    
    def _synthesize_insights(self, analysis_results: Dict[str, Any]):
        """Synthesize insights from multiple sources"""
        if analysis_results['sources_analyzed']:
            # Extract trending topics
            all_topics = []
            for source in analysis_results['sources_analyzed']:
                if 'trending_stories' in source:
                    for story in source['trending_stories']:
                        if 'key_themes' in story:
                            all_topics.extend(story['key_themes'])
            
            # Count topic frequency
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Get top trending topics
            analysis_results['trending_topics'] = sorted(
                topic_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run the complete news intelligence analysis"""
        print("🚀 WOW DEMO #3: Real-Time News Intelligence")
        print("=" * 70)
        print("Demonstrating advanced news analysis and sentiment intelligence...")
        
        complete_results = {
            "analysis_suite": "News Intelligence & Sentiment Analysis",
            "analyses_completed": [],
            "key_insights": [],
            "wow_factors_demonstrated": []
        }
        
        # Run all analyses
        analyses = [
            ("Trending Topics Analysis", lambda: self.analyze_trending_topics("technology")),
            ("AI Sentiment Deep Dive", lambda: self.sentiment_deep_dive("artificial intelligence")),
            ("Breaking News Monitor", self.breaking_news_monitor),
            ("Cross-Platform Correlation", self.news_correlation_analysis)
        ]
        
        for analysis_name, analysis_func in analyses:
            print(f"\n{'='*50}")
            print(f"Running: {analysis_name}")
            print('='*50)
            
            try:
                result = analysis_func()
                result['analysis_name'] = analysis_name
                complete_results['analyses_completed'].append(result)
                print(f"✅ {analysis_name} completed!")
                
            except Exception as e:
                print(f"❌ {analysis_name} failed: {e}")
                complete_results['analyses_completed'].append({
                    'analysis_name': analysis_name,
                    'error': str(e)
                })
        
        # Generate summary insights
        print("\n" + "="*70)
        print("📊 NEWS INTELLIGENCE ANALYSIS RESULTS")
        print("="*70)
        
        successful_analyses = [a for a in complete_results['analyses_completed'] if 'error' not in a]
        print(f"✅ Successful Analyses: {len(successful_analyses)}/{len(analyses)}")
        
        print("\n✨ WOW FACTORS DEMONSTRATED:")
        wow_factors = [
            "📈 Multi-source trending topic identification",
            "🎭 Advanced sentiment analysis across platforms",
            "🚨 Real-time breaking news detection and monitoring",
            "🔗 Cross-platform story correlation and bias analysis",
            "🧠 Intelligent news summarization and insights",
            "📊 Public opinion tracking and trend analysis",
            "🌐 Global event impact assessment",
            "⚡ Real-time information synthesis and reporting"
        ]
        
        for factor in wow_factors:
            print(f"   {factor}")
        
        print(f"\n🕒 Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return complete_results


if __name__ == "__main__":
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Please set NOVA_ACT_API_KEY environment variable")
        exit(1)
    
    demo = NewsIntelligenceDemo(api_key)
    demo.run_complete_analysis()
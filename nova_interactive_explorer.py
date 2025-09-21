#!/usr/bin/env python3
"""
Nova Act Interactive Explorer
============================

An interactive command-line tool to explore Nova Act's capabilities
in real-time. Users can experiment with different commands, see results,
and learn about advanced features.
"""

import os
import json
import time
from nova_act import NovaAct
from typing import Dict, Any, List, Optional


class NovaInteractiveExplorer:
    """Interactive explorer for Nova Act capabilities"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.current_url = "https://www.google.com"
        self.session_history = []
        self.bookmarks = {}
        
    def print_banner(self):
        """Print the welcome banner"""
        print("🚀 Nova Act Interactive Explorer")
        print("=" * 50)
        print("Explore Nova Act's capabilities interactively!")
        print("Type 'help' for available commands")
        print("Type 'quit' to exit")
        print("=" * 50)
    
    def print_help(self):
        """Print help information"""
        help_text = """
🎯 Available Commands:

Basic Navigation:
  go <url>              - Navigate to a specific URL
  search <query>        - Search on current page or Google
  click <element>       - Click on an element
  type <text>           - Type text into active field
  scroll <direction>    - Scroll up/down/left/right

Advanced Features:
  extract <what>        - Extract specific data from page
  form <instructions>   - Fill out forms with instructions
  compare <items>       - Compare multiple items on page
  analyze <aspect>      - Analyze page for specific aspects
  workflow <steps>      - Execute multi-step workflow

Exploration Tools:
  demo <category>       - Run predefined demos
  bookmark <name>       - Bookmark current page
  bookmarks             - List all bookmarks
  history               - Show session history
  current               - Show current page info
  
Utility Commands:
  schema <json_schema>  - Set JSON schema for structured output
  timeout <seconds>     - Set timeout for operations
  steps <number>        - Set max steps for complex operations
  
System Commands:
  help                  - Show this help
  clear                 - Clear screen
  quit                  - Exit explorer

💡 Examples:
  go https://news.ycombinator.com
  extract "top 5 articles with titles and points"
  form "fill contact form with test data"
  demo ecommerce
  workflow "search for laptops, compare top 3, add cheapest to cart"
        """
        print(help_text)
    
    def execute_nova_command(self, instruction: str, **kwargs) -> Optional[str]:
        """Execute a Nova Act command with the given instruction"""
        try:
            with NovaAct(starting_page=self.current_url, 
                        nova_act_api_key=self.api_key) as nova:
                
                result = nova.act(instruction, **kwargs)
                
                # Log to history
                self.session_history.append({
                    'timestamp': time.time(),
                    'url': self.current_url,
                    'instruction': instruction,
                    'result': result.response[:200] + '...' if len(str(result.response)) > 200 else result.response
                })
                
                return result.response
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def handle_go_command(self, url: str):
        """Handle navigation to a specific URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.current_url = url
        result = self.execute_nova_command(f"Navigate to {url}")
        if result:
            print(f"✅ Navigated to: {url}")
            print(f"📄 Page info: {result}")
        
    def handle_demo_command(self, category: str):
        """Handle demo commands"""
        demos = {
            'ecommerce': self.demo_ecommerce,
            'news': self.demo_news_extraction,
            'forms': self.demo_form_filling,
            'research': self.demo_research_workflow,
            'social': self.demo_social_media,
            'data': self.demo_data_extraction
        }
        
        if category in demos:
            print(f"🎬 Running {category} demo...")
            demos[category]()
        else:
            print(f"❌ Unknown demo category: {category}")
            print(f"Available demos: {', '.join(demos.keys())}")
    
    def demo_ecommerce(self):
        """Demo e-commerce workflow"""
        self.current_url = "https://demo.opencart.com"
        result = self.execute_nova_command("""
        Simulate an e-commerce shopping experience:
        1. Search for a product (like 'phone' or 'laptop')
        2. Browse the results
        3. Click on an interesting product
        4. Extract product details (name, price, description)
        5. Add to cart and view cart contents
        6. Return structured information about the shopping experience
        """, max_steps=15)
        
        if result:
            print("🛒 E-commerce Demo Results:")
            print(result)
    
    def demo_news_extraction(self):
        """Demo news extraction"""
        self.current_url = "https://news.ycombinator.com"
        result = self.execute_nova_command("""
        Extract news information:
        1. Find the top 5 stories on the front page
        2. For each story, get title, points, and number of comments
        3. Click on one interesting story to read more
        4. Extract key information from that article
        5. Return a summary of findings
        """, max_steps=12)
        
        if result:
            print("📰 News Extraction Demo Results:")
            print(result)
    
    def demo_form_filling(self):
        """Demo form filling"""
        self.current_url = "https://httpbin.org/forms/post"
        result = self.execute_nova_command("""
        Demonstrate intelligent form filling:
        1. Analyze the form structure
        2. Fill all fields with appropriate test data
        3. Validate the form before submission
        4. Submit and capture the response
        5. Return details about the form interaction
        """)
        
        if result:
            print("📝 Form Filling Demo Results:")
            print(result)
    
    def demo_research_workflow(self):
        """Demo research workflow"""
        self.current_url = "https://www.google.com"
        result = self.execute_nova_command("""
        Perform a research workflow:
        1. Search for "machine learning trends 2024"
        2. Click on a reputable source
        3. Extract key trends and insights
        4. Look for supporting data or statistics
        5. Summarize the main findings
        """, max_steps=15)
        
        if result:
            print("🔬 Research Demo Results:")
            print(result)
    
    def demo_social_media(self):
        """Demo social media exploration"""
        self.current_url = "https://www.reddit.com"
        result = self.execute_nova_command("""
        Explore social media content:
        1. Navigate to a popular subreddit (like r/technology)
        2. Find trending posts
        3. Extract post titles, upvotes, and comment counts
        4. Click on an interesting post to read comments
        5. Summarize the discussion and sentiment
        """, max_steps=12)
        
        if result:
            print("📱 Social Media Demo Results:")
            print(result)
    
    def demo_data_extraction(self):
        """Demo structured data extraction"""
        self.current_url = "https://en.wikipedia.org/wiki/List_of_programming_languages"
        result = self.execute_nova_command("""
        Extract structured data:
        1. Find the main table of programming languages
        2. Extract information about 10 popular languages
        3. For each language, get: name, year created, paradigm
        4. Format as structured data
        5. Provide insights about language evolution
        """)
        
        if result:
            print("📊 Data Extraction Demo Results:")
            print(result)
    
    def show_history(self):
        """Show session history"""
        if not self.session_history:
            print("📝 No history yet")
            return
        
        print("📝 Session History:")
        print("-" * 50)
        for i, entry in enumerate(self.session_history[-10:], 1):  # Show last 10
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry['timestamp']))
            print(f"{i}. [{timestamp}] {entry['url']}")
            print(f"   Command: {entry['instruction'][:60]}...")
            print(f"   Result: {entry['result'][:100]}...")
            print()
    
    def show_bookmarks(self):
        """Show bookmarks"""
        if not self.bookmarks:
            print("🔖 No bookmarks yet")
            return
        
        print("🔖 Bookmarks:")
        for name, url in self.bookmarks.items():
            print(f"  {name}: {url}")
    
    def add_bookmark(self, name: str):
        """Add current page to bookmarks"""
        self.bookmarks[name] = self.current_url
        print(f"🔖 Bookmarked '{name}': {self.current_url}")
    
    def show_current_info(self):
        """Show current page information"""
        print(f"📍 Current URL: {self.current_url}")
        print(f"📊 Session commands: {len(self.session_history)}")
        print(f"🔖 Bookmarks: {len(self.bookmarks)}")
    
    def run_interactive_session(self):
        """Run the main interactive session"""
        self.print_banner()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🤖 Nova> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(' ', 1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Handle commands
                if command == 'quit' or command == 'exit':
                    print("👋 Goodbye! Thanks for exploring Nova Act!")
                    break
                
                elif command == 'help':
                    self.print_help()
                
                elif command == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                
                elif command == 'go':
                    if args:
                        self.handle_go_command(args)
                    else:
                        print("❌ Usage: go <url>")
                
                elif command == 'demo':
                    if args:
                        self.handle_demo_command(args)
                    else:
                        print("❌ Usage: demo <category>")
                        print("Available: ecommerce, news, forms, research, social, data")
                
                elif command == 'bookmark':
                    if args:
                        self.add_bookmark(args)
                    else:
                        print("❌ Usage: bookmark <name>")
                
                elif command == 'bookmarks':
                    self.show_bookmarks()
                
                elif command == 'history':
                    self.show_history()
                
                elif command == 'current':
                    self.show_current_info()
                
                elif command in ['search', 'click', 'type', 'scroll', 'extract', 
                               'form', 'compare', 'analyze', 'workflow']:
                    if args:
                        print(f"🔄 Executing {command} command...")
                        result = self.execute_nova_command(f"{command.title()}: {args}")
                        if result:
                            print(f"✅ Result: {result}")
                    else:
                        print(f"❌ Usage: {command} <instructions>")
                
                else:
                    # Treat as general Nova Act instruction
                    print("🔄 Executing custom instruction...")
                    result = self.execute_nova_command(user_input)
                    if result:
                        print(f"✅ Result: {result}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for exploring Nova Act!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


def main():
    """Main function to start the interactive explorer"""
    
    # Check for API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("❌ Error: NOVA_ACT_API_KEY environment variable not set")
        print("Please set your Nova Act API key:")
        print("export NOVA_ACT_API_KEY=your_api_key_here")
        return
    
    # Create and run explorer
    explorer = NovaInteractiveExplorer(api_key)
    explorer.run_interactive_session()


if __name__ == "__main__":
    main()
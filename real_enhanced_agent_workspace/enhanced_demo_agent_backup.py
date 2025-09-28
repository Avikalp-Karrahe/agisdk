def _get_exploration_pattern(self) -> str:
        """Analyze the page journey to identify navigation patterns"""
        if len(self.page_journey) < 3:
            return "Insufficient data"
            
        # Get the sequence of page types
        page_types = [entry["page_type"] for entry in self.page_journey[-5:]]
        
        # Identify common patterns
        if page_types.count("Search") > 2:
            return "Multiple searches - consider more specific search terms"
        elif page_types.count("Product") > 2:
            return "Multiple product pages - comparison shopping"
        elif "Search" in page_types and "Product" in page_types and "Cart/Checkout" in page_types:
            return "Search → Product → Checkout flow"
        elif page_types[-3:].count("Homepage") > 1:
            return "Returning to homepage frequently - may be lost"
        elif len(set(page_types[-3:])) == 1:
            return f"Staying on {page_types[-1]} pages"
        
        # Check for back-and-forth navigation
        if len(self.page_journey) > 3:
            recent_urls = [entry["url"] for entry in self.page_journey[-4:]]
            if len(set(recent_urls)) < len(recent_urls):
                return "Back-and-forth navigation between pages"
                
        return "Mixed navigation pattern"
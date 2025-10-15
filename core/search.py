"""
Web search integration module for WellNavigator.
Provides interface for web search with stubbed implementation.
"""

import os
import time
from typing import List, Dict, Optional
import json

try:
    import requests
except ImportError:
    requests = None


class WebSearchInterface:
    """Interface for web search functionality."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self._configured = bool(self.api_key and self.cse_id)
    
    def is_available(self) -> bool:
        """Check if web search is properly configured."""
        return self._configured
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """
        Perform web search and return results.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of dictionaries with 'title', 'snippet', 'url' keys
        """
        if not self._configured:
            return self._get_stub_results(query, k)
        
        try:
            return self._google_search(query, k)
        except Exception as e:
            print(f"Search error: {e}")
            return self._get_stub_results(query, k)
    
    def _google_search(self, query: str, k: int) -> List[Dict[str, str]]:
        """Perform actual Google Custom Search."""
        if not requests:
            print("❌ requests library not available")
            return self._get_stub_results(query, k)
        
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': min(k, 10),  # Google API limit
            'safe': 'active',  # Safe search for health content
            'fields': 'items(title,snippet,link)'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', [])[:k]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': self._extract_domain(item.get('link', ''))
                })
            
            return results
            
        except requests.RequestException as e:
            print(f"Google Search API error: {e}")
            return self._get_stub_results(query, k)
        except KeyError as e:
            print(f"Unexpected API response format: {e}")
            return self._get_stub_results(query, k)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL for source attribution."""
        if not url:
            return "Unknown"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Clean up domain for better display
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Map common health domains to friendly names
            domain_map = {
                'mayoclinic.org': 'Mayo Clinic',
                'webmd.com': 'WebMD',
                'healthline.com': 'Healthline',
                'medlineplus.gov': 'MedlinePlus',
                'cdc.gov': 'CDC',
                'nih.gov': 'NIH',
                'who.int': 'WHO',
                'clevelandclinic.org': 'Cleveland Clinic',
                'hopkinsmedicine.org': 'Johns Hopkins',
                'harvard.edu': 'Harvard Health'
            }
            
            return domain_map.get(domain, domain.title())
            
        except:
            return "Web Source"
    
    def _get_stub_results(self, query: str, k: int) -> List[Dict[str, str]]:
        """Return stub results when search is not configured."""
        # Generate contextual stub results based on query
        stub_results = []
        
        # Health-focused stub results
        health_stubs = [
            {
                'title': 'Mayo Clinic - Comprehensive Health Information',
                'snippet': f'Expert medical information and resources about {query.lower()}. Mayo Clinic provides trusted health guidance from medical professionals.',
                'url': 'https://www.mayoclinic.org',
                'source': 'Mayo Clinic'
            },
            {
                'title': 'MedlinePlus - Reliable Health Information',
                'snippet': f'Authoritative health information from the National Library of Medicine about {query.lower()}. Includes symptoms, treatments, and prevention.',
                'url': 'https://medlineplus.gov',
                'source': 'MedlinePlus'
            },
            {
                'title': 'WebMD - Health Information and Resources',
                'snippet': f'Comprehensive health information about {query.lower()}. Find symptoms, treatments, and expert medical advice.',
                'url': 'https://www.webmd.com',
                'source': 'WebMD'
            }
        ]
        
        # Add query-specific stubs for common health topics
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['diabetes', 'blood sugar', 'insulin']):
            stub_results.extend([
                {
                    'title': 'American Diabetes Association - Diabetes Management',
                    'snippet': 'Comprehensive diabetes information, management strategies, and resources from the leading diabetes organization.',
                    'url': 'https://www.diabetes.org',
                    'source': 'American Diabetes Association'
                },
                {
                    'title': 'CDC - Diabetes Prevention and Management',
                    'snippet': 'Evidence-based information about diabetes prevention, management, and complications from the Centers for Disease Control.',
                    'url': 'https://www.cdc.gov/diabetes',
                    'source': 'CDC'
                }
            ])
        
        if any(term in query_lower for term in ['blood pressure', 'hypertension', 'high bp']):
            stub_results.extend([
                {
                    'title': 'American Heart Association - Blood Pressure Resources',
                    'snippet': 'Expert guidance on blood pressure management, healthy lifestyle choices, and cardiovascular health.',
                    'url': 'https://www.heart.org',
                    'source': 'American Heart Association'
                }
            ])
        
        if any(term in query_lower for term in ['doctor', 'appointment', 'visit']):
            stub_results.extend([
                {
                    'title': 'AHRQ - Tips for Doctor Visits',
                    'snippet': 'Evidence-based tips for making the most of your healthcare appointments from the Agency for Healthcare Research and Quality.',
                    'url': 'https://www.ahrq.gov',
                    'source': 'AHRQ'
                }
            ])
        
        # Combine health stubs with query-specific stubs
        all_stubs = health_stubs + stub_results
        
        # Return up to k results, removing duplicates
        seen_titles = set()
        unique_results = []
        
        for stub in all_stubs:
            if stub['title'] not in seen_titles:
                unique_results.append(stub)
                seen_titles.add(stub['title'])
                
                if len(unique_results) >= k:
                    break
        
        return unique_results[:k]


# Global search interface instance
_search_interface = None

def get_search_interface() -> WebSearchInterface:
    """Get or create global web search interface."""
    global _search_interface
    if _search_interface is None:
        _search_interface = WebSearchInterface()
    return _search_interface

def web_search(query: str, k: int = 3) -> List[Dict[str, str]]:
    """
    Convenience function to perform web search.
    
    Args:
        query: Search query string
        k: Number of results to return
        
    Returns:
        List of search results with title, snippet, url, and source
    """
    search_interface = get_search_interface()
    return search_interface.search(query, k)

def is_search_available() -> bool:
    """Check if web search is available and configured."""
    search_interface = get_search_interface()
    return search_interface.is_available()

def get_search_status() -> Dict[str, any]:
    """Get search configuration status."""
    search_interface = get_search_interface()
    
    return {
        "configured": search_interface.is_available(),
        "api_key_set": bool(os.getenv("GOOGLE_API_KEY")),
        "cse_id_set": bool(os.getenv("GOOGLE_CSE_ID")),
        "requests_available": requests is not None
    }

def reformulate_query_for_search(user_query: str, context: str = "") -> str:
    """
    Reformulate user query for better web search results.
    
    Args:
        user_query: Original user query
        context: Optional context from conversation
        
    Returns:
        Reformulated search query
    """
    # Basic query enhancement for health searches
    query = user_query.strip()
    
    # Add health context if not present
    if not any(term in query.lower() for term in ['health', 'medical', 'doctor', 'treatment', 'symptoms', 'condition']):
        # Check if it's likely a health query based on keywords
        health_keywords = [
            'diabetes', 'blood pressure', 'hypertension', 'cholesterol', 'heart',
            'pain', 'symptoms', 'medication', 'treatment', 'diagnosis', 'test',
            'appointment', 'visit', 'specialist', 'insurance', 'bill', 'cost'
        ]
        
        if any(keyword in query.lower() for keyword in health_keywords):
            query = f"{query} health medical information"
    
    # Add site preferences for reliable sources
    reliable_sites = [
        'mayoclinic.org', 'webmd.com', 'medlineplus.gov', 'cdc.gov', 
        'nih.gov', 'who.int', 'clevelandclinic.org'
    ]
    
    # For now, just return the enhanced query
    # In a full implementation, you might add site: operators
    return query

def test_search() -> Dict[str, any]:
    """Test the search functionality."""
    search_interface = get_search_interface()
    
    # Test queries
    test_queries = [
        "diabetes symptoms",
        "high blood pressure management", 
        "doctor visit preparation"
    ]
    
    results = {}
    
    for query in test_queries:
        try:
            search_results = search_interface.search(query, k=2)
            results[query] = {
                "success": True,
                "results_count": len(search_results),
                "sources": [r['source'] for r in search_results]
            }
        except Exception as e:
            results[query] = {
                "success": False,
                "error": str(e)
            }
    
    return {
        "search_available": search_interface.is_available(),
        "test_results": results,
        "status": get_search_status()
    }

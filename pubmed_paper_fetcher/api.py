"""Module for interacting with the PubMed API."""

import logging
from typing import Dict, List, Optional, Any
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time

logger = logging.getLogger(__name__)

class PubMedAPI:
    """Class for interacting with the PubMed API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, email: str, tool: str = "pubmed_paper_fetcher", api_key: Optional[str] = None):
        """
        Initialize the PubMed API client.
        
        Args:
            email: Email address of the user (required by NCBI)
            tool: Name of the tool (required by NCBI)
            api_key: NCBI API key for higher rate limits (optional)
        """
        self.email = email
        self.tool = tool
        self.api_key = api_key
    
    def search(self, query: str, retmax: int = 100) -> List[str]:
        """
        Search PubMed for papers matching the query.
        
        Args:
            query: PubMed search query
            retmax: Maximum number of results to return
            
        Returns:
            List of PubMed IDs matching the query
        """
        logger.debug(f"Searching PubMed with query: {query}")
        
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": str(retmax),
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email,
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        search_url = f"{self.BASE_URL}esearch.fcgi?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(search_url) as response:
                data = response.read()
                root = ET.fromstring(data)
                
                id_list = root.find("IdList")
                if id_list is None:
                    return []
                
                return [id_elem.text for id_elem in id_list.findall("Id")]
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
    
    def fetch_details(self, pmids: List[str]) -> Dict[str, Any]:
        """
        Fetch detailed information for a list of PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            Dictionary containing the XML response
        """
        if not pmids:
            return {}
            
        logger.debug(f"Fetching details for {len(pmids)} PubMed IDs")
        
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email,
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        fetch_url = f"{self.BASE_URL}efetch.fcgi?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(fetch_url) as response:
                data = response.read()
                root = ET.fromstring(data)
                
                # Process the XML to extract article details
                articles = {}
                for article_elem in root.findall(".//PubmedArticle"):
                    pmid_elem = article_elem.find(".//PMID")
                    if pmid_elem is not None and pmid_elem.text:
                        articles[pmid_elem.text] = article_elem
                
                return articles
        except Exception as e:
            logger.error(f"Error fetching details from PubMed: {e}")
            raise
    
    def search_and_fetch(self, query: str, retmax: int = 100) -> Dict[str, Any]:
        """
        Search PubMed and fetch details for matching papers.
        
        Args:
            query: PubMed search query
            retmax: Maximum number of results to return
            
        Returns:
            Dictionary mapping PubMed IDs to article details
        """
        pmids = self.search(query, retmax)
        
        # NCBI recommends no more than 3 requests per second
        time.sleep(0.33)
        
        return self.fetch_details(pmids)

print("PubMed API module loaded successfully")
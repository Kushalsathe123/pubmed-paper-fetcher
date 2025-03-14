"""Module for parsing PubMed API responses."""

import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any

from .affiliations import AffiliationDetector

logger = logging.getLogger(__name__)

class PubMedParser:
    """Class for parsing PubMed API responses."""
    
    @staticmethod
    def extract_title(article: ET.Element) -> str:
        """
        Extract the title of the article.
        
        Args:
            article: XML element representing the article
            
        Returns:
            Title of the article
        """
        title_elem = article.find(".//ArticleTitle")
        return title_elem.text if title_elem is not None and title_elem.text else "Unknown Title"
    
    @staticmethod
    def extract_publication_date(article: ET.Element) -> str:
        """
        Extract the publication date of the article.
        
        Args:
            article: XML element representing the article
            
        Returns:
            Publication date in YYYY-MM-DD format if available, otherwise partial date
        """
        pub_date = article.find(".//PubDate")
        if pub_date is None:
            return "Unknown Date"
            
        year = pub_date.find("Year")
        month = pub_date.find("Month")
        day = pub_date.find("Day")
        
        year_str = year.text if year is not None and year.text else "XXXX"
        month_str = month.text if month is not None and month.text else "XX"
        day_str = day.text if day is not None and day.text else "XX"
        
        # Handle month names
        try:
            if month_str.isalpha():
                from datetime import datetime
                month_str = str(datetime.strptime(month_str[:3], "%b").month).zfill(2)
        except (ValueError, AttributeError):
            month_str = "XX"
            
        if year_str != "XXXX":
            if month_str != "XX" and day_str != "XX":
                return f"{year_str}-{month_str}-{day_str}"
            elif month_str != "XX":
                return f"{year_str}-{month_str}"
            else:
                return year_str
        
        return "Unknown Date"
    
    @classmethod
    def extract_author_affiliations(cls, article: ET.Element) -> List[Tuple[str, str, Optional[str]]]:
        """
        Extract authors and their affiliations from the article.
        
        Args:
            article: XML element representing the article
            
        Returns:
            List of tuples containing (author name, affiliation, email if available)
        """
        result = []
        
        author_list = article.find(".//AuthorList")
        if author_list is None:
            return result
            
        for author in author_list.findall("Author"):
            # Extract author name
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            initials = author.find("Initials")
            
            if last_name is not None and last_name.text:
                if fore_name is not None and fore_name.text:
                    name = f"{fore_name.text} {last_name.text}"
                elif initials is not None and initials.text:
                    name = f"{initials.text} {last_name.text}"
                else:
                    name = last_name.text
            else:
                # Skip authors without names
                continue
                
            # Extract affiliation
            affiliation_elem = author.find("AffiliationInfo/Affiliation")
            affiliation = affiliation_elem.text if affiliation_elem is not None and affiliation_elem.text else ""
            
            # Extract email (if present in the affiliation text)
            email = AffiliationDetector.extract_email(affiliation) if affiliation else None
            
            result.append((name, affiliation, email))
            
        return result
    
    @classmethod
    def extract_corresponding_author_email(cls, article: ET.Element) -> Optional[str]:
        """
        Extract the email of the corresponding author.
        
        Args:
            article: XML element representing the article
            
        Returns:
            Email of the corresponding author if available, None otherwise
        """
        # First check if there's an explicit corresponding author
        for author in article.findall(".//Author"):
            if author.get("ValidYN") == "Y" and author.get("CorrespondingAuthor") == "Y":
                affiliations = author.findall("AffiliationInfo/Affiliation")
                for affiliation in affiliations:
                    if affiliation.text:
                        email = AffiliationDetector.extract_email(affiliation.text)
                        if email:
                            return email
        
        # If no corresponding author is marked, look for emails in all affiliations
        for affiliation in article.findall(".//AffiliationInfo/Affiliation"):
            if affiliation.text:
                email = AffiliationDetector.extract_email(affiliation.text)
                if email:
                    return email
                    
        return None
    
    @classmethod
    def parse_article(cls, pmid: str, article: ET.Element) -> Dict[str, Any]:
        """
        Parse an article to extract relevant information.
        
        Args:
            pmid: PubMed ID of the article
            article: XML element representing the article
            
        Returns:
            Dictionary containing extracted information
        """
        title = cls.extract_title(article)
        publication_date = cls.extract_publication_date(article) 
        author_affiliations = cls.extract_author_affiliations(article)
        
        # Filter for non-academic authors (those with company affiliations)
        non_academic_authors = []
        company_affiliations = set()
        
        for name, affiliation, _ in author_affiliations:
            if affiliation and AffiliationDetector.is_company_affiliation(affiliation):
                non_academic_authors.append(name)
                
                # Extract company name from affiliation
                company_name = AffiliationDetector.extract_company_name(affiliation)
                if company_name:
                    company_affiliations.add(company_name)
        
        corresponding_author_email = cls.extract_corresponding_author_email(article) or "Email Not Found"
        
        return {
            "PubmedID": pmid if pmid else "PubMed ID Not Found",
            "Title": title,
            "PublicationDate": publication_date,
            "NonAcademicAuthors": "; ".join(non_academic_authors) if non_academic_authors else "No Non-Academic Authors",
            "CompanyAffiliations": "; ".join(company_affiliations) if company_affiliations else "No Company Affiliations",
            "CorrespondingAuthorEmail": corresponding_author_email
        }

print("PubMed Parser module loaded successfully")
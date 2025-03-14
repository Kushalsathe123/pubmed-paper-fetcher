"""Module for identifying company affiliations in research papers."""

import re
from typing import List, Optional, Set

class AffiliationDetector:
    """Class for detecting and categorizing author affiliations."""
    
    # Keywords that suggest academic affiliations
    ACADEMIC_KEYWORDS: List[str] = [
        "university", "college", "institute", "school", "academy", "hospital",
        "medical center", "clinic", "foundation", "laboratory", "lab", "center for",
        "department of", "faculty", "division of", "national", "federal", "ministry",
        "government", "association", "society", "organization"
    ]
    
    # Keywords that suggest pharmaceutical or biotech companies
    COMPANY_KEYWORDS: List[str] = [
        "pharma", "biotech", "therapeutics", "biosciences", "laboratories", "inc", 
        "corp", "llc", "ltd", "co", "company", "gmbh", "ag", "sa", "bv", "plc",
        "biopharmaceutical", "pharmaceutical", "drug", "medicine", "health"
    ]
    
    @classmethod
    def is_company_affiliation(cls, affiliation: str) -> bool:
        """
        Determine if an affiliation is likely a pharmaceutical or biotech company.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            True if the affiliation appears to be a company, False otherwise
        """
        if not affiliation:
            return False
            
        affiliation_lower = affiliation.lower()
        
        # Check for company keywords
        for keyword in cls.COMPANY_KEYWORDS:
            if keyword in affiliation_lower:
                # Make sure it's not an academic institution with these keywords
                for academic_keyword in cls.ACADEMIC_KEYWORDS:
                    if academic_keyword in affiliation_lower:
                        # If both company and academic keywords are present,
                        # do additional checks to determine the type
                        
                        # If it starts with a company-like name pattern (e.g., "Pfizer, Inc.")
                        if re.search(r'^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,?\s*(?:Inc|Corp|LLC|Ltd|GmbH|AG|SA|BV|PLC)', affiliation):
                            return True
                        
                        # If it contains phrases like "X company" or "X corporation"
                        if re.search(r'(?:company|corporation|inc|corp|llc|ltd)\s*$', affiliation_lower):
                            return True
                            
                        # Default to academic if unclear
                        return False
                
                # No academic keywords found, likely a company
                return True
                
        # Check for company-like patterns in the affiliation
        if re.search(r'(?:Inc|Corp|LLC|Ltd|GmbH|AG|SA|BV|PLC)\.?(?:\s|$)', affiliation):
            return True
            
        return False
    
    @classmethod
    def extract_company_name(cls, affiliation: str) -> Optional[str]:
        """
        Extract company name from an affiliation string.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            Company name if found, None otherwise
        """
        if not affiliation:
            return None
            
        # Try to extract company name using patterns
        company_match = re.search(r'([A-Z][a-zA-Z0-9\s]+(?:Inc|Corp|LLC|Ltd|GmbH|AG|SA|BV|PLC)\.?)', affiliation)
        if company_match:
            return company_match.group(1).strip()
            
        # If no clear company name pattern, use the first part of the affiliation
        # if it's likely a company
        if cls.is_company_affiliation(affiliation):
            parts = affiliation.split(',')
            if parts:
                return parts[0].strip()
                
        return None
    
    @classmethod
    def extract_email(cls, text: str) -> Optional[str]:
        """
        Extract email address from text.
        
        Args:
            text: Text that may contain an email address
            
        Returns:
            Email address if found, None otherwise
        """
        if not text:
            return None
            
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            return email_match.group(0)
            
        return None
    
    @classmethod
    def get_company_affiliations(cls, affiliations: List[str]) -> Set[str]:
        """
        Get unique company names from a list of affiliations.
        
        Args:
            affiliations: List of affiliation strings
            
        Returns:
            Set of unique company names
        """
        companies = set()
        
        for affiliation in affiliations:
            if cls.is_company_affiliation(affiliation):
                company_name = cls.extract_company_name(affiliation)
                if company_name:
                    companies.add(company_name)
                    
        return companies

print("Affiliations module loaded successfully")
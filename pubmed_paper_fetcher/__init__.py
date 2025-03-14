"""PubMed Paper Fetcher - A tool to fetch research papers with company affiliations."""

__version__ = "0.1.0"

from .api import PubMedAPI
from .parser import PubMedParser
from .affiliations import AffiliationDetector

print("PubMed Paper Fetcher package initialized")
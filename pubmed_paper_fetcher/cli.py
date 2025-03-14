"""Command-line interface for the PubMed Paper Fetcher."""

import argparse
import csv
import logging
import sys
from typing import List, Dict, Any, Optional

from .api import PubMedAPI
from .parser import PubMedParser

def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        debug: Whether to enable debug logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers with authors affiliated with pharmaceutical or biotech companies."
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Output file path (CSV). If not provided, results are printed to stdout."
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--email",
        required=True,
        help="Email address (required by NCBI)"
    )
    
    parser.add_argument(
        "--api-key",
        help="NCBI API key for higher rate limits"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to return (default: 100)"
    )
    
    return parser.parse_args()

def filter_company_affiliated_papers(papers: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Filter papers to include only those with at least one author affiliated with a company.
    
    Args:
        papers: Dictionary mapping PubMed IDs to paper details
        
    Returns:
        Filtered dictionary
    """
    return {
        pmid: paper for pmid, paper in papers.items()
        if paper.get("NonAcademicAuthors")
    }

def write_csv(papers: Dict[str, Dict[str, Any]], file_path: Optional[str] = None) -> None:
    """
    Write papers to a CSV file or stdout.
    
    Args:
        papers: Dictionary mapping PubMed IDs to paper details
        file_path: Path to the output CSV file, or None to write to stdout
    """
    fieldnames = [
        "PubmedID",
        "Title",
        "PublicationDate",
        "NonAcademicAuthors",
        "CompanyAffiliations",
        "CorrespondingAuthorEmail"
    ]
    
    if file_path:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for paper in papers.values():
                writer.writerow(paper)
        print(f"Results written to {file_path}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers.values():
            writer.writerow(paper)

def main() -> None:
    """Main entry point for the command-line interface."""
    args = parse_args()
    setup_logging(args.debug)
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Starting search with query: {args.query}")
    
    # Initialize the PubMed API client
    api = PubMedAPI(email=args.email, api_key=args.api_key)
    
    # Search for papers and fetch details
    articles = api.search_and_fetch(args.query, args.max_results)
    
    # Parse articles to extract relevant information
    papers = {}
    for pmid, article in articles.items():
        try:
            paper_info = PubMedParser.parse_article(pmid, article)
            papers[pmid] = paper_info
        except Exception as e:
            logger.error(f"Error parsing article {pmid}: {e}")
    
    # Filter papers to include only those with company affiliations
    filtered_papers = filter_company_affiliated_papers(papers)
    
    logger.info(f"Found {len(filtered_papers)} papers with company affiliations out of {len(papers)} total papers")
    
    # Write results to CSV
    write_csv(filtered_papers, args.file)

if __name__ == "__main__":
    main()

print("CLI module loaded successfully")
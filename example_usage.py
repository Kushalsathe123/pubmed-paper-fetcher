import csv
import logging
from pubmed_paper_fetcher.api import PubMedAPI
from pubmed_paper_fetcher.parser import PubMedParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

EMAIL = "kushalsathe1@gmail.com"

def save_to_csv(papers, filename="output.csv"):
    """Save fetched papers to CSV with sections for complete and incomplete data."""
    fieldnames = ["PubmedID", "Title", "PublicationDate", "NonAcademicAuthors", "CompanyAffiliations", "CorrespondingAuthorEmail"]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Writing section for Complete Data (Only when all required fields are properly filled)
        file.write("\n# Complete Data (All Fields Present)\n")
        for paper in papers["complete"]:
            writer.writerow(paper)

        # Writing section for Incomplete Data (Missing 'NonAcademicAuthors' or 'CompanyAffiliations')
        file.write("\n# Incomplete Data (Missing 'NonAcademicAuthors' or 'CompanyAffiliations')\n")
        for paper in papers["incomplete"]:
            writer.writerow(paper)

    print(f"Results saved to {filename}")

def main():
    """Demonstrate the usage of PubMed Paper Fetcher."""
    api = PubMedAPI(email=EMAIL)
    
    query = "cancer therapy AND 2023[PDAT]"
    print(f"Searching for: {query}")
    
    articles = api.search_and_fetch(query, retmax=10)
    print(f"Found {len(articles)} articles")
    
    papers = {}
    for pmid, article in articles.items():
        paper_info = PubMedParser.parse_article(pmid, article)
        papers[pmid] = paper_info
    
    complete_papers = {}
    incomplete_papers = {}

    for pmid, paper in papers.items():
        # Move to incomplete if either field is missing or set to "No Non-Academic Authors" / "No Company Affiliations"
        if paper.get("NonAcademicAuthors") in [None, "", "No Non-Academic Authors"] or \
           paper.get("CompanyAffiliations") in [None, "", "No Company Affiliations"]:
            incomplete_papers[pmid] = paper
        else:
            complete_papers[pmid] = paper

    print(f"Found {len(complete_papers)} complete papers")
    print(f"Found {len(incomplete_papers)} incomplete papers (Missing 'NonAcademicAuthors' or 'CompanyAffiliations')")

    save_to_csv({"complete": complete_papers.values(), "incomplete": incomplete_papers.values()})  

if __name__ == "__main__":
    main()

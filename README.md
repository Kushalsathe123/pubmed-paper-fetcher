# PubMed Paper Fetcher
🚀 **PubMed Paper Fetcher** is a Python tool that searches PubMed for research papers and extracts information about authors affiliated with **pharmaceutical or biotech companies**.

---

## 📌 Features
- 🔍 **Search PubMed** using complex queries.
- 🏢 **Filter papers with company-affiliated authors**.
- 📄 **Export results to CSV**.
- ⚡ **Command-line Interface (CLI) support**.
- 📦 **Available on [TestPyPI](https://test.pypi.org/project/pubmed-paper-fetcher-kushal/)**.

---

## 🔧 Installation
### **From TestPyPI**
To install the package, run:
```sh
pip install --index-url https://test.pypi.org/simple/ --no-deps pubmed-paper-fetcher-kushal
```

## 🚀 Usage

### Command-Line Interface (CLI)
After installation, you can run the tool from the terminal:
```sh
python -m pubmed_paper_fetcher.cli "cancer therapy" --email "kushalsathe1@gmail.com"
```

### CLI Options:
| Option | Description |
|--------|-------------|
| -h, --help | Show usage instructions |
| -d, --debug | Enable debug logging |
| -f, --file | Save output to a CSV file |
| --email | (Required) Your email for PubMed API |
| --api-key | (Optional) NCBI API key for higher rate limits |

Example to save results to results.csv:
```sh
get-papers-list "cancer therapy" --email "kushalsathe1@gmail.com" -f results.csv
```

### Python Module Usage
You can also use this package in your Python scripts:
```python
from pubmed_paper_fetcher.api import PubMedAPI
from pubmed_paper_fetcher.parser import PubMedParser

email = "kushalsathe1@gmail.com"
api = PubMedAPI(email=email)

# Search and fetch paper details
query = "cancer therapy AND 2023[PDAT]"
articles = api.search_and_fetch(query, retmax=10)

# Parse article data
papers = {pmid: PubMedParser.parse_article(pmid, article) for pmid, article in articles.items()}

# Print first paper details
print(papers[next(iter(papers))])
```

## 🛠 Development Setup

### Clone the Repository
```sh
git clone https://github.com/yourusername/pubmed-paper-fetcher.git
cd pubmed-paper-fetcher
```

### Install Dependencies
```sh
poetry install
```

### Run Tests
```sh
pytest
```

## 🛠 Build & Publish Package

### 1️⃣ Build the Package
```sh
poetry build
```

### 2️⃣ Publish to TestPyPI
First, configure TestPyPI as a repository:
```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

Then, publish your package:
```sh
poetry publish -r testpypi --username **token** --password YOUR_TEST_PYPI_API_TOKEN
```

Your package will be available at:
```
https://test.pypi.org/project/pubmed-paper-fetcher-kushal/
```

## 📜 License
This project is licensed under the MIT License.

## 📞 Contact
If you have any questions, feel free to reach out!


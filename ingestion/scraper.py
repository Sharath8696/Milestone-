import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URLs to scrape as per problem statement and architecture
URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

def clean_html(html_content):
    """Parses HTML and extracts clean text dropping noise."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside"]):
        script_or_style.decompose()
        
    # Get text
    text = soup.get_text(separator=' ')
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def scrape_url(url):
    """Fetches the URL and returns the raw html."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for url in URLS:
        html = scrape_url(url)
        if html:
            text_content = clean_html(html)
            
            # Extract basic title from the url slug
            slug = url.rstrip('/').split('/')[-1]
            
            metadata = {
                "source_url": url,
                "last_updated_date": datetime.utcnow().isoformat(),
                "document_type": "webpage",
                "content_length": len(text_content)
            }
            
            output_data = {
                "metadata": metadata,
                "text": text_content
            }
            
            output_file = os.path.join(DATA_DIR, f"{slug}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
                
            print(f"Saved {output_file}")

if __name__ == "__main__":
    main()

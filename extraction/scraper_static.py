import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Keywords to filter our help center crawl ---
# We are looking for links related to JioPay
RELEVANT_KEYWORDS = ['pay', 'upi', 'payment']

def scrape_and_find_links(base_url, keywords):
    """
    Scrapes a single page and finds all links that match our keywords.
    """
    print(f"Crawling for links on: {base_url}")
    found_urls = set()
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            link_text = a_tag.get_text().lower()
            link_href = a_tag['href']
            
            # Check if any keyword is in the link text or the URL
            if any(keyword in link_text for keyword in keywords) or \
               any(keyword in link_href for keyword in keywords):
                
                # Convert relative URLs (like /help/faq/...) to absolute URLs
                full_url = urljoin(base_url, link_href)
                
                # Check if it's a valid http/https URL
                if urlparse(full_url).scheme in ['http', 'https']:
                    found_urls.add(full_url)
                    
    except requests.exceptions.RequestException as e:
        print(f"Failed to crawl {base_url}: {e}")
        
    return list(found_urls)

def scrape_static_page(url):
    """
    Fetches a single URL with 'requests' and extracts text with 'BeautifulSoup'.
    This is our main scraping function for static content.
    """
    print(f"Scraping (static): {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"Skipped (not HTML): {url}")
            return {'url': url, 'status': 'skipped_not_html'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find specific content tags, fall back to body
        content_tag = soup.find('main')
        if not content_tag:
            content_tag = soup.find('article')
        if not content_tag:
            # For Jio help pages, content is often in a class like 'j-content'
            content_tag = soup.find(class_=re.compile(r'content', re.IGNORECASE))
        if not content_tag:
            content_tag = soup.find('body')
            
        if not content_tag:
            raise Exception("No <body> tag found")

        clean_text = content_tag.get_text(separator=' ', strip=True)
        
        return {
            'url': url,
            'source_type': 'static_scrape',
            'content': clean_text,
            'status': 'success'
        }
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'failed', 'error': str(e)}

def main():
    """
    Main function to orchestrate the targeted scraping.
    """
    # Start the timer for our ablation study
    start_time = time.time()
    
    # --- 1. Define our TARGETED seed URLs ---
    # These are high-quality, known JioPay pages
    jiopay_seed_urls = [
        "https://docs.jiopay.in/docs/payment-gateway",
        "https://docs.jiopay.in/docs/online",
    ]
    
    # This is the page we will crawl to find more links
    help_center_start_url = "https://www.jio.com/help/home/#/"
    
    print("--- Starting Phase 1: Targeted URL Discovery ---")
    
    # --- 2. Crawl the help center for relevant links ---
    # We are only going one level deep
    target_urls = set(jiopay_seed_urls)
    found_help_links = scrape_and_find_links(help_center_start_url, RELEVANT_KEYWORDS)
    
    # Filter out links that are clearly not help pages
    for url in found_help_links:
        if 'help/faq' in url or 'jiopay.in' in url:
             target_urls.add(url)

    target_urls = sorted(list(target_urls))
    
    print(f"\n--- Found {len(target_urls)} relevant URLs to scrape ---")
    for url in target_urls:
        print(url)

    # --- 3. Scrape all relevant static URLs ---
    print("\n--- Starting Phase 2: Static Scraping ---")
    scraped_data = []
    
    for url in target_urls:
        data = scrape_static_page(url)
        if data:
            scraped_data.append(data)
        time.sleep(1) # Be polite!
        
    # --- 4. Save the results ---
    output_filename = "scraped_data_static.json"
    
    successful_scrapes = [d for d in scraped_data if d.get('status') == 'success']
    failed_scrapes = [d for d in scraped_data if d.get('status') != 'success']
    
    with open(output_filename, "w", encoding='utf-8') as f:
        json.dump(successful_scrapes, f, indent=2, ensure_ascii=False)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n--- Static scraping complete ---")
    print(f"Successfully scraped {len(successful_scrapes)} pages.")
    print(f"Failed or skipped {len(failed_scrapes)} pages.")
    print(f"Results saved to {output_filename}")
    
    # --- 5. Ablation Data (Pipeline 1) ---
    print(f"\n--- Ablation Data (Pipeline 1 - Static) ---")
    print(f"Total time taken: {total_time:.2f} seconds")
    if target_urls: # Avoid division by zero
        print(f"Throughput: {len(target_urls) / total_time:.2f} pages/sec")
        print(f"Failure Rate: {len(failed_scrapes) / len(target_urls) * 100:.2f}%")
    
    # Calculate word count and noise
    total_words = 0
    noisy_pages = 0
    for item in successful_scrapes:
        words = len(item['content'].split())
        total_words += words
        if words < 100: # Let's define "noise" as < 100 words
            noisy_pages += 1
            
    print(f"Total Words Scraped: {total_words}")
    if successful_scrapes: # Avoid division by zero
        print(f"Noise % (Pages < 100 words): {noisy_pages / len(successful_scrapes) * 100:.2f}%")

if __name__ == "__main__":
    main()
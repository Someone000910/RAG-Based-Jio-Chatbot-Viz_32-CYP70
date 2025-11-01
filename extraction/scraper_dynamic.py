import requests
from bs4 import BeautifulSoup
import json
import time
import re

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Stealth import
from selenium_stealth import stealth


def scrape_dynamic_url(driver, url):
    """
    Fetches a single URL with Selenium (using stealth), waits for JS to load,
    and extracts text content using BeautifulSoup.
    """
    print(f"Scraping (dynamic-stealth): {url}")
    try:
        driver.get(url)

        # Wait up to 10 seconds for a <main> tag (common in SPAs)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        content_tag = soup.find("main")
        if not content_tag:
            content_tag = soup.find("body")

        if not content_tag:
            raise Exception("No <body> or <main> tag found in the page")

        clean_text = content_tag.get_text(separator=" ", strip=True)

        if len(clean_text) < 200:
            print(f"⚠️  Warning: Very little content found for {url}")

        return {
            "url": url,
            "source_type": "dynamic_scrape",
            "content": clean_text,
            "status": "success",
        }

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return {
            "url": url,
            "source_type": "dynamic_scrape",
            "content": None,
            "status": "failed",
            "error": str(e),
        }


def main():
    """Main function to perform stealth-based dynamic scraping."""
    start_time = time.time()

    print("🚀 Setting up Selenium WebDriver with Stealth...")

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Initialize WebDriver
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
    except Exception as e:
        print(f"❌ Error initializing WebDriver: {e}")
        print("Please ensure Google Chrome is installed correctly.")
        return

    # Apply stealth
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    print("✅ WebDriver initialized with stealth mode enabled.\n")

    # Target URLs (SPA or JS-heavy pages)
    dynamic_urls = [
        "https://www.jiopay.com/business/",
        "https://www.jiopay.com/business/paymentgateway",
        "https://www.jio.com/help/home/#/",
    ]

    print(f"--- Found {len(dynamic_urls)} dynamic URLs to scrape ---\n")

    scraped_data = []

    # Scrape all dynamic URLs
    for url in dynamic_urls:
        data = scrape_dynamic_url(driver, url)
        if data:
            scraped_data.append(data)

    # Separate success and failure results
    successful_scrapes = [d for d in scraped_data if d.get("status") == "success"]
    failed_scrapes = [d for d in scraped_data if d.get("status") != "success"]

    # Save successful results to JSON
    output_filename = "scraped_data_dynamic.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(successful_scrapes, f, indent=2, ensure_ascii=False)

    # Close browser
    driver.quit()

    # --- Summary ---
    end_time = time.time()
    total_time = end_time - start_time

    print("\n--- ✅ Dynamic Scraping Summary ---")
    print(f"Successfully scraped: {len(successful_scrapes)} pages")
    print(f"Failed/skipped: {len(failed_scrapes)} pages")
    print(f"Results saved to: {output_filename}")
    print(f"Total time taken: {total_time:.2f} seconds")

    if dynamic_urls:
        print(f"Throughput: {len(dynamic_urls) / total_time:.2f} pages/sec")
        print(f"Failure Rate: {len(failed_scrapes) / len(dynamic_urls) * 100:.2f}%")

    # --- Word count stats ---
    total_words = 0
    noisy_pages = 0
    for item in successful_scrapes:
        words = len(item.get("content", "").split())
        total_words += words
        if words < 100:
            noisy_pages += 1

    print(f"Total Words Scraped: {total_words}")
    if successful_scrapes:
        print(f"Noise % (Pages < 100 words): {noisy_pages / len(successful_scrapes) * 100:.2f}%")
    print("\n--- 🕵️‍♂️ Dynamic Stealth Scraping Complete ---")


if __name__ == "__main__":
    main()

# Data Card for JioPay RAG Chatbot Knowledge Base

## 1. Data Sources

The knowledge base for this chatbot was constructed *exclusively* from publicly accessible JioPay web pages and documents. No private or user data was accessed. The primary sources include:

* **JioPay Business Website:** `https://www.jiopay.com/business/` and its subpages (e.g., `/paymentgateway`, `/voicebox`, `/about-us`, `/terms-and-condition`, etc.)
* **JioPay Developer Documentation:** `https://docs.jiopay.in/docs/payment-gateway`, `https://docs.jiopay.in/docs/online`
* **Jio Help Center (JioPay Relevant Sections):** Starting from `https://www.jio.com/help/home/` (dynamically loaded content).
* **Publicly Linked Documents:** e.g., `Grievance-Redressal-Policy.pdf` found linked from the main site.

Compliance with `robots.txt` was maintained throughout the automated phases.

## 2. Collection Method (Ingestion Ablation)

A hybrid data collection strategy was employed due to varying website technologies and anti-scraping measures:

1.  **Static Scrape (`requests` + `BeautifulSoup4`):** Used successfully for the static developer documentation pages (`docs.jiopay.in`). Fast and efficient for non-JavaScript content.
2.  **Dynamic Scrape Attempt (`selenium` + `selenium-stealth`):** Attempted for the main `jiopay.com/business` SPA and the `jio.com/help` portal.
    * *Result:* Successfully rendered and scraped the `jio.com/help` homepage. **Failed** on `jiopay.com` domains due to immediate detection and blocking by enterprise-grade anti-bot measures, even with stealth techniques applied.
3.  [cite_start]**Manual Export (Fallback):** Due to the failure of automated scraping on the core business site, we pivoted to manual export as allowed by the assignment[cite: 28].
    * *Method:* Navigated the `jiopay.com` site in a standard browser, waited for full JavaScript rendering, and used Chrome Developer Tools ("Elements" -> Right-click `<html>` -> "Copy outerHTML") to save the fully rendered HTML of each relevant page. Relevant PDF documents were downloaded directly.
    * *Outcome:* This successfully bypassed bot detection and captured the rich content of the SPAs.

The final raw data was collected using a combination of the successful static scrape (2 docs) and manual export (approx. 25 HTML files + 1 PDF).

## 3. Preprocessing & Cleaning

The collected raw data underwent several processing and cleaning steps:

1.  **Initial Parsing (`build_knowledge_base.py`):**
    * HTML files were parsed using `BeautifulSoup4` to extract text content, primarily targeting `<main>` or `<body>` tags.
    * PDF files were processed using `PyMuPDF` (`fitz`) to extract plain text page by page.
    * Metadata (source URL from mapping, page title from `<title>` tag or filename) was associated with the extracted text.
    * This initial extraction resulted in `knowledge_base.json`.

2.  **Boilerplate Removal & Text Cleaning (`clean_json_data.py`):**
    * The `knowledge_base.json` file was processed using a dedicated cleaning script.
    * **Regex-based Cleaning:** Applied a comprehensive set of regular expressions (case-insensitive, multiline) to remove common boilerplate content identified during manual inspection. This included:
        * JavaScript requirement messages ("You need to enable JavaScript...").
        * Navigation menus, headers, and footers (site navigation links, addresses).
        * Common promotional sections ("Why JioPay?", statistics blocks).
        * Contact form elements and disclaimers.
        * Repeated phrases ("Know More", "Explore Products", "| JioPay").
        * Unicode private use area characters.
    * **Whitespace Normalization:** Collapsed excessive newlines, spaces, and tabs into single spaces or appropriate paragraph breaks.
    * **Short/Noisy Content Filtering:** Removed documents where the cleaned content fell below a minimum word count (10 words).
    * **Duplicate Removal:** Calculated MD5 hashes of the cleaned content and removed documents with identical content to previously seen documents.
    * **Title Cleaning:** Basic cleaning applied to source titles.
    * This step produced the final `knowledge_base_cleaned.json` used for chunking and embedding.

## 4. Data Characteristics

* **Final Document Count:** The cleaned knowledge base (`knowledge_base_cleaned.json`) contains **28** documents.
* **Content Types:** The documents cover JioPay product descriptions (Payment Gateway, POS, UPI Hub, VoiceBox, etc.), business features, terms and conditions, privacy policies, grievance redressal policies, KYC policies, developer documentation snippets, and help center information.
* **Language:** English.
* **Format:** JSON list of objects, each with `source_url`, `source_title`, `content`, `local_path` (if applicable), `source_type`, and `status`.

## 5. Ethical Considerations & Limitations

* **Public Data:** Only publicly accessible information was targeted. No login credentials were used, and no private customer data was accessed.
* **`robots.txt`:** The rules specified in `robots.txt` were followed during the automated scraping attempts.
* **Rate Limiting:** A `time.sleep(1)` was included in static scraping loops as a basic politeness measure (though largely unnecessary due to the small number of static targets). Selenium's inherent page load time acted as a natural delay for dynamic attempts.
* **Manual Fallback:** The reliance on manual export for a significant portion of the data means the knowledge base is a snapshot in time and requires manual effort to update. It also highlights the challenges posed by modern web anti-scraping technologies.

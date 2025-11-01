import json
from bs4 import BeautifulSoup
import re
import glob  # New import to find files
import fitz  # New import for PyMuPDF
import os

def load_json_file(filename):
    """Loads a JSON file and returns its content."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"✅ Loaded {filename}")
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: File not found {filename}. Skipping.")
        return []
    except json.JSONDecodeError:
        print(f"⚠️ Error: Could not decode {filename}. Skipping.")
        return []

def parse_local_html(filename):
    """Parses a local HTML file and returns its text content."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to get a clean title, fallback to filename
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            source_title = title_tag.string.strip()
        else:
            source_title = os.path.basename(filename) # Use filename as fallback

        content_tag = soup.find('main')
        if not content_tag:
            content_tag = soup.find('body')
        
        if not content_tag:
            print(f"⚠️ No <body> tag in {filename}, skipping.")
            return None

        clean_text = content_tag.get_text(separator=' ', strip=True)
        
        print(f"  > Processing HTML: {filename} ({len(clean_text.split())} words)")
        
        return {
            'source_path': filename,
            'source_title': source_title,
            'content': clean_text,
            'source_type': 'manual_html_export',
            'status': 'success'
        }
    except Exception as e:
        print(f"❌ Error parsing {filename}: {e}")
        return None

def parse_pdf_file(filename):
    """Parses a local PDF file and returns its text content."""
    try:
        doc = fitz.open(filename)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n" # Get plain text
        doc.close()
        
        print(f"  > Processing PDF: {filename} ({len(full_text.split())} words)")
        
        return {
            'source_path': filename,
            'source_title': os.path.basename(filename), # Use filename
            'content': full_text,
            'source_type': 'manual_pdf_export',
            'status': 'success'
        }
    except Exception as e:
        print(f"❌ Error parsing PDF {filename}: {e}")
        return None

def main():
    print("--- 🚀 Starting Knowledge Base Build ---")
    
    all_documents = []
    
    # This dictionary will hold our report data
    ablation_stats = {
        'static': {'success': 0, 'fail': 0, 'total_words': 0},
        'dynamic': {'success': 0, 'fail': 0, 'total_words': 0},
        'manual': {'success': 0, 'fail': 0, 'total_words': 0}
    }
    
    # --- 1. Process Static Scraper (Pipeline 1) ---
    print("\n--- Processing Pipeline 1: Static (requests) ---")
    static_docs = load_json_file('scraped_data_static.json')
    for doc in static_docs:
        if doc.get('status') == 'success' and doc.get('content'):
            ablation_stats['static']['success'] += 1
            ablation_stats['static']['total_words'] += len(doc['content'].split())
            # Standardize keys
            doc['source_path'] = doc.get('url', 'unknown_static')
            doc['source_title'] = doc.get('url', 'unknown_static')
            all_documents.append(doc)
        else:
            ablation_stats['static']['fail'] += 1
    
    # --- 2. Process Dynamic Scraper (Pipeline 2) ---
    print("\n--- Processing Pipeline 2: Dynamic (selenium) ---")
    dynamic_docs = load_json_file('scraped_data_dynamic.json')
    for doc in dynamic_docs:
        if doc.get('status') == 'success' and doc.get('content'):
            ablation_stats['dynamic']['success'] += 1
            ablation_stats['dynamic']['total_words'] += len(doc['content'].split())
            # Standardize keys
            doc['source_path'] = doc.get('url', 'unknown_dynamic')
            doc['source_title'] = doc.get('url', 'unknown_dynamic')
            all_documents.append(doc)
        else:
            ablation_stats['dynamic']['fail'] += 1
            
    # --- 3. Process Manual Exports (Pipeline 3) ---
    print("\n--- Processing Pipeline 3: Manual Exports ---")
    
    # Find and process all local HTML files
    html_files = glob.glob('*.html')
    print(f"Found {len(html_files)} local HTML files...")
    for html_file in html_files:
        doc = parse_local_html(html_file)
        if doc:
            ablation_stats['manual']['success'] += 1
            ablation_stats['manual']['total_words'] += len(doc['content'].split())
            all_documents.append(doc)
        else:
            ablation_stats['manual']['fail'] += 1
            
    # Find and process all local PDF files
    pdf_files = glob.glob('*.pdf')
    print(f"Found {len(pdf_files)} local PDF files...")
    for pdf_file in pdf_files:
        doc = parse_pdf_file(pdf_file)
        if doc:
            ablation_stats['manual']['success'] += 1
            ablation_stats['manual']['total_words'] += len(doc['content'].split())
            all_documents.append(doc)
        else:
            ablation_stats['manual']['fail'] += 1
        
    # --- 4. Finalize and Save Knowledge Base ---
    print("\n--- Finalizing Knowledge Base ---")
    
    # Final cleanup of any failed/empty items and normalize titles
    final_documents = []
    for doc in all_documents:
        if doc and 'content' in doc and doc.get('content') and len(doc['content'].split()) > 10:
            # Clean up titles
            doc['source_title'] = doc['source_title'].replace('.html', '').replace('_', ' ').replace('-', ' ').strip()
            doc['source_path'] = doc['source_path'].strip()
            final_documents.append(doc)

    output_filename = "knowledge_base.json"
    with open(output_filename, "w", encoding='utf-8') as f:
        json.dump(final_documents, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully built knowledge base with {len(final_documents)} documents.")
    print(f"Final data saved to: {output_filename}")

    # --- 5. Print Ablation Study Report ---
    print("\n\n--- 📊 INGESTION ABLATION STUDY (FOR YOUR REPORT) ---")
    print("------------------------------------------------------------------")
    print(f"{'Pipeline':<20} | {'# Pages (Success)':<17} | {'# Pages (Fail)':<15} | {'Total Words':<12}")
    print("------------------------------------------------------------------")
    
    s = ablation_stats['static']
    print(f"{'1. Static (requests)':<20} | {s['success']:<17} | {s['fail']:<15} | {s['total_words']:<12}")
    
    d = ablation_stats['dynamic']
    print(f"{'2. Dynamic (selenium)':<20} | {d['success']:<17} | {d['fail']:<15} | {d['total_words']:<12}")
    
    m = ablation_stats['manual']
    print(f"{'3. Manual Export':<20} | {m['success']:<17} | {m['fail']:<15} | {m['total_words']:<12}")
    
    print("------------------------------------------------------------------")
    total_success = s['success'] + d['success'] + m['success']
    total_fail = s['fail'] + d['fail'] + m['fail']
    total_words = s['total_words'] + d['total_words'] + m['total_words']
    print(f"{'TOTAL':<20} | {total_success:<17} | {total_fail:<15} | {total_words:<12}")
    print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
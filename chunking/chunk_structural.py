import uuid
import os
from bs4 import BeautifulSoup
import chunk_utils as utils

def chunk_strategy_structural(documents):
    """Splits documents based on HTML structure (headings)."""
    print("\n--- Running Strategy: Structural Chunking ---")
    all_chunks = []
    
    for doc in documents:
        metadata = {
            "source_title": doc['source_title'],
            "source_path": doc['source_url']
        }
        local_path = doc.get('local_path')
        
        if local_path and local_path.endswith('.html'):
            # Construct the full path to the HTML file
            full_html_path = os.path.join(utils.EXTRACTION_DATA_DIR, local_path)
            
            if not os.path.exists(full_html_path):
                print(f"Warning: HTML file {full_html_path} not found. Using fallback.")
            else:
                try:
                    with open(full_html_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                    
                    headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
                    if headings:
                        sections = []
                        for h in headings:
                            content = ""
                            for sibling in h.find_next_siblings():
                                if sibling.name in ['h1', 'h2', 'h3', 'h4']: break
                                content += sibling.get_text(separator=' ', strip=True) + " "
                            section_text = h.get_text(strip=True) + ": " + content
                            sections.append(section_text)
                        
                        if sections:
                            all_chunks.extend(utils.create_chunks_from_text(sections, metadata))
                            continue
                except Exception as e:
                    print(f"Warning: Could not parse HTML for {local_path}: {e}. Using fallback.")
                
        # --- Fallback ---
        text = doc.get('content', '')
        if text:
            chunks_text = utils.recursive_splitter.split_text(text)
            all_chunks.extend(utils.create_chunks_from_text(chunks_text, metadata))

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks
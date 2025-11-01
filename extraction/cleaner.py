import json
import re
import os
import argparse
import hashlib
from urllib.parse import urlparse


def clean_text(text):
    """Removes boilerplate patterns, excessive whitespace, and performs basic text cleaning."""
    if not isinstance(text, str):
        return ""

    original_length = len(text)
    
    # 1. Remove common boilerplate sections (case-insensitive, multiline)
    boilerplate_patterns = [
        # JavaScript requirement message
        re.compile(r"You need to enable JavaScript to run this app\.?", re.IGNORECASE),
        
        # Navigation menus and headers (multiple variations)
        re.compile(r"JioPay Business Products Partner Program Contact Us About Us", re.IGNORECASE),
        re.compile(r"Digital payment acceptance made easy,?\s*by JioPay\.?", re.IGNORECASE),
        
        # Stats block that appears everywhere
        re.compile(r"2\s*Million\+\s*API requests per day\s+100K\+\s*Merchants trust us\s+300\s*Million\+\s*Transactions processed\s+100\+\s*Payment methods supported", re.IGNORECASE | re.DOTALL),
        re.compile(r"300\s*Million\+\s*Transactions processed\s+100K\+\s*Unique merchants\s+7\s*Million\+\s*Cards tokenized", re.IGNORECASE | re.DOTALL),
        
        # Product menu section
        re.compile(r"Our Products\s+Our platform with its suite.*?be it on websites or in-store\.?", re.IGNORECASE | re.DOTALL),
        re.compile(r"PAYMENT GATEWAY\s+POINT OF SALE\s+UPI HUB\s+BILLER CENTER\s+BUSINESS APP", re.IGNORECASE),
        
        # Contact form fields (very common)
        re.compile(r"(?:Want to better your checkout experience\?\s*)?Contact Us\.?\s*First Name\s+Last Name\s+Work Email Address\s+Mobile Number\s+Company Website\s+Daily\s*Transaction\s*Value in INR\s+Contact JioPay", re.IGNORECASE | re.DOTALL),
        re.compile(r"By completing this form,?\s*I have read and acknowledged the Privacy Policy and agree that JioPay may contact me at the email address or phone number above", re.IGNORECASE),
        
        # Footer addresses (appears multiple times)
        re.compile(r"JioPay Business\s+Jio Payment Solutions Limited\s*\(formerly known as Reliance Payment Solutions Limited\)\s*Registered Address\s*:.*?400\s*710,?\s*India", re.IGNORECASE | re.DOTALL),
        
        # Footer navigation links
        re.compile(r"General\s+About Us\s+Help Center\s+Investor Relations\s+Complaint Resolution\s+JioPay Business Partner Program", re.IGNORECASE),
        re.compile(r"Products\s+JioPay for Business\s+Payment Gateway\s+Point of Sale\s+UPI Hub\s+Biller Centre\s+JioPay Business App", re.IGNORECASE),
        re.compile(r"Legal\s+Privacy Policy\s+Terms & Conditions\s+Grievance Redressal Policy\s+Merchant Onboarding & KYC-AML Policy\s+BillPay Terms & Conditions", re.IGNORECASE),
        
        # Sign In links
        re.compile(r"Sign In\s+(?=PAYMENT|POINT|UPI|BILLER|Get|Offer|Tokenize|Control|Automate|Run|Operate|Multiply)", re.IGNORECASE),
        
        # "Why JioPay" section
        re.compile(r"Why JioPay\?\s+We are obsessed with technology.*?superior success rates and uptime", re.IGNORECASE | re.DOTALL),
        
        # "Know More" links scattered everywhere
        re.compile(r"\s+Know More\s+", re.IGNORECASE),
        
        # Repeated "Start accepting UPI payments" message
        re.compile(r"JioPay Business App\s+Start accepting UPI payments from your customers instantly irrespective of which UPI app they use\.?", re.IGNORECASE),
        
        # Unicode private use area characters
        re.compile(r'[\ue000-\uf8ff]+'),
    ]
    
    for pattern in boilerplate_patterns:
        text = pattern.sub(' ', text)
    
    # 2. Remove specific repetitive phrases
    repetitive_phrases = [
        '| JioPay',
        'JioPay |',
        'Explore Products',
        'Want to better your checkout experience?',
        'Contact JioPay',
    ]
    for phrase in repetitive_phrases:
        text = text.replace(phrase, ' ')
    
    # 3. Remove excessive newlines and whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\t+', ' ', text)  # Tabs to space
    
    # 4. Remove lines that are just navigation/menu items (short lines with only caps/spaces)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip very short lines that are likely menu items
        if len(line) < 15 and line.isupper():
            continue
        # Skip empty lines
        if not line:
            continue
        cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # 5. Final cleanup
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Normalize all whitespace to single spaces
    
    # Debug: Show reduction
    new_length = len(text)
    if original_length > 0:
        reduction = ((original_length - new_length) / original_length) * 100
        if reduction > 50:  # Only log significant reductions
            print(f"    Reduced content by {reduction:.1f}% ({original_length} → {new_length} chars)")
    
    return text.strip()


def clean_json_data(input_filename="knowledge_base.json",
                    output_filename="knowledge_base_cleaned.json",
                    min_word_count=10):
    """Loads a JSON file, cleans the 'content' field, and saves to a new file."""
    print(f"--- 🧹 Starting JSON Cleaning Process ---")
    print(f"Input file: {input_filename}")
    print(f"Output file: {output_filename}")
    print(f"Minimum word count: {min_word_count}")

    # Load the JSON data
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"❌ Error: Input file '{input_filename}' does not contain a JSON list.")
                return
            print(f"✅ Successfully loaded {len(data)} documents from {input_filename}")
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{input_filename}'. Is it valid JSON?")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred loading '{input_filename}': {e}")
        return

    # Process and clean each document
    cleaned_data = []
    seen_content_hashes = set()
    cleaned_count = 0
    filtered_count = 0
    duplicate_count = 0

    print(f"\n--- Cleaning individual documents ---")
    for index, doc in enumerate(data):
        if not isinstance(doc, dict):
            print(f"  ⚠️ Skipping item at index {index}: Not a dictionary.")
            filtered_count += 1
            continue

        original_content = doc.get('content')
        source_url = doc.get('source_url', doc.get('url', f'Unknown URL - Index {index}'))
        source_title = doc.get('source_title', doc.get('title', ''))

        if not original_content:
            print(f"  ⚠️ Skipping doc '{source_url}': Missing 'content' field.")
            filtered_count += 1
            continue

        print(f"  Processing: {source_url}")
        
        # Clean the content
        cleaned_content = clean_text(original_content)

        # Clean the title (simpler cleaning for titles)
        if source_title:
            cleaned_title = re.sub(r'\s+', ' ', source_title).strip()
            cleaned_title = cleaned_title.replace('| JioPay', '').replace('JioPay |', '').strip()
        else:
            cleaned_title = os.path.basename(urlparse(source_url).path)
            if not cleaned_title:
                cleaned_title = f"Document {index}"

        # Check minimum word count
        word_count = len(cleaned_content.split())
        if word_count < min_word_count:
            print(f"  ⚠️ Filtering doc '{source_url}': Content too short after cleaning ({word_count} words).")
            filtered_count += 1
            continue

        # Check for duplicates based on cleaned content
        content_hash = hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()
        if content_hash in seen_content_hashes:
            print(f"  ⚠️ Skipping duplicate content from: {source_url}")
            duplicate_count += 1
            continue
        seen_content_hashes.add(content_hash)

        # Create a cleaned document
        cleaned_doc = {
            'source_url': source_url,
            'source_title': cleaned_title,
            'content': cleaned_content,
            **{k: v for k, v in doc.items() if k not in ['content', 'source_url', 'url', 'source_title', 'title']}
        }

        cleaned_data.append(cleaned_doc)
        cleaned_count += 1
        
        if (index + 1) % 10 == 0:
            print(f"  Progress: {index+1}/{len(data)} documents...")

    print(f"\n--- ✨ Cleaning Summary ---")
    print(f"Documents Processed: {len(data)}")
    print(f"Documents Cleaned & Kept: {cleaned_count}")
    print(f"Documents Filtered (Missing content/Too short): {filtered_count}")
    print(f"Duplicate Content Skipped: {duplicate_count}")

    # Save the cleaned data
    try:
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_filename, "w", encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Successfully saved cleaned data ({len(cleaned_data)} documents) to: {output_filename}")
    except Exception as e:
        print(f"❌ Error saving cleaned JSON to '{output_filename}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean the 'content' field in a JSON knowledge base file by removing boilerplate text.")
    parser.add_argument(
        "-i", "--input",
        default="knowledge_base.json",
        help="Path to the input JSON file (default: knowledge_base.json)"
    )
    parser.add_argument(
        "-o", "--output",
        default="knowledge_base_cleaned.json",
        help="Path to save the cleaned output JSON file (default: knowledge_base_cleaned.json)"
    )
    parser.add_argument(
        "-m", "--minwords",
        type=int,
        default=10,
        help="Minimum number of words required for content to be kept after cleaning (default: 10)"
    )

    args = parser.parse_args()
    clean_json_data(args.input, args.output, args.minwords)
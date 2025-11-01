import os
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
import chunk_utils as utils
import time

# --- LLM-Based Chunking Configuration ---
PRE_CHUNK_SIZE = 4096 
LLM_CHUNK_DELIMITER = "||CHUNK_BREAK||"

# --- Setup LLM Client ---
load_dotenv() # Loads your .env file
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    # Use a fast, modern model
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Google Gemini client initialized successfully.")
except Exception as e:
    print(f"Error initializing Google Gemini client: {e}")
    print("Please make sure your GOOGLE_API_KEY is set in a .env file.")
    model = None

# This is the prompt we will send to Gemini
LLM_SYSTEM_PROMPT = f"""
You are an expert text processing assistant. Your task is to read the following text document and split it into logical,
self-contained chunks. Each chunk should cover a single, specific topic (e.g., a specific feature, a policy section, an API endpoint).

- Aim for chunks between 200 and 500 tokens.
- **DO NOT** lose any text. Every part of the original text must be in one of the chunks.
- Respond *ONLY* with the text of the chunks, separated by the delimiter: {LLM_CHUNK_DELIMITER}
- Do not add any preamble, explanation, or commentary.
"""

# We must add safety settings to allow it to process the text
safety_settings = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
}

def chunk_document_with_llm(doc_content):
    """
    Takes a single document's text, pre-chunks it, and uses Gemini to chunk it.
    """
    if not model:
        print("LLM client not available. Skipping.")
        return []

    pre_splitter = utils.RecursiveCharacterTextSplitter(
        chunk_size=PRE_CHUNK_SIZE,
        chunk_overlap=200,
        length_function=utils.count_tokens
    )
    pre_chunks = pre_splitter.split_text(doc_content)
    
    print(f"  > Document split into {len(pre_chunks)} pre-chunks for LLM.")
    
    final_chunks = []
    
    for i, pre_chunk in enumerate(pre_chunks):
        print(f"    > Sending pre-chunk {i+1}/{len(pre_chunks)} to LLM...")
        try:
            # Combine the system prompt and the user's text
            full_prompt = f"{LLM_SYSTEM_PROMPT}\n\n--- DOCUMENT TEXT ---\n\n{pre_chunk}"
            
            response = model.generate_content(
                full_prompt,
                safety_settings=safety_settings
            )
            
            llm_response_text = response.text
            
            # Split the LLM's response by our delimiter
            llm_chunks = llm_response_text.split(LLM_CHUNK_DELIMITER)
            
            for chunk_text in llm_chunks:
                chunk_text = chunk_text.strip()
                if len(chunk_text.split()) > 5:
                    final_chunks.append(chunk_text)
            
            # The free tier has a rate limit (e.g., 60 requests/min)
            # A small sleep avoids hitting it.
            time.sleep(1) 
                    
        except Exception as e:
            print(f"    > Error processing pre-chunk {i+1}: {e}")
            # Fallback: If LLM fails, just use the pre-chunk
            final_chunks.append(pre_chunk)
            
    return final_chunks

def chunk_strategy_llm(documents):
    """
    Splits documents using an LLM with a specific prompt.
    """
    print("\n--- Running Strategy: LLM-Based Chunking (Gemini) ---")
    all_chunks = []
    
    for doc in documents:
        if not doc.get('content'): continue
        print(f"Processing document: {doc['source_title']}")
        
        metadata = {
            "source_title": doc['source_title'],
            "source_path": doc['source_url']
        }
        
        llm_chunk_texts = chunk_document_with_llm(doc['content'])
        
        all_chunks.extend(utils.create_chunks_from_text(llm_chunk_texts, metadata))
            
    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks
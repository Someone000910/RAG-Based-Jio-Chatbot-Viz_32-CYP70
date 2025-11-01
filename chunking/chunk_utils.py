import json
import tiktoken
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import numpy as np

# --- Configuration ---
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# --- Path Configuration (Robust) ---
# Get the directory where this script is located (chunking/)
SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR == "":
    SCRIPT_DIR = "."
# Set the path to the data *relative* to this script (../extraction/data/)
EXTRACTION_DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'extraction', 'data')
# Set the path to our knowledge base
KNOWLEDGE_BASE_PATH = os.path.join(EXTRACTION_DATA_DIR, 'knowledge_base.json')
# Set the directory to save our new chunk files (chunking/)
CHUNK_OUTPUT_DIR = SCRIPT_DIR

# --- Models & Splitters (Load once) ---
print("Loading shared models and splitters...")
try:
    SEMANTIC_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer model. Semantic chunking will fail. Error: {e}")
    SEMANTIC_MODEL = None

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=lambda text: count_tokens(text),
    separators=["\n\n", "\n", ". ", " ", ""]
)
sentence_splitter = RecursiveCharacterTextSplitter(
    chunk_size=128, 
    chunk_overlap=0,
    length_function=lambda text: count_tokens(text),
    separators=["\n\n", "\n", ". ", "? ", "! ", "。"]
)
print("Models loaded.")

# --- Helper Functions ---

def load_documents(filename=KNOWLEDGE_BASE_PATH):
    """Loads the combined knowledge base from the extraction/data directory."""
    print(f"Loading knowledge base from {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        print(f"Loaded {len(documents)} documents.")
        return documents
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def create_chunks_from_text(text_list, metadata, token_limit=CHUNK_SIZE):
    """Creates chunks from text, applying recursive fallback if needed."""
    all_chunks = []
    for text in text_list:
        token_count = count_tokens(text)
        
        if token_count > token_limit:
            sub_chunks = recursive_splitter.split_text(text)
            for sub_text in sub_chunks:
                all_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "content": sub_text,
                    "metadata": metadata,
                    "token_count": count_tokens(sub_text)
                })
        elif token_count > 10: # Ignore tiny chunks
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": text,
                "metadata": metadata,
                "token_count": token_count
            })
    return all_chunks

def save_chunks(chunks, filename):
    """Saves the list of chunks to the chunking output directory."""
    filepath = os.path.join(CHUNK_OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(chunks)} chunks to {filepath}")
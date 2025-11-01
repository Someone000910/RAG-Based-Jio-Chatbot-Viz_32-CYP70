import json
import os
import faiss
import numpy as np
import sys
import argparse
from sentence_transformers import SentenceTransformer
# We no longer need OpenAI or dotenv
# from openai import OpenAI
# from dotenv import load_dotenv

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR == "":
    SCRIPT_DIR = "."
CHUNK_DIR = os.path.join(SCRIPT_DIR, '..', 'chunking')
INDEX_DIR = SCRIPT_DIR

# --- Load Models (Load once) ---
print("Loading embedding models (this may take a moment)...")
models = {
    "bge": SentenceTransformer('BAAI/bge-small-en-v1.5'),
    "minilm": SentenceTransformer('all-MiniLM-L6-v2'),
    "e5": SentenceTransformer('intfloat/e5-large-v2') # <-- OUR NEW MODEL
}
print("All models loaded.")

def get_local_embeddings(texts, model_name):
    """Gets embeddings from a local SentenceTransformer model."""
    model = models.get(model_name)
    if not model:
        raise ValueError(f"Unknown local model: {model_name}")
    
    # Batch processing is much faster
    print(f"Generating embeddings with '{model_name}'...")
    return model.encode(texts, show_progress_bar=True)

def main(chunk_file, model_name):
    """
    Main function to load chunks, create embeddings, and build a FAISS index.
    """
    
    # 1. Load Chunks
    chunk_filepath = os.path.join(CHUNK_DIR, chunk_file)
    try:
        with open(chunk_filepath, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"Loaded {len(chunks)} chunks from {chunk_file}")
    except FileNotFoundError:
        print(f"Error: Chunk file not found at {chunk_filepath}")
        return

    # 2. Get all chunk content
    texts = [chunk['content'] for chunk in chunks]
    
    # 3. Generate Embeddings
    all_embeddings = []
    
    if model_name in models:
        all_embeddings = get_local_embeddings(texts, model_name)
    else:
        print(f"Error: Unknown model '{model_name}'. Choose from: 'bge', 'minilm', 'e5'.")
        return

    # 4. Build FAISS Index
    print("Building FAISS index...")
    embeddings_np = np.array(all_embeddings).astype('float32')
    d = embeddings_np.shape[1]
    
    index = faiss.IndexFlatL2(d)
    index.add(embeddings_np)
    print(f"FAISS index built with {index.ntotal} vectors of dimension {d}.")

    # 5. Create the Metadata Map
    metadata_map = []
    for i, chunk in enumerate(chunks):
        metadata_map.append({
            "chunk_id": chunk['chunk_id'],
            "content": chunk['content'],
            "metadata": chunk['metadata']
        })

    # 6. Save Files
    base_name = chunk_file.replace('.json', '') + f"_{model_name}"
    index_filename = os.path.join(INDEX_DIR, f"{base_name}.faiss")
    map_filename = os.path.join(INDEX_DIR, f"{base_name}.json")
    
    faiss.write_index(index, index_filename)
    with open(map_filename, 'w', encoding='utf-8') as f:
        json.dump(metadata_map, f, indent=2)
        
    print(f"\n--- Embedding Complete ---")
    print(f"Saved FAISS index to: {index_filename}")
    print(f"Saved metadata map to: {map_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create embeddings and FAISS index for chunks.")
    
    parser.add_argument(
        'chunk_file', 
        type=str, 
        help="The chunk file to process (e.g., 'chunks_recursive.json')"
    )
    # Updated the choices to our three free models
    parser.add_argument(
        'model_name', 
        type=str, 
        choices=['bge', 'minilm', 'e5'], 
        help="The embedding model to use: 'bge', 'minilm', or 'e5'"
    )
    
    args = parser.parse_args()
    main(args.chunk_file, args.model_name)
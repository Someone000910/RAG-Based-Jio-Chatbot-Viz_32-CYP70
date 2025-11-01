import tiktoken
import uuid
import chunk_utils as utils # Import our shared utils

def chunk_strategy_fixed(documents):
    """Splits documents using a simple fixed-size window."""
    print("\n--- Running Strategy: Fixed Chunking ---")
    all_chunks = []
    encoding = tiktoken.get_encoding("cl100k_base")
    
    for doc in documents:
        if not doc.get('content'): continue
        text = doc['content']
        metadata = {"source_title": doc['source_title'], "source_path": doc['source_url']}
        tokens = encoding.encode(text)
        
        start_idx = 0
        while start_idx < len(tokens):
            end_idx = start_idx + utils.CHUNK_SIZE
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = encoding.decode(chunk_tokens)
            
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": chunk_text,
                "metadata": metadata,
                "token_count": len(chunk_tokens)
            })
            start_idx += (utils.CHUNK_SIZE - utils.CHUNK_OVERLAP)
            
    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks
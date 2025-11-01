import uuid
import chunk_utils as utils

def chunk_strategy_recursive(documents):
    """Splits documents using RecursiveCharacterTextSplitter."""
    print("\n--- Running Strategy: Recursive Chunking ---")
    all_chunks = []
    for doc in documents:
        if not doc.get('content'): continue
        metadata = {"source_title": doc['source_title'], "source_path": doc['source_url']}
        text = doc['content']
        
        # Use the splitter from utils
        chunks_text = utils.recursive_splitter.split_text(text)
        
        # Use the chunk creator from utils
        all_chunks.extend(utils.create_chunks_from_text(chunks_text, metadata))
            
    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks
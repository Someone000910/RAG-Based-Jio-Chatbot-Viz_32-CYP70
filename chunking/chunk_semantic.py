import uuid
import numpy as np
import chunk_utils as utils

def chunk_strategy_semantic(documents, similarity_threshold=0.75):
    """Splits by sentences, then merges semantically similar sentences."""
    print("\n--- Running Strategy: Semantic Chunking ---")
    if utils.SEMANTIC_MODEL is None:
        print("Error: SentenceTransformer model not loaded. Skipping semantic chunking.")
        return []
        
    all_chunks = []
    for doc in documents:
        if not doc.get('content'): continue
        metadata = {"source_title": doc['source_title'], "source_path": doc['source_url']}
        
        sentences = utils.sentence_splitter.split_text(doc['content'])
        if not sentences: continue
            
        embeddings = utils.SEMANTIC_MODEL.encode(sentences)
        
        current_chunk_sentences = []
        for i, sentence in enumerate(sentences):
            if not current_chunk_sentences:
                current_chunk_sentences.append(sentence)
                continue
            
            last_embedding = embeddings[i-1]
            current_embedding = embeddings[i]
            similarity = np.dot(last_embedding, current_embedding)
            
            current_chunk_text = " ".join(current_chunk_sentences)
            token_count = utils.count_tokens(current_chunk_text)
            
            if similarity > similarity_threshold and token_count < (utils.CHUNK_SIZE - 50):
                current_chunk_sentences.append(sentence)
            else:
                all_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "content": " ".join(current_chunk_sentences),
                    "metadata": metadata,
                    "token_count": token_count
                })
                current_chunk_sentences = [sentence]

        if current_chunk_sentences:
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": " ".join(current_chunk_sentences),
                "metadata": metadata,
                "token_count": utils.count_tokens(" ".join(current_chunk_sentences))
            })
            
    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks
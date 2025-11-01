import chunk_utils as utils
from chunk_fixed import chunk_strategy_fixed
from chunk_recursive import chunk_strategy_recursive
from chunk_structural import chunk_strategy_structural
from chunk_semantic import chunk_strategy_semantic
from chunk_llm import chunk_strategy_llm # <-- NEW IMPORT

def main():
    # 1. Load our master document list
    documents = utils.load_documents()
    
    if not documents:
        print("No documents found. Exiting.")
        return
        
    # --- Run and save Strategy 1 ---
    chunks_fixed = chunk_strategy_fixed(documents)
    utils.save_chunks(chunks_fixed, "chunks_fixed.json")
    
    # --- Run and save Strategy 2 ---
    chunks_recursive = chunk_strategy_recursive(documents)
    utils.save_chunks(chunks_recursive, "chunks_recursive.json")
    
    # --- Run and save Strategy 3 ---
    chunks_structural = chunk_strategy_structural(documents)
    utils.save_chunks(chunks_structural, "chunks_structural.json")
    
    # --- Run and save Strategy 4 ---
    chunks_semantic = chunk_strategy_semantic(documents)
    utils.save_chunks(chunks_semantic, "chunks_semantic.json")
    
    # --- Run and save Strategy 5 ---
    chunks_llm = chunk_strategy_llm(documents) 
    utils.save_chunks(chunks_llm, "chunks_llm.json") 
    
    print("\n--- Phase 2 Complete ---")
    print(f"Created chunks_fixed.json")
    print(f"Created chunks_recursive.json")
    print(f"Created chunks_structural.json")
    print(f"Created chunks_semantic.json")
    print(f"Created chunks_llm.json") 

if __name__ == "__main__":
    main()
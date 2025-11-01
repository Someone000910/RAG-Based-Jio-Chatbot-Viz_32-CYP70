import subprocess
import os
import sys

# --- Configuration ---
MODEL_NAME = "e5" # Model for this script
CHUNK_STRATEGIES = ["fixed", "recursive", "structural", "semantic", "llm"]

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR == "": SCRIPT_DIR = "."
EMBEDDER_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "embedder.py")
CHUNK_DIR = os.path.join(SCRIPT_DIR, '..', 'chunking')

# --- run_embedding_process function (Identical to BGE script) ---
def run_embedding_process(chunk_strategy, model_name):
    """Calls embedder.py with the specified arguments."""
    chunk_file_name = f"chunks_{chunk_strategy}.json"
    chunk_file_path = os.path.join(CHUNK_DIR, chunk_file_name)

    if not os.path.exists(chunk_file_path):
        print(f"--- Skipping: Chunk file not found: {chunk_file_path}")
        return False

    print(f"\n--- Generating {model_name.upper()} Embeddings: Strategy='{chunk_strategy}' ---")
    print(f"Using chunk file: {chunk_file_path}")

    command = [sys.executable, EMBEDDER_SCRIPT_PATH, chunk_file_name, model_name]

    try:
        subprocess.run(command, check=True, text=True, cwd=SCRIPT_DIR)
        print(f"--- Successfully completed: Strategy='{chunk_strategy}', Model='{model_name}' ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- FAILED: Strategy='{chunk_strategy}', Model='{model_name}' ---")
        print(f"Error output:\n{e}")
        return False
    except FileNotFoundError:
        print(f"Error: Could not find Python interpreter '{sys.executable}' or script '{EMBEDDER_SCRIPT_PATH}'")
        return False

# --- main function (Identical logic, uses MODEL_NAME) ---
def main():
    print(f"--- Starting Generation of {MODEL_NAME.upper()} Embedding Combinations ---")
    success_count = 0
    fail_count = 0

    for strategy in CHUNK_STRATEGIES:
        base_name = f"chunks_{strategy}_{MODEL_NAME}"
        index_filename = os.path.join(SCRIPT_DIR, f"{base_name}.faiss")
        map_filename = os.path.join(SCRIPT_DIR, f"{base_name}.json")

        if os.path.exists(index_filename) and os.path.exists(map_filename):
            print(f"--- Skipping: Output files already exist for Strategy='{strategy}', Model='{MODEL_NAME}' ---")
            success_count += 1
            continue

        if run_embedding_process(strategy, MODEL_NAME):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n--- {MODEL_NAME.upper()} Embedding Generation Summary ---")
    print(f"Total combinations attempted: {len(CHUNK_STRATEGIES)}")
    print(f"Successful (or existing): {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    main()
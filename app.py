# app.py
import streamlit as st
import time
import os
import faiss
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import json
from typing import Any, Dict, List, Optional, Tuple, Union

# --- Page Configuration ---
st.set_page_config(
    page_title="JioPay Concierge AI",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Luxury Concierge Dashboard Theme (Black/Gold/Jewel) ---
st.markdown("""
<style>
/* ----------------------------------------------------
   LUXURY CONCIERGE THEME — Black / Gold / Teal / Red
   ---------------------------------------------------- */

/* --- Color Palette --- */
:root {
    --black: #000000;
    --dark-carbon: #151515;
    --teal-aqua: #00E5FF;
    --gold: #D4AF37;
    --peacock-blue: #009688;
    --dark-red: #A00000;
    --dark-orange: #CC5500;
    --silver-text: #F5F5F5;
    --input-field: #1A1A1A;
    --muted: #9E9E9E;
}

/* --- Global Background & Font --- */
html, body, [class*="css"] {
    background-color: var(--black) !important;
    color: var(--silver-text) !important;
    font-family: 'Poppins', Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* --- App Container --- */
.stApp {
    background-color: var(--black);
    color: var(--silver-text);
}

/* --- Concierge Banner --- */
.main-header {
    background: linear-gradient(90deg, var(--dark-red) 0%, var(--dark-carbon) 100%);
    padding: 2rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.75rem;
    border-left: 8px solid var(--gold);
    box-shadow: 0 6px 22px rgba(0,0,0,0.85);
}
.main-header h1 {
    color: var(--gold) !important;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: 1.6px;
    text-shadow: 0 2px 8px rgba(212,175,55,0.3);
}
.main-header p {
    color: var(--silver-text);
    margin: 0.5rem 0 0;
    font-size: 1rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"] {
    background-color: var(--dark-carbon) !important;
    border-right: 3px solid var(--peacock-blue);
    padding-top: 1.6rem;
}
section[data-testid="stSidebar"] * {
    color: var(--silver-text) !important;
}
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] h4, 
section[data-testid="stSidebar"] label {
    color: var(--gold) !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* --- Dropdowns (Selectbox) --- */
div[data-baseweb="select"] > div {
    background-color: var(--input-field) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid var(--gold) !important;
}
ul[data-baseweb="menu"] {
    background-color: var(--dark-carbon) !important;
}
li[data-baseweb="option"] {
    color: #ffffff !important;
}
li[data-baseweb="option"]:hover {
    background-color: #333 !important;
}

/* --- Status Badges --- */
.status-badge {
    background-color: var(--input-field);
    color: var(--teal-aqua);
    border: 2px solid var(--peacock-blue);
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    font-weight: 700;
    font-family: monospace;
    text-transform: uppercase;
    font-size: 0.82rem;
}
.status-active {
    background-color: #004d40 !important;
    color: var(--gold) !important;
    border: 2px solid var(--peacock-blue) !important;
    animation: glow-active 1.6s infinite alternate;
}
@keyframes glow-active {
    from { box-shadow: 0 0 6px rgba(0,150,136,0.6); }
    to { box-shadow: 0 0 14px rgba(0,150,136,0.9), 0 0 20px rgba(0,150,136,0.3); }
}

/* --- Chat Messages --- */
.stChatMessage {
    border-radius: 10px !important;
    padding: 0.9rem !important;
    margin: 0.4rem 0 !important;
}

/* Assistant message */
.stChatMessage[data-testid="stChatMessage"][role="assistant"] {
    background: linear-gradient(90deg, #1c1c1c 0%, #2a2a2a 100%) !important;
    border-left: 4px solid var(--gold);
    color: #f5f0d0 !important;
}
.stChatMessage[data-testid="stChatMessage"][role="assistant"] * {
    color: #f5f0d0 !important;
}

/* User message */
.stChatMessage[data-testid="stChatMessage"][role="user"] {
    background-color: #111 !important;
    border-right: 4px solid var(--dark-orange);
    color: #ffffff !important;
}
.stChatMessage[data-testid="stChatMessage"][role="user"] * {
    color: #ffffff !important;
}

/* Chat message text globally */
[data-testid="stChatMessageContent"] {
    color: #f5f0d0 !important;
    font-size: 1.05rem;
    line-height: 1.6;
}

/* --- Input Box --- */
textarea, input[type="text"] {
    background-color: #111 !important;
    color: #ffffff !important;
    border: 1px solid var(--gold) !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

/* --- Buttons --- */
button[kind="secondary"], button[kind="primary"], .stButton > button {
    background: linear-gradient(90deg, #d4af37, #ffd700) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.6) !important;
}
button[kind="secondary"]:hover, button[kind="primary"]:hover, .stButton > button:hover {
    background: var(--dark-orange) !important;
    color: var(--silver-text) !important;
    transform: translateY(-2px);
}

/* --- Expanders --- */
.streamlit-expanderHeader {
    background: var(--input-field);
    color: var(--silver-text) !important;
    border-left: 3px solid var(--dark-orange);
    border-radius: 6px;
}
.streamlit-expanderContent {
    background: #181818;
}

/* --- Metrics --- */
[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-size: 1.6rem;
    font-weight: 700;
}
[data-testid="stMetricLabel"] {
    color: var(--peacock-blue) !important;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 1px;
}

/* --- Markdown Text --- */
div[data-testid="stMarkdownContainer"] p {
    color: #f5f0d0 !important;
}

/* --- Footer --- */
.footer {
    color: rgba(245,245,245,0.6);
    text-align: center;
    padding-top: 18px;
}

/* --- Mobile Adjustments --- */
@media (max-width: 768px) {
    .main-header h1 { font-size: 1.6rem; }
    .main-header { padding: 1rem; }
}

</style>
""", unsafe_allow_html=True)


# --- Path Setup ---
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
EMBEDDING_DIR = os.path.join(SCRIPT_DIR, "embeddings")
CHUNK_DIR = os.path.join(SCRIPT_DIR, "chunking")

# --- Constants ---
CHUNK_STRATEGIES = ["fixed", "recursive", "structural", "semantic", "llm"]
EMBEDDING_MODELS = ["bge", "minilm", "e5"]
TOP_K = 3

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://th.bing.com/th/id/OIP.Ka-7EGb_xqkA9oW2A0eSlwHaE7?w=270&h=180&c=7&r=0&o=7&dpr=1.5&pid=1.7&rm=3")
    st.markdown("### ⚙️ Ablation Configuration")
    st.markdown("---")

    st.markdown("#### 📜 Chunking Strategy")
    selected_chunk_strategy = st.selectbox(
        "Select chunking method",
        options=CHUNK_STRATEGIES,
        index=CHUNK_STRATEGIES.index("recursive"),
        key="chunk_select",
        help="Choose how documents are split into chunks"
    )

    st.markdown("#### 🔱 Embedding Model")
    selected_embedding_model = st.selectbox(
        "Select embedding model",
        options=EMBEDDING_MODELS,
        index=EMBEDDING_MODELS.index("bge"),
        key="embed_select",
        help="Choose the model for generating embeddings"
    )

    st.markdown("---")
    st.markdown("### 👑 Active RAG Stack")
    model_info = {
        "bge": "BAAI BGE Small (High-Accuracy)",
        "minilm": "MiniLM L6 v2 (High-Speed)",
        "e5": "E5 Large v2 (High-Capacity)"
    }
    st.info(f"**Chunking**: {selected_chunk_strategy.title()}\n\n**Embeddings**: {model_info.get(selected_embedding_model, 'Unknown')}")

    st.markdown("---")
    st.markdown("### 📈 Session Ledger")
    if "messages" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Exchanges", len(st.session_state.messages))
        with col2:
            queries = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("Inquiries", queries)
    else:
        st.caption("No session yet. Start a conversation to populate metrics.")

    st.markdown("---")
    if st.button("⚜️ Reset Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_config = ""
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("### ℹ️ Protocol Details")
    st.markdown(
        """
This system is powered by an **Advanced RAG architecture**. It exclusively utilizes **JioPay's public documentation** to ensure factual integrity and source traceability.
"""
    )

# --- Load API Key for Gemini ---
load_dotenv()
try:
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not google_api_key:
        raise ValueError("API Key not found in environment or .env")

    genai.configure(api_key=google_api_key)

    generation_config = {
        "temperature": 0.1,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048
    }
    safety_settings = [
        {"category": c, "threshold": "BLOCK_ONLY_HIGH"}
        for c in [
            "HARM_CATEGORY_HARASSMENT",
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
        ]
    ]

    # Keep a reference object; actual SDK versions differ so we handle generation safely below.
    try:
        llm_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    except Exception:
        # If this constructor is unavailable in installed SDK, set llm_model to a sentinel and try genai.generate() later.
        llm_model = "GENAI_CLIENT"
except Exception as e:
    st.error(f"⚠️ Error loading Gemini API key or model: {e}")
    llm_model = None

# --- Load Embedding Model (cache by model_name) ---
@st.cache_resource
def load_embedding_model(model_name: str) -> Optional[SentenceTransformer]:
    """
    Load a SentenceTransformer model by name. Cached by model_name to avoid caching unhashable objects.
    """
    try:
        if model_name == "bge":
            model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        elif model_name == "minilm":
            model = SentenceTransformer("all-MiniLM-L6-v2")
        elif model_name == "e5":
            model = SentenceTransformer("intfloat/e5-large-v2")
        else:
            raise ValueError(f"Unknown model name: {model_name}")
        return model
    except Exception as e:
        st.error(f"⚠️ Error loading embedding model {model_name}: {e}")
        return None


embedding_model = load_embedding_model(selected_embedding_model)

# --- Load FAISS Index and Metadata (cache by selection) ---
@st.cache_resource
def load_faiss_index(strategy_name: str, model_name: str) -> Tuple[Optional[faiss.Index], Optional[Union[List[Dict], Dict]]]:
    index_basename = f"chunks_{strategy_name}_{model_name}"
    index_path = os.path.join(EMBEDDING_DIR, f"{index_basename}.faiss")
    map_path = os.path.join(EMBEDDING_DIR, f"{index_basename}.json")

    try:
        if not os.path.exists(index_path):
            st.warning(f"FAISS index not found: {index_path}")
            return None, None
        if not os.path.exists(map_path):
            st.warning(f"Metadata map not found: {map_path}")
            return None, None

        index = faiss.read_index(index_path)
        with open(map_path, "r", encoding="utf-8") as f:
            metadata_map = json.load(f)

        return index, metadata_map
    except Exception as e:
        st.error(f"⚠️ Error loading FAISS index or metadata: {e}")
        return None, None


faiss_index, metadata_map = load_faiss_index(selected_chunk_strategy, selected_embedding_model)


# --- Helper: Resolve metadata for a FAISS index id robustly ---
def resolve_metadata_by_faiss_id(mmap: Union[List, Dict], idx: int) -> Optional[Dict]:
    """Attempt multiple strategies to locate metadata for a returned FAISS idx."""
    if mmap is None:
        return None
    try:
        if isinstance(mmap, list):
            if 0 <= idx < len(mmap):
                return mmap[idx]
            else:
                return None
        if isinstance(mmap, dict):
            # Try string key, int key, and fallback to positional values
            if str(idx) in mmap:
                return mmap[str(idx)]
            if idx in mmap:
                return mmap[idx]
            # If values look like a list wrapped in dict, try conversion
            vals = list(mmap.values())
            if 0 <= idx < len(vals):
                return vals[idx]
    except Exception:
        return None
    return None


# --- RAG Backend Function (Robust, Fixed FAISS Search + Logging) ---
def get_rag_response(user_query: str,
                     _embedding_model: SentenceTransformer,
                     _faiss_index: faiss.Index,
                     _metadata_map: Union[List, Dict]):
    """
    Generate a RAG response using FAISS-based retrieval and Gemini LLM.
    Handles all known FAISS tuple-return bugs and provides detailed Streamlit logs.
    """
    # --- Sanity Checks ---
    if not _embedding_model:
        return "Embedding model not initialized. Check logs.", []
    if _faiss_index is None or _metadata_map is None:
        return "Retrieval index or metadata missing. Ensure FAISS index and metadata JSON exist.", []
    if not llm_model:
        return "Language model (Gemini) not configured. Check API key and SDK.", []

    try:
        # --- Step 1: Encode Query into Embedding ---
        emb = _embedding_model.encode([user_query])

        # Some models return [array], others np.ndarray directly
        if isinstance(emb, (list, tuple)):
            query_embedding = np.array(emb[0], dtype="float32").reshape(1, -1)
        else:
            query_embedding = np.array(emb, dtype="float32").reshape(1, -1)

        # --- Step 2: FAISS Search (Safe unpacking) ---
        try:
            faiss_result = _faiss_index.search(query_embedding, TOP_K)
        except Exception as e:
            st.error(f"⚠️ FAISS search raised exception: {e}")
            return "Retrieval failed due to FAISS error. Check index compatibility.", []

        # Handle different shapes of return values from FAISS
        distances, indices = None, None
        if isinstance(faiss_result, (tuple, list)):
            if len(faiss_result) >= 2:
                distances, indices = faiss_result[0], faiss_result[1]
            else:
                st.error(f"⚠️ Unexpected FAISS search tuple length: {len(faiss_result)}")
                return "Retrieval returned unexpected shape from FAISS. Check logs.", []
        elif hasattr(faiss_result, "distances") and hasattr(faiss_result, "labels"):
            distances = getattr(faiss_result, "distances")
            indices = getattr(faiss_result, "labels")
        else:
            try:
                distances, indices = faiss_result[0], faiss_result[1]
            except Exception as e_unpack:
                st.error(f"⚠️ Unable to parse FAISS result type={type(faiss_result)} | {repr(faiss_result)[:300]}")
                return "Retrieval returned an unrecognized format. Verify FAISS version.", []

        # --- Step 3: Retrieve Top-K Chunks ---
        indices_row = indices[0] if indices is not None else []
        retrieved_chunks = []
        context_blocks = []

        for rank, idx in enumerate(indices_row):
            if idx is None or int(idx) < 0:
                continue

            idx_int = int(idx)
            chunk_data = resolve_metadata_by_faiss_id(_metadata_map, idx_int)

            if chunk_data:
                retrieved_chunks.append(chunk_data)
                src_path = chunk_data.get("metadata", {}).get("source_path", f"Source {rank + 1}")
                content = chunk_data.get("content", "")
                context_blocks.append(
                    f"### Context Source {rank + 1} (Document: {src_path}) ###\n{content}\n\n"
                )

        if not retrieved_chunks:
            return (
                "Sorry, I couldn't find relevant information in the secured JioPay documents.",
                [],
            )

        context_str = "\n".join(context_blocks)

        # --- Step 4: Build Authoritative Prompt ---
        prompt = f"""You are the JioPay Concierge AI — an executive-level assistant specialized in payments, policy, and integration.
Provide strictly factual answers based only on the given context. Do not speculate.

Protocol:
1. Read the user's inquiry and the provided context.
2. Provide a concise, accurate, and authoritative response.
3. If context is insufficient, reply exactly:
"I cannot fulfill this request as the necessary information is not present in the secured JioPay documentation."

Context:
{context_str}

User Inquiry: {user_query}

Concise Answer:"""

        # --- Step 5: Generate Response with Gemini ---
        try:
            if hasattr(llm_model, "generate_content"):
                response = llm_model.generate_content(prompt)
                llm_text = getattr(response, "text", None) or str(response)
            else:
                try:
                    response = genai.generate(
                        model="gemini-2.5-flash",
                        prompt=prompt,
                        **generation_config,
                    )
                    llm_text = getattr(response, "text", None) or getattr(response, "output", None) or str(response)
                    if isinstance(llm_text, (list, tuple)):
                        llm_text = llm_text[0]
                    if isinstance(llm_text, dict) and "content" in llm_text:
                        llm_text = llm_text["content"]
                except Exception as e_gen:
                    st.error(f"⚠️ Gemini generation error: {e_gen}")
                    return "Language model generation failed. Check Gemini SDK/API key.", retrieved_chunks

            return llm_text.strip(), retrieved_chunks

        except Exception as e_llm:
            st.error(f"⚠️ Error invoking Gemini: {e_llm}")
            return "An error occurred during response generation. See logs for details.", retrieved_chunks

    except Exception as e_outer:
        st.error(f"⚠️ Error during RAG processing: {e_outer}")
        return "An internal error occurred during retrieval or encoding. Check logs.", []


# --- Main UI ---
# Header
st.markdown(
    """
<div class="main-header">
    <h1>👑 JioPay Concierge AI</h1>
    <p>Providing definitive answers from secured JioPay documentation. Ablation in progress.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Status indicator row
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown(f'<span class="status-badge">Chunk: {selected_chunk_strategy.title()}</span>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<span class="status-badge">Embed: {selected_embedding_model.upper()}</span>', unsafe_allow_html=True)
with col3:
    if faiss_index is not None and metadata_map is not None:
        st.markdown('<span class="status-badge status-active">System Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge" style="border-color: var(--dark-red); color: var(--dark-red);">⚠ Index Missing</span>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Initialize session messages once
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Welcome. I am the JioPay Concierge AI. Please submit your inquiry regarding payments, policy, or integration, and I shall consult the official documentation.",
        "citations": []
    })

# Render chat history
for message in st.session_state.messages:
    role = message.get("role", "assistant")
    with st.chat_message(role, avatar="👑" if role == "assistant" else "👤"):
        st.markdown(message.get("content", ""))
        if message.get("citations"):
            with st.expander("📜 View Official References"):
                for i, chunk in enumerate(message.get("citations", [])):
                    meta = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
                    title = meta.get("source_title", meta.get("title", "Unknown Title"))
                    path = meta.get("source_path", "#")
                    st.markdown(f"**{i+1}. Reference Document:** [{title}]({path})")
                    st.caption(chunk.get("content", "N/A"))
                    if i < len(message.get("citations", [])) - 1:
                        st.markdown("---")

# Chat input + handling
if user_prompt := st.chat_input("💬 Submit your inquiry..."):
    # record user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # assistant placeholder
    with st.chat_message("assistant", avatar="👑"):
        placeholder = st.empty()
        # show spinner while retrieving
        with st.spinner("🧐 Consulting Official Documentation..."):
            assistant_response, source_chunks = get_rag_response(
                user_prompt, embedding_model, faiss_index, metadata_map
            )

        # streaming-like display but in chunks for responsiveness
        if not assistant_response:
            assistant_response = "No response from language model."

        displayed = ""
        chunk_size = 80  # characters per update - fast and readable
        for i in range(0, len(assistant_response), chunk_size):
            displayed += assistant_response[i:i + chunk_size]
            placeholder.markdown(displayed + "▌")
            time.sleep(0.02)
        placeholder.markdown(displayed)  # final render

        # show sources in expander for persistence
        if source_chunks:
            with st.expander("📜 View Official References"):
                for i, chunk in enumerate(source_chunks):
                    meta = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
                    title = meta.get("source_title", meta.get("title", "Unknown Title"))
                    path = meta.get("source_path", "#")
                    st.markdown(f"**{i+1}. Reference Document:** [{title}]({path})")
                    st.caption(chunk.get("content", "N/A"))
                    if i < len(source_chunks) - 1:
                        st.markdown("---")

    # persist assistant message in session
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response,
        "citations": source_chunks or []
    })

# Footer
st.markdown(
    """
<div class="footer" style="border-top: 1px solid var(--peacock-blue); background-color: var(--black); color: var(--silver-text); text-align: center; padding: 1rem; font-size: 0.86rem; margin-top: 2rem;">
    <p>👑 <strong>JioPay Concierge AI</strong> | Authority, Accuracy, and Transparency</p>
    <p style="font-size: 0.82rem; color: #9E9E9E;">A Vizuara RAG Ablation Study Implementation</p>
</div>
""",
    unsafe_allow_html=True,
)

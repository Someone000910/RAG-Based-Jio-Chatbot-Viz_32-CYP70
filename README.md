# JioPay Customer Support RAG Chatbot

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A production-grade Retrieval-Augmented Generation (RAG) chatbot for JioPay customer support queries, built with Google Gemini and FAISS. Features multiple chunking strategies and embedding models for comprehensive ablation studies.

## 🌟 Features

- **Full RAG Pipeline**: Complete implementation of Retrieval → Augmentation → Generation workflow
- **Public Knowledge Base**: Built from scraped JioPay web pages, help center, and developer documentation
- **Multiple Chunking Strategies**: 
  - Fixed-size chunking
  - Recursive text splitting
  - Structural chunking
  - Semantic chunking
  - LLM-based chunking (Gemini)
- **Multiple Embedding Models**:
  - `bge-small-en-v1.5`
  - `all-MiniLM-L6-v2`
  - `e5-large-v2`
- **Vector Search**: FAISS-powered efficient similarity search
- **Source Citations**: Answers include URL, title, and snippet citations
- **Interactive UI**: Built with Streamlit for easy experimentation
- **Deployment Ready**: Configured for Streamlit Community Cloud

## 📋 Table of Contents

- [Demo](#-demo)
- [Installation](#-installation)
- [Project Structure](#-project-structure)
- [Data Pipeline](#-data-pipeline)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [Ablation Studies](#-ablation-studies)
- [Contributing](#-contributing)
- [License](#-license)

## 🎥 Demo

**Live Application**: [Add Your Streamlit App URL Here]

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google API Key ([Get one here](https://aistudio.google.com/))
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Linux users**: pyperclip may require xclip
   > ```bash
   > sudo apt-get install xclip
   > ```

4. **Configure API key**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Add your Google API key:
   ```env
   GOOGLE_API_KEY="your_api_key_here"
   ```

## 📁 Project Structure

```
Assignment 2/
├── extraction/
│   ├── data/
│   │   ├── knowledge_base.json          # Raw extracted data
│   │   └── knowledge_base_cleaned.json  # Cleaned data
│   ├── build_knowledge_base.py          # Data extraction script
│   └── clean_json_data.py               # Data cleaning script
├── chunking/
│   ├── chunk_utils.py                   # Chunking utilities
│   ├── chunk_fixed.py                   # Fixed-size chunking
│   ├── chunk_recursive.py               # Recursive chunking
│   ├── chunk_structural.py              # Structural chunking
│   ├── chunk_semantic.py                # Semantic chunking
│   ├── chunk_llm.py                     # LLM-based chunking
│   └── run_all_chunkers.py              # Generate all chunks
├── embedding/
│   ├── embedder.py                      # Base embedder
│   ├── generate_bge_embeddings.py       # BGE embeddings
│   ├── generate_minilm_embeddings.py    # MiniLM embeddings
│   └── generate_e5_embeddings.py        # E5 embeddings
├── app.py                               # Main Streamlit application
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment template
├── DATA CARD.md                         # Data source documentation
├── LICENSE
└── README.md
```

## 🔄 Data Pipeline

The chatbot requires locally generated data. Follow these steps in order:

### Step 1: Collect Source Data

Manually save JioPay HTML pages and PDFs into `extraction/data/`. See `DATA CARD.md` for required sources.

### Step 2: Build Knowledge Base

```bash
cd extraction
python build_knowledge_base.py
```

Creates `extraction/data/knowledge_base.json`

### Step 3: Clean Data

```bash
python clean_json_data.py -i data/knowledge_base.json -o data/knowledge_base_cleaned.json
```

Creates `extraction/data/knowledge_base_cleaned.json`

### Step 4: Generate Chunks

```bash
cd ../chunking
python run_all_chunkers.py
```

Creates `chunks_*.json` files in the `chunking/` directory

### Step 5: Generate Embeddings

Run these sequentially to avoid memory issues:

```bash
cd ../embedding
python generate_minilm_embeddings.py
python generate_bge_embeddings.py
python generate_e5_embeddings.py
```

Creates `*.faiss` index files and `chunks_*.json` mapping files in the `embedding/` directory

## 💻 Usage

### Local Development

1. Complete all data pipeline steps above
2. Ensure `.env` file contains your `GOOGLE_API_KEY`
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Open your browser to the displayed URL (typically `http://localhost:8501`)
5. Select chunking strategy and embedding model in the sidebar
6. Start asking questions about JioPay!

### Example Queries

- "How do I reset my JioPay PIN?"
- "What are the transaction limits on JioPay?"
- "How can I link my bank account to JioPay?"

## 🌐 Deployment

This application is configured for Streamlit Community Cloud deployment.

### Deployment Steps

1. Push your repository to GitHub
2. Connect to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Add `GOOGLE_API_KEY` in Streamlit Secrets management
4. Deploy from your GitHub repository

> **Note**: Large embedding files (`*.faiss`) are not included in the repository due to size constraints. For full functionality in production, consider using cloud storage solutions or generating embeddings on deployment.

## 🔬 Ablation Studies

This project implements comprehensive ablation studies across three dimensions:

### 1. Data Ingestion Methods
- Static scraping
- Dynamic scraping (Selenium)
- Manual extraction

### 2. Chunking Strategies
- **Fixed**: Equal-sized chunks with overlap
- **Recursive**: Hierarchical text splitting
- **Structural**: Document structure-aware chunking
- **Semantic**: Meaning-based segmentation
- **LLM-based**: Gemini-powered intelligent chunking

### 3. Embedding Models
- **bge-small-en-v1.5**: Balanced performance
- **all-MiniLM-L6-v2**: Lightweight and fast
- **e5-large-v2**: High-quality embeddings

### Evaluation Metrics

Quantitative analysis includes:
- **Retrieval**: Precision@1, Recall@k, MRR
- **Quality**: F1 Score
- **Performance**: Latency, Index Size
- **Cost**: Token usage and API costs

Results are detailed in the project report (Phase 5).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Vizuara "LLM Production and Deployment" assignment
- Powered by Google Gemini API
- Uses FAISS for vector similarity search
- Built with Streamlit

## 📧 Contact

For questions or feedback, please open an issue in this repository.

---

**Made with ❤️ for better customer support experiences**

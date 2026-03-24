# LLM-Based Hybrid RAG System: Online & Offline Document Integration

## 🎓 Final Year Project
**Domain:** Artificial Intelligence & Machine Learning  
**Core Objective:** To overcome the "Knowledge Cutoff" and "Hallucination" limitations of Large Language Models (LLMs) by integrating a real-time Hybrid Retrieval-Augmented Generation (RAG) pipeline.

---

## 🚀 Overview
Standard LLMs are limited by their training data cutoff dates. This project implements a **Hybrid RAG** system that combines:
1.  **Offline Retrieval:** Processes user-uploaded documents (PDFs/Text) using semantic vector search.
2.  **Online Retrieval:** Fetches real-time web data to supplement missing information.
3.  **Intelligent Arbitration:** The system automatically detects if it has enough info offline or needs to search the web, ensuring the most accurate and up-to-date response.

---

## 🛠️ Technical Stack
* **LLM:** `TinyLlama-1.1B-Chat-v1.0` (Optimized with FP16 for local execution)
* **Embeddings:** `all-MiniLM-L6-v2` (Sentence-Transformers)
* **Vector Search:** FAISS / Custom Indexing
* **Backend:** Python 3.x, PyTorch
* **Real-time Data:** Online Scraping & Search APIs

---

## ✨ Key Features
* **Academic Grading Logic:** The system detects keywords like "2 mark", "10 mark", or "16 mark" to adjust the length and depth of the answer.
* **Structural Output:** High-mark questions automatically generate side headings (Introduction, Core Concepts, Working, Conclusion).
* **Source Attribution:** Every answer is tagged with 📌 **Source: Offline**, **Online**, or **Hybrid** to ensure transparency.
* **Ask-Back Mechanism:** If the system cannot find relevant data in either source, it prompts the user to upload more specific documents.
* **Automated Logging:** All interactions, sources, and timestamps are saved to `project_logs.csv` for result analysis.

---

## 📂 Project Structure
```text
├── data/               # Folder for user-uploaded documents (PDFs/TXT)
├── mods/               # Virtual environment (ignored by git)
├── pipeline.py         # Main execution script
├── data_loader.py      # Document processing logic
├── retriever.py        # Vector search & Reranking logic
├── online_retrieval.py # Web search integration
├── project_logs.csv    # Auto-generated interaction history
└── requirements.txt    # List of dependencies
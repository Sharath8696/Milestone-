# Mutual Fund FAQ Assistant

A facts-only Retrieval-Augmented Generation (RAG) assistant designed to answer objective, verifiable queries related to mutual funds. The system relies entirely on a curated corpus of official public documents and strictly avoids providing investment advice, opinions, or recommendations.

## Overview

Based on the [Groww product context](https://groww.in), this assistant retrieves context from 5 specific HDFC Mutual Fund pages and generates concise, highly-regulated answers powered by an embedded semantic search engine.

### Selected AMC and Schemes
**Asset Management Company (AMC):** HDFC Mutual Fund
1. HDFC Mid-Cap Fund (Direct Growth)
2. HDFC Equity Fund (Direct Growth)
3. HDFC Focused Fund (Direct Growth)
4. HDFC ELSS Tax Saver Fund (Direct Plan Growth)
5. HDFC Large-Cap Fund (Direct Growth)

## Architecture

The system utilizes a 5-part localized RAG architecture:

1. **Ingestion (Batch Offline Component)**: 
   - A Github Actions workflow runs a daily schedule to execute a localized web scraper.
   - Text is parsed using BeautifulSoup, chunked using Langchain, and passed through `text-embedding-3-small`.
   - Resulting vectors are committed to a local `ChromaDB` directory.
2. **Retrieval**: 
   - Queries map to vectors, returning K=4 chunks utilizing basic semantic similarity search.
3. **Generation & Guardrails**:
   - Stringent input-filtering verifies intent (blocking PII & "Should I invest?" logic).
   - Generates answers constrained to 3 sentences, powered by `gpt-4o-mini`.
4. **API Backend**: 
   - Managed by `FastAPI` to provide seamless, concurrent session states mapping chat IDs directly to in-memory dictionaries.
5. **Frontend**:
   - Exposes a minimal Streamlit interface that strictly showcases a `"Facts-only. No investment advice."` disclaimer wrapper. 

## Setup Instructions

### Environment Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation

1. **Clone the repository and jump to the target directory:**
   ```bash
   cd test
   ```

2. **Install all Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a local `.env` file in the root codebase and define your OpenAI token.
   ```bash
   OPENAI_API_KEY="sk-proj-xyz..."
   ```

4. **Initialize the Vector Database:**
   *(Run this once initially, or to manually refresh vector documents)*
   ```bash
   python ingestion/vector_store.py
   ```

5. **Start the Application Stack:**
   Launch the FastAPI background application and the Streamlit frontend concurrently:
   ```bash
   python run.py
   ```
   > The UI will automatically launch in your browser explicitly listening on Port 8501.

## Known Limitations
- The Vector Database (`ChromaDB`) runs entirely stateless locally to `data/chroma_db`. In a larger system, it should map to a standalone Cloud instance (e.g. PineCone, AWS OpenSearch).
- Chat Thread persistency relies entirely on dictionaries in RAM in `api/main.py`. Server resets wipe session logs securely but permanently. A production mapping would rely on robust storage architecture targeting Redis.

# RAG Ingestion Pipeline

This project provides a pipeline for ingesting, chunking, embedding, and storing text documents for Retrieval-Augmented Generation (RAG) applications. It uses [LangChain](https://python.langchain.com/), [ChromaDB](https://www.trychroma.com/), and Google Gemini Embeddings to process and persist document data for downstream retrieval tasks.

---

## Features

- **Document Loading:** Loads all `.txt` files from a specified directory (including subfolders).
- **Chunking:** Splits large documents into manageable text chunks.
- **Chunk Persistence:** Saves chunks as JSON for incremental processing.
- **Embeddings:** Uses Google Gemini to create vector embeddings for each chunk.
- **Vector Store:** Stores embeddings in a local ChromaDB instance for efficient retrieval.
- **Incremental Processing:** Only processes new or remaining chunks on subsequent runs.

---

## Directory Structure

```
RAG/
├── docs/                # Place your .txt documents here
├── db/
│   ├── chunks           # JSON file with chunked document data
│   └── chroma_db/       # ChromaDB persistent storage
├── ingestion_pipeline.py
├── .env                 # For API keys and environment variables
└── README.md
```

---

## Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd RAG
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the project root.
   - Add your Google Gemini API key:
     ```
     GOOGLE_API_KEY=your_google_gemini_api_key
     ```

4. **Add your documents:**
   - Place your `.txt` files in the `docs/` directory.

---

## Usage

Run the ingestion pipeline:

```sh
python ingestion_pipeline.py
```

- On first run, the script will:
  - Load and chunk all documents in `docs/`
  - Save chunks to `db/chunks`
  - Embed and store chunks in ChromaDB (`db/chroma_db`)
- On subsequent runs, it will only process new or remaining chunks.

---

## Code Overview

### ingestion_pipeline.py

- **load_documents(docs_path="docs")**  
  Loads all `.txt` files from the specified directory (including subfolders) using LangChain's `DirectoryLoader`. Prints info about the first two documents.

- **split_documents(documents, chunk_size=1000, chunk_overlap=0)**  
  Splits documents into smaller chunks using `CharacterTextSplitter`. Prints info about the first five chunks.

- **save_chunks(chunks, filename="db/chunks")**  
  Saves the chunked data as a JSON file for incremental processing.

- **create_vector_store(chunksjson_dir="db/chunks", persist_directory="db/chroma_db")**  
  Loads chunks from JSON, creates embeddings using Google Gemini, and stores them in ChromaDB. Pops processed chunks from the JSON to allow incremental processing.

- **main()**  
  Orchestrates the pipeline:
  - If `db/chunks` does not exist or is empty, loads and chunks documents, saves them, and creates the vector store.
  - If `db/chunks` exists and has unprocessed chunks, continues embedding and storing them.

---

## Customization

- **Chunk Size:** Adjust `chunk_size` in `split_documents()` for larger/smaller text segments.
- **Embeddings Model:** Change the model in `GoogleGenerativeAIEmbeddings` if needed.
- **Document Types:** Extend `DirectoryLoader` to support other file formats.

---

## Requirements

- Python 3.8+
- [langchain](https://pypi.org/project/langchain/)
- [chromadb](https://pypi.org/project/chromadb/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Google Gemini API access

---

## License

MIT License

---

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [Google Gemini](https://ai.google.dev/)

---

**Note:** For production use, ensure proper error handling, logging, and security for API keys.
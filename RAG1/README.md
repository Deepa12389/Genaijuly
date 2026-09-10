# HDFC Bank Financial RAG

`RAG1` is a financial document question-answering system for HDFC Bank's FY 2024-25 annual report. It extracts the report, creates searchable chunks and embeddings, stores them in ChromaDB, and uses an LLM to generate answers with page and section citations.

## Features

- PDF ingestion and financial-document preprocessing
- ChromaDB vector search
- Ollama or OpenAI embeddings and text generation
- Scope filters for `All`, `Standalone`, `Consolidated`, and `ESG`
- Browser chat interface at `/`
- JSON API endpoints for querying and re-ingestion

## Project Layout

```text
RAG1/
├── app.py                         # Application entry point and API routes
├── web/index.html                 # Browser interface
├── chroma_db/                     # Persisted ChromaDB data
├── utils/
│   ├── config.yaml                # PDF, model, chunking, and store settings
│   ├── ingestion.py               # PDF-to-vector-store pipeline
│   ├── query.py                   # Retrieval and answer generation
│   ├── retrieval.py               # Similarity search
│   ├── embedding.py               # Ollama/OpenAI embeddings
│   └── requirements.txt
└── utils/HDFC_Bank_Annual_Report_2024_25-310202.pdf
```

## Requirements

- Python 3.10 or newer
- An LLM and embedding backend:
  - Ollama running locally, or
  - an OpenAI API key

## Installation

From the `RAG1` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\utils\requirements.txt
```

### Option A: Ollama

Install Ollama, start it, and download the configured models:

```powershell
ollama pull nomic-embed-text:latest
ollama pull llama3.2:latest
$env:USE_OLLAMA = "true"
```

The default Ollama endpoint is `http://localhost:11434`. Override it when needed:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

### Option B: OpenAI

Set the API key in the shell or in a local `.env` file. Never commit the key.

```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:USE_OLLAMA = "false"
```

Set `llm.model` and `embedding.model` in `utils/config.yaml` to the OpenAI models you intend to use.

## Ingest the Report

Run ingestion once before asking questions:

```powershell
python .\utils\ingestion.py
```

This extracts the PDF, preprocesses and chunks the text, generates embeddings, and writes the indexed data to `chroma_db/`. Run it again after replacing the source PDF or changing chunking or embedding settings.

## Start the Application

```powershell
python .\app.py
```

Or start Uvicorn directly:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open <http://127.0.0.1:8000> in a browser.

## API

### Ask a question

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/query `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query":"What was HDFC Bank\'s net profit in FY25?","scope":"Standalone"}'
```

The response contains:

```json
{
  "answer": "...",
  "citations": [
    {"page": 210, "section": "...", "scope": "Standalone"}
  ],
  "raw_context": ["..."]
}
```

Supported scopes are `All`, `Standalone`, `Consolidated`, and `ESG`.

### Re-ingest the PDF

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/ingest -Method Post
```

## Configuration

Edit `utils/config.yaml` to change:

- Source PDF path
- Chunk size and overlap
- Embedding and LLM models
- ChromaDB collection and persistence directory
- Number of retrieved chunks (`top_k`)

The application is configured to prioritize accurate financial answers: it asks the model to distinguish standalone from consolidated figures, state units, cite pages and sections, and avoid guessing when the report does not contain the requested information.

## Troubleshooting

- **No LLM backend available:** start Ollama or set `OPENAI_API_KEY`.
- **Ollama model errors:** verify that both `nomic-embed-text:latest` and `llama3.2:latest` are installed, or update `utils/config.yaml`.
- **Empty or outdated results:** run the ingestion command again and confirm that `utils/config.yaml` points to the intended PDF.
- **File not found errors:** run commands from the `RAG1` directory so the relative `utils/` and `chroma_db/` paths resolve correctly.
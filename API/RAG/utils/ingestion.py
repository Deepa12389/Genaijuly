import yaml
from qdrant_client import QdrantClient

from utils.loader import load_pdf
from utils.preprocessing import preprocess
from utils.chunking import chunk_text
from utils.embedding import generate_embeddings
from utils.vectorstore import setup_collection, ingest_chunks

import os

PDF_PATH = os.getenv("PDF_PATH", "hr_policy_detailed_5_pages.pdf")


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def main():

    config = load_config()

    print("Loading PDF...")
    raw_text = load_pdf(PDF_PATH)

    print("Preprocessing...")
    cleaned = preprocess(raw_text)

    print("Chunking...")
    chunks = chunk_text(cleaned)

    print("Total chunks:", len(chunks))

    print("Generating embeddings via Ollama...")
    embeddings = generate_embeddings(
        chunks,
        config["ollama"]["embedding_model"]
    )

    print("Connecting Qdrant...")
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", config["qdrant"]["host"]),
        port=int(os.getenv("QDRANT_PORT", config["qdrant"]["port"]))
    )

    setup_collection(
        client,
        config["qdrant"]["collection_name"],
        config["qdrant"]["vector_size"]
    )

    print("Ingesting vectors...")
    ingest_chunks(
        client,
        config["qdrant"]["collection_name"],
        chunks,
        embeddings
    )

    print("✅ Ingestion completed")


if __name__ == "__main__":
    main()
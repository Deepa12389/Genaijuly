from loader import FinancialPDFLoader
from preprocessing import FinancialPreprocessor
from chunking import FinancialChunker
from embedding import EmbeddingGenerator
from vectorstore import FinancialVectorStore
import time

def run_ingestion():
    print("=" * 60)
    print("[1/5] Starting PDF Document Extraction...")
    start = time.time()
    loader = FinancialPDFLoader()
    raw_pages = loader.extract_pages()
    print(f"      Extracted {len(raw_pages)} pages in {time.time() - start:.2f}s")

    print("[2/5] Running Preprocessing & Financial Categorisation...")
    preprocessor = FinancialPreprocessor()
    processed_pages = preprocessor.process(raw_pages)

    print("[3/5] Chunking Content into Structured Blocks...")
    chunker = FinancialChunker()
    chunks = chunker.chunk_documents(processed_pages)
    print(f"      Generated {len(chunks)} contextual chunks.")

    print("[4/5] Generating Embeddings (via OpenAI)...")
    embedder = EmbeddingGenerator()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.get_embeddings(texts)

    print("[5/5] Indexing into Chroma Vector Store...")
    vector_store = FinancialVectorStore()
    vector_store.add_chunks(chunks, embeddings)
    print("=" * 60)
    print("Ingestion successfully completed! Ready to query.")

if __name__ == "__main__":
    run_ingestion()
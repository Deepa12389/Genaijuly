import os
import chromadb
import yaml
from typing import List, Dict, Any


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class FinancialVectorStore:
    def __init__(self):
        config = load_config()
        self.persist_dir = config["vectorstore"]["persist_directory"]
        self.collection_name = config["vectorstore"]["collection_name"]
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Chroma has a default batch ceiling, add in batches of 500
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=texts[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size]
            )

    def query(self, query_embedding: List[float], n_results: int = 5, where_filter: Dict = None):
        params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results
        }
        if where_filter:
            params["where"] = where_filter
            
        return self.collection.query(**params)
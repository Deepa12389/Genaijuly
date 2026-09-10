import os
from embedding import EmbeddingGenerator
from vectorstore import FinancialVectorStore
from typing import List, Dict, Any
import yaml


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class FinancialRetriever:
    def __init__(self):
        config = load_config()
        self.top_k = config["llm"]["top_k"]
        self.embedder = EmbeddingGenerator()
        self.store = FinancialVectorStore()

    def retrieve(self, query: str, scope: str = "All") -> List[Dict[str, Any]]:
        query_embedding = self.embedder.get_query_embedding(query)
        
        where_filter = None
        if scope in ["Standalone", "Consolidated", "ESG"]:
            where_filter = {"scope": scope}

        results = self.store.query(query_embedding, n_results=self.top_k, where_filter=where_filter)

        retrieved_docs = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            for doc_text, metadata in zip(docs, metas):
                retrieved_docs.append({
                    "text": doc_text,
                    "metadata": metadata
                })

        return retrieved_docs
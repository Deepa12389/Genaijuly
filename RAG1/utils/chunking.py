import os
from typing import List, Dict, Any
import yaml


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class FinancialChunker:
    def __init__(self):
        config = load_config()
        self.chunk_size = config["chunking"]["chunk_size"]
        self.chunk_overlap = config["chunking"]["chunk_overlap"]

    def chunk_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_id = 0

        for doc in docs:
            text = doc["content"]
            meta = doc["metadata"]
            
            # Split text by paragraphs/lines
            paragraphs = text.split("\n\n")
            current_chunk = []
            current_length = 0

            for para in paragraphs:
                para_len = len(para)
                if current_length + para_len > self.chunk_size and current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    
                    # Context header ensures isolated numbers have context
                    contextual_header = (
                        f"[{meta['section']} | Scope: {meta['scope']} | "
                        f"Page: {meta['page_number']} | Units: {meta['unit']}]\n"
                    )
                    
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": contextual_header + chunk_text,
                        "metadata": {
                            "page_number": meta["page_number"],
                            "scope": meta["scope"],
                            "section": meta["section"],
                            "unit": meta["unit"]
                        }
                    })
                    chunk_id += 1

                    # Retain last paragraph for overlap
                    current_chunk = [current_chunk[-1]] if len(current_chunk) > 1 else []
                    current_length = len(current_chunk[0]) if current_chunk else 0

                current_chunk.append(para)
                current_length += para_len

            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                contextual_header = (
                    f"[{meta['section']} | Scope: {meta['scope']} | "
                    f"Page: {meta['page_number']} | Units: {meta['unit']}]\n"
                )
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": contextual_header + chunk_text,
                    "metadata": {
                        "page_number": meta["page_number"],
                        "scope": meta["scope"],
                        "section": meta["section"],
                        "unit": meta["unit"]
                    }
                })
                chunk_id += 1

        return chunks
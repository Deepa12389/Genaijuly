import os
import yaml
from typing import List
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from ollama import Client
except Exception:
    Client = None

if os.getenv("USE_OLLAMA", "").lower() not in {"true", "1", "yes", "on"}:
    load_dotenv()


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _normalize_ollama_model(model_name: str) -> str:
    model_name = str(model_name).strip()
    if model_name and ":" not in model_name and "/" not in model_name:
        return model_name + ":latest"
    return model_name


def _should_use_ollama() -> bool:
    env_value = os.getenv("USE_OLLAMA", "").strip().lower()
    if env_value in {"true", "1", "yes", "on"}:
        return True
    if env_value in {"false", "0", "no"}:
        return False
    return Client is not None


class EmbeddingGenerator:
    def __init__(self):
        config = load_config()
        self.model = _normalize_ollama_model(os.getenv("OLLAMA_EMBED_MODEL", config["embedding"].get("model", "nomic-embed-text:latest")))
        self.use_ollama = _should_use_ollama()
        self.openai_client = None
        self.ollama_client = None

        if Client is not None:
            self.ollama_client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

        if OpenAI is not None and os.getenv("OPENAI_API_KEY") and not self.use_ollama:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif OpenAI is not None and os.getenv("OPENAI_API_KEY") and self.ollama_client is None:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.ollama_client is None:
            raise RuntimeError("Ollama is not installed or not running. Install Ollama and run: ollama pull nomic-embed-text")
        response = self.ollama_client.embed(model=self.model, input=texts)
        return response.get("embeddings", [])

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.ollama_client is not None and self.use_ollama:
            return self._ollama_embeddings(texts)

        if self.openai_client is not None:
            try:
                batch_size = 64
                all_embeddings = []
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    batch = [t if t.strip() else "empty" for t in batch]
                    response = self.openai_client.embeddings.create(input=batch, model=self.model)
                    all_embeddings.extend([item.embedding for item in response.data])
                return all_embeddings
            except Exception:
                if self.ollama_client is not None:
                    return self._ollama_embeddings(texts)
                raise

        if self.ollama_client is not None:
            return self._ollama_embeddings(texts)

        raise RuntimeError("No embedding backend available. Set OPENAI_API_KEY or start Ollama.")

    def get_query_embedding(self, query: str) -> List[float]:
        if self.ollama_client is not None and self.use_ollama:
            response = self.ollama_client.embed(model=self.model, input=[query])
            return response["embeddings"][0]

        if self.openai_client is not None:
            try:
                response = self.openai_client.embeddings.create(input=[query], model=self.model)
                return response.data[0].embedding
            except Exception:
                if self.ollama_client is not None:
                    response = self.ollama_client.embed(model=self.model, input=[query])
                    return response["embeddings"][0]
                raise

        if self.ollama_client is not None:
            response = self.ollama_client.embed(model=self.model, input=[query])
            return response["embeddings"][0]

        raise RuntimeError("No embedding backend available. Set OPENAI_API_KEY or start Ollama.")
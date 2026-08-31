import os
import yaml
import requests
from qdrant_client import QdrantClient


#Ollama API endpoints (override with OLLAMA_BASE_URL, e.g. http://host.docker.internal:11434 in Docker)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
EMBED_URL = f"{OLLAMA_BASE_URL}/api/embeddings"

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


# Convert user question into embedding
def embed_query(query, model):

    response = requests.post(
        EMBED_URL,
        json={
            "model": model,
            "prompt": query
        }
    )

    data = response.json()

    if "embedding" not in data:
        raise Exception(f"Ollama embedding error: {data}")

    return data["embedding"]


# Ask LLM with retrieved context
def ask_llm(context, question, model):

    prompt = f"""
You are an HR assistant.

Use the provided context to answer the question.

Context:
{context}

Question:
{question}

Please make sure to stick to the data present in the document and answer dont give unncessary information
Answer clearly and concisely.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    if "response" not in data:
        raise Exception(f"Ollama generation error: {data}")

    return data["response"]


def main():

    config = load_config()

    # Connect to Qdrant (env vars override config.yaml, useful inside Docker)
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", config["qdrant"]["host"]),
        port=int(os.getenv("QDRANT_PORT", config["qdrant"]["port"]))
    )

    # User question
    question = input("\nAsk a question: ")

    # Convert question to embedding
    query_vector = embed_query(
        question,
        config["ollama"]["embedding_model"]
    )

    # Vector search in Qdrant
    results = client.query_points(
        collection_name=config["qdrant"]["collection_name"],
        query=query_vector,
        limit=3
    )

    # Extract retrieved chunks
    context = "\n".join(
        point.payload["text"] for point in results.points
    )

    print("\nRetrieved Context:\n")
    print(context)

    # Ask LLM
    answer = ask_llm(
        context,
        question,
        config["ollama"]["llm_model"]
    )

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()
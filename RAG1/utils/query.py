import os
import yaml
from typing import Dict, Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from ollama import Client
except Exception:
    Client = None

from dotenv import load_dotenv

if os.getenv("USE_OLLAMA", "").lower() not in {"true", "1", "yes", "on"}:
    load_dotenv()

from retrieval import FinancialRetriever


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


FINANCIAL_SYSTEM_PROMPT = """You are a senior financial analyst assistant for HDFC Bank's Annual Report (FY 2024-25).
Answer questions strictly based on the provided context. Follow these critical rules:
1. ALWAYS distinguish between 'Standalone' and 'Consolidated' figures.
2. ALWAYS state the units explicitly (e.g., '₹ in crore', '₹ in thousands', or percentages). Check table headings for units!
3. Cite the exact Page Number and Section for each key metric.
4. If the figures are not found in the context, explicitly say: 'The information is not available in the provided report excerpts.' Do not guess or extrapolate.
"""


class QueryEngine:
    def __init__(self):
        config = load_config()
        self.model = _normalize_ollama_model(os.getenv("OLLAMA_LLM_MODEL", config["llm"].get("model", "llama3.2:latest")))
        self.temperature = config["llm"].get("temperature", 0.0)
        self.retriever = FinancialRetriever()
        self.use_ollama = _should_use_ollama()

        self.openai_client = None
        self.ollama_client = None

        if Client is not None:
            self.ollama_client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

        if OpenAI is not None and os.getenv("OPENAI_API_KEY") and not self.use_ollama:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif OpenAI is not None and os.getenv("OPENAI_API_KEY") and self.ollama_client is None:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _ollama_answer(self, prompt: str) -> str:
        if self.ollama_client is None:
            raise RuntimeError("Ollama is not installed or not running. Install Ollama and run: ollama pull llama3.2")
        response = self.ollama_client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
            stream=False,
        )
        return response.get("response", "")

    def answer_query(self, question: str, scope: str = "All") -> Dict[str, Any]:
        retrieved_items = self.retriever.retrieve(question, scope=scope)

        context_str = "\n\n---\n\n".join([item["text"] for item in retrieved_items])

        user_prompt = f"""Context from HDFC Bank Annual Report:
{context_str}

User Question: {question}

Provide a concise, accurate financial response with citations:"""

        if self.ollama_client is not None and self.use_ollama:
            answer = self._ollama_answer(user_prompt)
        elif self.openai_client is not None:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": FINANCIAL_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception:
                if self.ollama_client is not None:
                    answer = self._ollama_answer(user_prompt)
                else:
                    raise
        elif self.ollama_client is not None:
            answer = self._ollama_answer(user_prompt)
        else:
            raise RuntimeError("No LLM backend available. Start Ollama or set OPENAI_API_KEY.")

        citations = [
            {"page": item["metadata"]["page_number"], "section": item["metadata"]["section"], "scope": item["metadata"]["scope"]}
            for item in retrieved_items
        ]

        unique_citations = [dict(t) for t in {tuple(d.items()) for d in citations}]

        return {
            "answer": answer,
            "citations": unique_citations,
            "raw_context": [item["text"] for item in retrieved_items]
        }
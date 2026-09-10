import pdfplumber
from typing import List, Dict, Any
import yaml
import os


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class FinancialPDFLoader:
    def __init__(self, pdf_path: str = None):
        config = load_config()
        self.pdf_path = pdf_path or config["pdf"]["path"]
        self.skip_early = config["pdf"]["skip_early_pages"]
        self.start_page = config["pdf"]["start_page"] if self.skip_early else 1
        self.end_page = config["pdf"]["end_page"]

    def extract_pages(self) -> List[Dict[str, Any]]:
        """Extracts text and tables while preserving page coordinates and numbers."""
        if not os.path.exists(self.pdf_path):
            # Try to find any matching PDF in the directory if exact name differs
            pdf_files = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
            if pdf_files:
                self.pdf_path = pdf_files[0]
            else:
                raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        extracted_docs = []
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            end = self.end_page if self.end_page else total_pages

            print(f"[+] Processing pages {self.start_page} to {end} out of {total_pages} total pages...")

            for page_idx in range(self.start_page - 1, end):
                page = pdf.pages[page_idx]
                page_number = page_idx + 1

                # 1. Try extracting tables into markdown syntax
                tables = page.extract_tables()
                table_md = ""
                if tables:
                    for table in tables:
                        clean_rows = [[str(cell or "").replace("\n", " ").strip() for cell in row] for row in table if any(row)]
                        if clean_rows:
                            # Build markdown table representation
                            headers = clean_rows[0]
                            header_line = "| " + " | ".join(headers) + " |"
                            sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
                            data_lines = ["| " + " | ".join(row) + " |" for row in clean_rows[1:]]
                            table_md += "\n" + "\n".join([header_line, sep_line] + data_lines) + "\n"

                # 2. Extract plain text
                raw_text = page.extract_text(layout=False) or ""
                
                # Merge table markdown and text
                combined_content = raw_text.strip()
                if table_md:
                    combined_content += "\n\n### Extracted Tables:\n" + table_md

                if combined_content.strip():
                    extracted_docs.append({
                        "page_number": page_number,
                        "content": combined_content
                    })

        return extracted_docs

if __name__ == "__main__":
    loader = FinancialPDFLoader()
    docs = loader.extract_pages()
    print(f"Loaded {len(docs)} pages.")
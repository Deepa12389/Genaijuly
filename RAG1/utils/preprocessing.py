import re
from typing import List, Dict, Any

class FinancialPreprocessor:
    @staticmethod
    def classify_section(page_num: int, text: str) -> Dict[str, Any]:
        """Classify report section and reporting scope (Standalone vs Consolidated)."""
        lower_text = text.lower()

        # Document boundaries for HDFC Annual Report
        if "consolidated balance sheet" in lower_text or "consolidated profit" in lower_text or (428 <= page_num <= 527):
            scope = "Consolidated"
            section = "Consolidated Financial Statements"
        elif "standalone balance sheet" in lower_text or "standalone profit" in lower_text or (310 <= page_num <= 427):
            scope = "Standalone"
            section = "Standalone Financial Statements"
        elif 208 <= page_num < 310:
            scope = "Statutory"
            section = "Directors Report & Corporate Governance"
        elif page_num >= 528:
            scope = "ESG"
            section = "Business Responsibility and Sustainability Report"
        else:
            scope = "Overview"
            section = "General Overview"

        # Unit detection
        unit = "Unspecified"
        if "` in ‘000" in text or "in ‘000" in text:
            unit = "INR in Thousands"
        elif "` in crore" in text or "in crore" in text or "c in crore" in text:
            unit = "INR in Crores"
        elif "` in lakh" in text or "in lakh" in text:
            unit = "INR in Lakhs"

        return {
            "scope": scope,
            "section": section,
            "unit": unit
        }

    def process(self, raw_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_docs = []
        for doc in raw_docs:
            text = doc["content"]
            # Clean non-printable characters and repeated excessive line breaks
            text = re.sub(r"\n{3,}", "\n\n", text)
            
            meta = self.classify_section(doc["page_number"], text)
            meta["page_number"] = doc["page_number"]

            cleaned_docs.append({
                "page_number": doc["page_number"],
                "content": text,
                "metadata": meta
            })
        return cleaned_docs
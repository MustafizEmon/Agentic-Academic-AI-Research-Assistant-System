import json
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

class StructuringAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=0.1  # Low temperature for highly analytical factual extraction
        )

    def structure_paper(self, paper_no: int, title: str, authors: str, year: str, paper_text: str) -> dict:
        # Use a truncated sample of the text if it's exceptionally long to respect LLM context tokens safely
        sample_context = paper_text[:12000] 
        #sample_context = paper_text[:20000] 
        
        prompt = f"""
        You are an elite academic peer reviewer. Analyze the following scientific paper context and extract structural components.

        PAPER DETAILS:
        Paper No: {paper_no}
        Title: {title}
        Authors: {authors}
        Year: {year}

        DOCUMENT TEXT EXCERPT:
        \"\"\"{sample_context}\"\"\"

        TASK:
        Generate a comprehensive structural breakdown of this paper. Every field must be highly detailed and academic.
        CRITICAL: If a field is not explicitly mentioned or cannot be inferred from the text excerpt, set its value to "Not specified in paper". Do not hallucinate.

        You must return strictly valid JSON matching this exact schema:
        {{
            "paper_no": {paper_no},
            "title": "{title}",
            "authors": "{authors}",
            "year": "{year}",
            "research_problem": "Detailed description of the problem the paper addresses.",
            "methodology": "Detailed description of the proposed method, network architecture, or theoretical framework.",
            "experimental_setup": "Hardware, software, baseline comparisons, or evaluation metrics configuration.",
            "datasets_used": "Names of specific datasets, clinical trials, or simulated environments.",
            "key_findings": "The core breakthroughs, quantitative metric improvements, or outcomes.",
            "strengths": "Methodological, practical, or theoretical advantages.",
            "limitations": "Flaws, assumptions, computational overhead, or scaling issues mentioned.",
            "relevance_to_query": "How this work applies to medical image segmentation under constrained or general data regimes.",
            "citation_id": "[{paper_no}]"
            "publication_venue": "Identify the conference name, journal name, or publisher abbreviation mentioned in the header, footer, or text. If not found, output 'Not found maybe, ArXiv Pre-print'."
        }}

        Do not include markdown wrappers like ```json or any introductory text. Return only the raw JSON.
        """
        
        try:
            response = self.llm.invoke(prompt)
            cleaned_text = response.content.strip().lstrip("```json").rstrip("```").strip()
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"[DEBUG] Structuring failed for Paper {paper_no}: {e}")
            # Robust fallback record guaranteeing no pipeline breaks
            return {
                "paper_no": paper_no,
                "title": title,
                "authors": authors,
                "year": year,
                "research_problem": "Failed to parse automatically.",
                "methodology": "Not specified in paper",
                "experimental_setup": "Not specified in paper",
                "datasets_used": "Not specified in paper",
                "key_findings": "Not specified in paper",
                "strengths": "Not specified in paper",
                "limitations": "Not specified in paper",
                "relevance_to_query": "Not specified in paper",
                "citation_id": f"[{paper_no}]"
            }
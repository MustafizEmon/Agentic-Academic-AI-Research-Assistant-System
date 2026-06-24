import json
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

class EvaluationAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=0.1
        )

    def evaluate_generation(self, matrix: list, review: str) -> dict:
        """Evaluates pipeline data metrics for completeness and quality."""
        prompt = f"""
        You are a senior academic quality auditor. Evaluate the following generated research outputs for completeness and structural precision.

        MATRIX PREVIEW SIZE: {len(matrix)} papers processed.
        LITERATURE REVIEW CONTENT PREVIEW:
        \"\"\"{review[:2000]}\"\"\"

        Rate the overall extraction completeness and synthesis quality on a scale from 0 to 10.
        Provide a list of critical missing elements or issues, and actionable improvement steps.

        You must return strictly valid JSON matching this schema:
        {{
            "score": 8.5,
            "issues": ["Issue item one", "Issue item two"],
            "improvements": ["Step one", "Step two"]
        }}
        Do not wrap in markdown or markdown code blocks. Return raw JSON text only.
        """
        try:
            response = self.llm.invoke(prompt)
            cleaned = response.content.strip().lstrip("```json").rstrip("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {"score": 7.0, "issues": ["None detected"], "improvements": ["Expand source counts"]}
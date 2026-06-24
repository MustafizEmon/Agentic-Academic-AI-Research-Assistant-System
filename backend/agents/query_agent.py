import json
from pydantic import BaseModel, Field
from typing import List
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

class QueryExpansionSchema(BaseModel):
    keywords: List[str] = Field(description="List of 3-5 core keywords extracted from the user prompt.")
    expanded_queries: List[str] = Field(description="3 distinct search phrases optimized for academic search engines.")
    domain: str = Field(description="Broad academic domain and sub-domain categorization.")

class QueryAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=0.2
        )

    def process_topic(self, user_topic: str) -> dict:
        prompt = f"""
        You are an expert research system engineer. Analyze the following user research topic:
        "{user_topic}"
        
        Extract core keywords, expand them into 3 high-quality academic search phrases, and identify the primary scientific domain.
        
        CRITICAL CRITERIA FOR EXPANDED QUERIES:
        - Must be flat plain text phrases (e.g., "medical image segmentation low data deep learning").
        - DO NOT include boolean operators like AND, OR, NOT.
        - DO NOT include parentheses or nested quotes.
        - Keep each phrase between 4 to 7 clean keywords.
        
        You must return strictly valid JSON matching this schema:
        {{
            "keywords": ["word1", "word2"],
            "expanded_queries": ["phrase one", "phrase two", "phrase three"],
            "domain": "Domain Name / Sub-domain"
        }}
        
        Do not include markdown wrappers like ```json or any introductory/concluding text. Only return the raw JSON block.
        """
        
        response = self.llm.invoke(prompt)
        try:
            # Clean up potential LLM code block wrappers just in case
            cleaned_text = response.content.strip().lstrip("```json").rstrip("```").strip()
            data = json.loads(cleaned_text)
            return data
        except Exception as e:
            # Fallback parsing strategy if schema verification fails
            return {
                "keywords": [w.strip() for w in user_topic.split()[:4]],
                "expanded_queries": [user_topic],
                "domain": "Computer Science / General Engineering"
            }
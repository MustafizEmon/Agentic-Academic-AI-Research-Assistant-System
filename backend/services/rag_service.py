import os
import json
import re
from config import VECTORSTORE_DIR, GROQ_API_KEY, LLM_MODEL
from langchain_groq import ChatGroq

class RAGService:
    def __init__(self):
        print("-> Initializing Resilient Pure-Python Search Matrix...")
        self.vectorstore_file = os.path.join(VECTORSTORE_DIR, "local_chunks.json")
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=0.0  # Factual response behavior
        )
        self.local_db = []
        self.load_vector_store()

    def build_vector_store(self, chunked_papers: list):
        """Processes chunks and saves them cleanly as a JSON document repository."""
        if not chunked_papers:
            print("[DEBUG] No text segments provided.")
            return

        self.local_db = []
        for paper in chunked_papers:
            for chunk in paper['chunks']:
                self.local_db.append({
                    "page_content": chunk,
                    "title": paper['title'],
                    "paper_no": paper['paper_no']
                })

        # Save to local disk directory
        with open(self.vectorstore_file, "w", encoding="utf-8") as f:
            json.dump(self.local_db, f, indent=4, ensure_ascii=False)
        print(f"-> Successfully indexed {len(self.local_db)} text segments to native database store.")

    def load_vector_store(self) -> bool:
        """Loads text database records from local storage."""
        if os.path.exists(self.vectorstore_file):
            try:
                with open(self.vectorstore_file, "r", encoding="utf-8") as f:
                    self.local_db = json.load(f)
                return True
            except Exception:
                self.local_db = []
        return False

    def _calculate_score(self, query: str, text: str) -> float:
        """Calculates structural keyword intersection density (relevance scoring)."""
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return 0.0
        text_lower = text.lower()
        score = 0.0
        for word in query_words:
            # Score points based on term occurrences
            score += text_lower.count(word)
        return score

    def answer_query(self, user_question: str) -> str:
        """Finds top relevant text segments and queries Groq within free tier token limits."""
        if not self.local_db:
            if not self.load_vector_store():
                return "The research context repository is empty. Please run the ingest pipeline first."

        # Rank all fragments based on keyword density
        scored_fragments = []
        for doc in self.local_db:
            score = self._calculate_score(user_question, doc["page_content"])
            if score > 0:
                scored_fragments.append((score, doc))

        # Sort by relevance score descending
        scored_fragments.sort(key=lambda x: x[0], reverse=True)
        
        # Pick top 2 chunks (instead of 4) to stay safely under Groq's 6,000 TPM Free Tier limits
        top_docs = [item[1] for item in scored_fragments[:2]]

        # Fallback to general first two documents if keyword density is low
        if not top_docs:
            top_docs = self.local_db[:2]

        context_blocks = []
        for d in top_docs:
            ref = f"[Paper {d['paper_no']}: {d['title']}]"
            # Protect token bounds by taking a maximum of 2500 characters per text chunk
            clean_text = d['page_content'][:2500].strip()
            context_blocks.append(f"Source Context Fragment {ref}:\n{clean_text}")

        context_string = "\n\n---\n\n".join(context_blocks)

        prompt = f"""
        You are an analytical research assistant. Answer the user's question using the provided academic snippets.

        CONTEXT EXCERPTS:
        \"\"\"{context_string}\"\"\"

        USER QUESTION:
        {user_question}

        CRITICAL OUTPUT INSTRUCTIONS:
        - Base your answer entirely on the provided fragments. Do not extrapolate.
        - Cite the accurate specific paper index using inline markers whenever stating a fact (e.g., "[Paper 1]").
        
        Write your technical answer clearly and concisely:
        """

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error querying local context window parameters: {str(e)}"
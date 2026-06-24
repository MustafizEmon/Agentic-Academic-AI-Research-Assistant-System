import os
import json
import requests
import fitz  # PyMuPDF
from config import PAPERS_DIR, METADATA_FILE

class PDFService:
    def __init__(self):
        self.papers_dir = PAPERS_DIR
        self.metadata_file = METADATA_FILE

    def download_paper_pdf(self, paper_title: str, pdf_url: str) -> str:
        """Downloads a PDF from a remote link and stores it locally."""
        if not pdf_url:
            return ""
            
        # Clean filename strings safely
        safe_title = "".join([c if c.isalnum() else "_" for c in paper_title])[:60]
        file_path = os.path.join(self.papers_dir, f"{safe_title}.pdf")
        
        # If the paper already exists locally, skip downloading
        if os.path.exists(file_path):
            return file_path
            
        try:
            headers = {"User-Agent": "AcademicAgentAssistant/1.0"}
            response = requests.get(pdf_url, headers=headers, stream=True, timeout=20)
            if response.status_code == 200 and "pdf" in response.headers.get("Content-Type", "").lower():
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return file_path
        except Exception as e:
            print(f"[DEBUG] Failed downloading PDF for {paper_title}: {e}")
        return ""

    def update_metadata_store(self, papers_list: list):
        """Persists structural information about all discovered articles locally."""
        existing_data = []
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                existing_data = []

        # Simple title-based duplicate elimination
        existing_titles = {p["title"].lower().strip() for p in existing_data}
        
        for p in papers_list:
            if p["title"].lower().strip() not in existing_titles:
                existing_data.append(p)

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Parses raw text content from local PDF files using PyMuPDF."""
        text_content = []
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
        except Exception as e:
            print(f"[DEBUG] PyMuPDF reading error on {file_path}: {e}")
            
        return "\n".join(text_content)

    def chunk_text(self, text: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> list:
        """Slices full documents into overlapping segments for RAG embeddings and context windows."""
        if not text.strip():
            return []
            
        chunks = []
        words = text.split()
        
        # Approximate dynamic sliding window based on word groupings
        step = chunk_size - chunk_overlap
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
                
        return chunks
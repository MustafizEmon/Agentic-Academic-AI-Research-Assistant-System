import os
import json
from services.pdf_service import PDFService
from agents.structuring_agent import StructuringAgent
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL

class SynthesisService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.structuring_agent = StructuringAgent()
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=0.3  # Slightly elevated for elegant academic writing rhythm
        )

    def generate_academic_table(self, local_papers_list: list) -> list:
        """Processes a list of metadata records, checks for downloaded PDFs, structures them, and aggregates a table."""
        structured_table = []
        for idx, paper in enumerate(local_papers_list, start=1):
            safe_title = "".join([c if c.isalnum() else "_" for c in paper["title"]])[:60]
            file_path = os.path.join(self.pdf_service.papers_dir, f"{safe_title}.pdf")
            
            paper_text = ""
            if os.path.exists(file_path):
                paper_text = self.pdf_service.extract_text_from_pdf(file_path)
            
            if not paper_text.strip():
                paper_text = paper.get("abstract", "No text data available.")
                
            print(f"-> Extracting structured data from Paper #{idx}: {paper['title'][:40]}...")
            
            structured_data = self.structuring_agent.structure_paper(
                paper_no=idx,
                title=paper["title"],
                authors=paper["authors"],
                year=paper["year"],
                paper_text=paper_text
            )
            structured_table.append(structured_data)
            
        return structured_table

    def generate_literature_review(self, structured_matrix: list) -> str:
        """Synthesizes the structured matrix records into a clean, concise literature review using direct facts."""
        import json
        matrix_string = json.dumps(structured_matrix, indent=2)
        
        prompt = f"""
        You are an expert academic writer. Review and cross-analyze the provided paper matrix.
        
        INPUT DATA MATRIX:
        {matrix_string}
        
        TASK:
        Write a concise, factual Literature Review using very clear, simple English vocabulary and short, direct sentence structures. 
        
        STRICT RULES:
        - Avoid long-winded, repetitive, or artificial-sounding filler sentences. 
        - Rely ONLY on the explicit facts, limitations, and findings provided in the matrix. Do not invent outside details.
        - You must use the actual paper numbers (e.g., [1], [2]) that correspond to the 'paper_no' in the matrix.
        - Keep each section punchy and short (1-2 paragraphs max per section).
        
        REQUIRED SECTIONS:
        ## 1. Introduction
        Briefly state the main problem addressed by these specific papers and their overall goal.
        
        ## 2. Thematic Grouping & Methodological Frameworks
        Group the papers by their approaches. Explain simply how each paper tackles the problem.
        
        ## 3. Comparative Analysis & Contradictions
        Directly compare their differences in datasets, bottlenecks, or performance based only on the data.
        
        ## 4. Gap Analysis & Open Challenges
        List the actual problems or missing pieces stated explicitly in the papers' limitations.
        
        ## 5. Future Research Directions
        Provide basic, realistic next steps derived directly from their listed limitations.
        
        ## 6. Conclusion
        A short wrap-up of what these papers achieve.
        
        Output clean Markdown text. Do not include any introductory or concluding conversational chat.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error synthesizing literature review automatically: {str(e)}"
        
    def generate_publication_review(self, structured_matrix: list) -> str:
        """Compiles a highly concise, on-the-point, and factual RELATED WORK paragraph section."""
        import json
        matrix_string = json.dumps(structured_matrix, indent=2)
        
        prompt = f"""
        You are an academic writer drafting a crisp, highly focused "RELATED WORK" section.
        
        INPUT ANALYSIS MATRIX:
        {matrix_string}
        
        TASK:
        Synthesize a short, dense, and completely on-the-point "RELATED WORK"  section. It must be written using simple, clear, and direct language without any decorative words or fluff.
        
        STRICT RULES:
        - Do not use abstract filler phrases or bloated AI vocabulary. Keep sentences short and active.
        - State exactly what the papers did and what their limits were using ONLY the provided text.
        - Use the exact real paper numbers (e.g., [1], [2]) matching the matrix 'paper_no'.
        - Make it brief and highly appealing by getting straight to the core technical points.
        
        STRUCTURE LOGIC (Render as 2 short, continuous paragraphs):
        - PARAGRAPH 1: Current methods used in this domain based on the papers (cite real paper numbers) and Direct comparison of their supervised or technical approaches.
        - PARAGRAPH 2: Concrete architectural limitations explicitly mentioned in the matrix data and specific technical gap left open by these papers, setting up where a new solution is needed.
        
        Output raw markdown text without markdown code blocks or conversational intros.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error synthesizing camera-ready publication section: {str(e)}"
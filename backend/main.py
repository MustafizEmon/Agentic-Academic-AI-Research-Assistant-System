import os
import shutil
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from config import PAPERS_DIR, VECTORSTORE_DIR, METADATA_FILE
from agents.query_agent import QueryAgent
from agents.evaluation_agent import EvaluationAgent
from services.retrieval_service import RetrievalService
from services.pdf_service import PDFService
from services.synthesis_service import SynthesisService
from services.rag_service import RAGService

app = FastAPI(title="Agentic Academic AI Research Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_state = {
    "status": "idle",
    "step": 0,
    "topic_meta": {},
    "papers": [],
    "matrix": [],
    "review": "",
    "publication_review": "",
    "evaluation": {}
}

class PipelineStartRequest(BaseModel):
    topic: str
    max_papers: int

class ChatRequest(BaseModel):
    question: str

@app.get("/api/state")
def get_pipeline_state():
    return pipeline_state

@app.post("/api/upload-multiple")
async def upload_multiple_papers(files: List[UploadFile] = File(...)):
    """Core Feature Upgrade: Stores and indexes bulk user-uploaded research papers."""
    try:
        pdf_service = PDFService()
        uploaded_papers = []
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            file_path = os.path.join(PAPERS_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            mock_entry = {
                "title": file.filename.replace(".pdf", "").replace("_", " ").title(),
                "authors": "Local Contributor",
                "year": "2026",
                "abstract": "User-provided local foundational paper context.",
                "url": f"local-file://{file.filename}",
                "pdf_link": "",
                "source": "Local Upload"
            }
            uploaded_papers.append(mock_entry)
            
        if uploaded_papers:
            pdf_service.update_metadata_store(uploaded_papers)
            
        return {"status": "success", "uploaded_count": len(uploaded_papers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/start")
async def start_research_pipeline(payload: PipelineStartRequest):
    global pipeline_state
    try:
        pipeline_state["status"] = "processing"
        pdf_service = PDFService()
        
        # 1. Load manually uploaded local documents first to guarantee prioritization
        local_initial_papers = []
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                try:
                    local_initial_papers = json.load(f)
                except Exception:
                    local_initial_papers = []
                    
        # Verify text readability on local uploads right away
        verified_active_papers = []
        for paper in local_initial_papers:
            safe_title = "".join([c if c.isalnum() else "_" for c in paper["title"]])[:60]
            file_path = os.path.join(pdf_service.papers_dir, f"{safe_title}.pdf")
            
            # If readable, or if it has an abstract as a structural baseline, retain it
            text_preview = pdf_service.extract_text_from_pdf(file_path) if os.path.exists(file_path) else ""
            if len(text_preview.strip()) > 200 or len(paper.get("abstract", "")) > 100:
                verified_active_papers.append(paper)
            else:
                print(f"Skipping corrupted/unreadable local file: {paper['title']}")

        # 2. Extract Keywords and Intent Expansion
        pipeline_state["step"] = 1
        q_agent = QueryAgent()
        meta = q_agent.process_topic(payload.topic)
        pipeline_state["topic_meta"] = meta

        # 3. Calculate remaining target spots based on user configuration bounds
        uploaded_count = len(verified_active_papers)
        additional_needed = max(0, payload.max_papers - uploaded_count)

        if additional_needed > 0:
            pipeline_state["step"] = 2
            retriever = RetrievalService()
            discovered_papers = retriever.execute_parallel_search(meta["expanded_queries"])
            
            pipeline_state["step"] = 3
            downloaded_count = 0
            
            # Look-ahead filter and replace loop engine
            for p in discovered_papers:
                if downloaded_count >= additional_needed:
                    break
                    
                if p.get("pdf_link"):
                    # Attempt local download
                    path = pdf_service.download_paper_pdf(p["title"], p["pdf_link"])
                    
                    if path and os.path.exists(path):
                        # Extract and check for actual academic structure right here
                        extracted_text = pdf_service.extract_text_from_pdf(path)
                        text_lower = extracted_text.lower()
                        
                        # Hard Core Indicators: Must be readable AND contain standard research sections
                        has_enough_text = len(extracted_text.strip()) > 1000
                        has_academic_structure = any(kw in text_lower for kw in ["abstract", "introduction", "conclusion", "references"])
                        is_not_lecture_note = "lecture notes" not in text_lower and "course layout" not in text_lower
                        
                        if has_enough_text and has_academic_structure and is_not_lecture_note:
                            verified_active_papers.append(p)
                            downloaded_count += 1
                            print(f"Successfully verified and added empirical research paper: {p['title'][:40]}...")
                        else:
                            # Non-empirical document, scanned copy, or textbook chapter: drop and replace
                            print(f"⚠️ Rejecting non-empirical/unreadable paper format: {p['title'][:40]}... Swapping for replacement.")
                            try:
                                os.remove(path)
                            except Exception:
                                pass

        # Slice cleanly to match the user's max budget constraints safely
        final_papers = verified_active_papers[:payload.max_papers]
        pipeline_state["papers"] = final_papers
        
        # Enforce clean structural persistence with active valid documents only
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(final_papers, f, indent=4, ensure_ascii=False)

        # Step 4: Process Multi-Document Analysis Matrix
        pipeline_state["step"] = 4
        synthesis = SynthesisService()
        matrix_data = synthesis.generate_academic_table(final_papers)
        
        # Inject the actual online link from search metrics into each matrix row matching by index
        for idx, row in enumerate(matrix_data):
            if idx < len(final_papers):
                row["online_link"] = final_papers[idx].get("url", "#")
            else:
                row["online_link"] = "#"
                
        pipeline_state["matrix"] = matrix_data

        # 5. Generate both Literature Synthesis and Publication-Ready Reviews
        pipeline_state["step"] = 5
        pipeline_state["review"] = synthesis.generate_literature_review(matrix_data)
        pipeline_state["publication_review"] = synthesis.generate_publication_review(matrix_data)

        # 6. Assemble Pure-Python High-Speed Vector Retrieval Store
        pipeline_state["step"] = 6
        rag_service = RAGService()
        chunked_payload = []
        for idx, paper in enumerate(final_papers, start=1):
            safe_title = "".join([c if c.isalnum() else "_" for c in paper["title"]])[:60]
            file_path = os.path.join(pdf_service.papers_dir, f"{safe_title}.pdf")
            text = pdf_service.extract_text_from_pdf(file_path) if os.path.exists(file_path) else paper.get("abstract", "")
            chunks = pdf_service.chunk_text(text)
            chunked_payload.append({"title": paper["title"], "paper_no": idx, "chunks": chunks})
        rag_service.build_vector_store(chunked_payload)

        # 7. Quality Assurance Loop Validation
        pipeline_state["step"] = 7
        evaluator = EvaluationAgent()
        pipeline_state["evaluation"] = evaluator.evaluate_generation(matrix_data, pipeline_state["review"])

        pipeline_state["status"] = "completed"
        return pipeline_state

    except Exception as e:
        pipeline_state["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_with_library(payload: ChatRequest):
    rag = RAGService()
    return {"answer": rag.answer_query(payload.question)}

@app.post("/api/reset")
def reset_entire_system():
    global pipeline_state
    try:
        if os.path.exists(PAPERS_DIR):
            shutil.rmtree(PAPERS_DIR)
        if os.path.exists(VECTORSTORE_DIR):
            shutil.rmtree(VECTORSTORE_DIR)
        if os.path.exists(METADATA_FILE):
            os.remove(METADATA_FILE)
            
        os.makedirs(PAPERS_DIR, exist_ok=True)
        os.makedirs(VECTORSTORE_DIR, exist_ok=True)
        
        pipeline_state = {
            "status": "idle",
            "step": 0,
            "topic_meta": {},
            "papers": [],
            "matrix": [],
            "review": "",
            "publication_review": "",
            "evaluation": {}
        }
        return {"status": "system reset completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def home():
    return {"message": "API is running..."}
import json
import os
from services.pdf_service import PDFService
from services.rag_service import RAGService

def test_rag_cycle():
    pdf_service = PDFService()
    rag_service = RAGService()

    if not os.path.exists(pdf_service.metadata_file):
        print("Metadata store missing. Run test_retrieval.py first.")
        return

    with open(pdf_service.metadata_file, "r", encoding="utf-8") as f:
        meta_papers = json.load(f)

    # Prepare chunks from the first paper we downloaded
    chunked_payload = []
    for idx, paper in enumerate(meta_papers[:2], start=1):
        safe_title = "".join([c if c.isalnum() else "_" for c in paper["title"]])[:60]
        file_path = os.path.join(pdf_service.papers_dir, f"{safe_title}.pdf")
        
        if os.path.exists(file_path):
            text = pdf_service.extract_text_from_pdf(file_path)
            chunks = pdf_service.chunk_text(text)
            chunked_payload.append({
                "title": paper["title"],
                "paper_no": idx,
                "chunks": chunks
            })

    if not chunked_payload:
        print("No local downloaded paper files available to index. Run test_retrieval.py first.")
        return

    print("\nBuilding FAISS database profile...")
    rag_service.build_vector_store(chunked_payload)

    print("\nExecuting RAG Query...")
    query = "What limitations or challenges are mentioned regarding 3D CNN architectures?"
    reply = rag_service.answer_query(query)

    print("\n" + "="*50)
    print("RAG CHATBOT CONTEXTUAL ANSWER")
    print("="*50)
    print(reply)

if __name__ == "__main__":
    test_rag_cycle()
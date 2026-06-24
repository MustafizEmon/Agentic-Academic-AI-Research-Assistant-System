import os
from agents.query_agent import QueryAgent
from services.retrieval_service import RetrievalService
from services.pdf_service import PDFService

def run_test():
    print("Step 1: Processing Query Expansion...")
    agent = QueryAgent()
    topic = "Low-data regime medical image segmentation using deep learning"
    parsed_meta = agent.process_topic(topic)
    
    print("Step 2: Harvesting Records across Free APIs...")
    retriever = RetrievalService()
    results = retriever.execute_parallel_search(parsed_meta['expanded_queries'])
    print(f"Harvested {len(results)} records.")
    
    if not results:
        print("No papers discovered to test download features.")
        return

    print("\nStep 3: Initiating Local PDF Storage Engine...")
    pdf_service = PDFService()
    
    # Let's save structural discovery items to metadata.json
    pdf_service.update_metadata_store(results)
    
    # Attempt downloading the first item containing a valid remote file stream URL
    target_paper = None
    for paper in results:
        if paper.get("pdf_link"):
            target_paper = paper
            break
            
    if target_paper:
        print(f"Attempting to pull: '{target_paper['title']}' from link: {target_paper['pdf_link']}")
        local_path = pdf_service.download_paper_pdf(target_paper['title'], target_paper['pdf_link'])
        
        if local_path and os.path.exists(local_path):
            print(f"Success! Document cached locally at: {local_path}")
            
            print("\nStep 4: Parsing text content using PyMuPDF...")
            raw_text = pdf_service.extract_text_from_pdf(local_path)
            print(f"Total extracted character content footprint: {len(raw_text)} chars.")
            
            chunks = pdf_service.chunk_text(raw_text)
            print(f"Generated {len(chunks)} contextual overlaps for Vector Storage pipeline steps.")
        else:
            print("Download skipped or link returned invalid non-PDF content header structure.")
    else:
        print("No paper returned a direct public download link this turn.")

if __name__ == "__main__":
    run_test()
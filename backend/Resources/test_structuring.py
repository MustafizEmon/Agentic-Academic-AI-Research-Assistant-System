import json
from services.pdf_service import PDFService
from services.synthesis_service import SynthesisService

def test_pipeline_structuring():
    print("Loading cached metadata profile...")
    pdf_service = PDFService()
    
    if not os.path.exists(pdf_service.metadata_file):
        print("Metadata file missing. Please run test_retrieval.py first.")
        return
        
    with open(pdf_service.metadata_file, "r", encoding="utf-8") as f:
        meta_papers = json.load(f)
        
    # Take just the top 2 papers to avoid token rate limits during testing
    test_subset = meta_papers[:2]
    print(f"Beginning LLM structuring extraction for {len(test_subset)} articles...")
    
    synthesis = SynthesisService()
    structured_matrix = synthesis.generate_academic_table(test_subset)
    
    print("\n--- TEST ROW EXTRACTION OUTPUT SUCCESS ---")
    print(json.dumps(structured_matrix[0], indent=2))

if __name__ == "__main__":
    import os
    test_pipeline_structuring()
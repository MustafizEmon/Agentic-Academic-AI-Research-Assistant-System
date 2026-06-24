import json
import os
from services.pdf_service import PDFService
from services.synthesis_service import SynthesisService

def test_full_synthesis():
    pdf_service = PDFService()
    if not os.path.exists(pdf_service.metadata_file):
        print("Metadata file missing. Please run test_retrieval.py first.")
        return
        
    with open(pdf_service.metadata_file, "r", encoding="utf-8") as f:
        meta_papers = json.load(f)
        
    test_subset = meta_papers[:2]
    synthesis = SynthesisService()
    
    print("Generating structural matrix data...")
    structured_matrix = synthesis.generate_academic_table(test_subset)
    
    print("\nSynthesizing Literature Review document via Groq...")
    lit_review = synthesis.generate_literature_review(structured_matrix)
    
    print("\n" + "="*50)
    print("GENERATED LITERATURE REVIEW PREVIEW")
    print("="*50)
    print(lit_review[:1500] + "\n\n... [Truncated for Console Preview] ...")

if __name__ == "__main__":
    test_full_synthesis()
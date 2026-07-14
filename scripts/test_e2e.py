import time
import requests
from fpdf import FPDF
import json

BASE_URL = "http://127.0.0.1:8000"

def create_sample_pdf(filepath="sample_manual.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="""
    INDUSMIND AI - INDUSTRIAL TEST MANUAL
    
    Equipment: Pump P-101
    
    Maintenance History:
    Pump P-101 failed on 2024-05-12 due to a bearing overheat.
    The bearing was replaced. 
    Routine inspection must be performed every 6 months to comply with safety regulations.
    
    Connections:
    Pump P-101 is connected to Valve A-12 and the Main Cooling System.
    
    Safety Compliance:
    Operators must wear PPE at all times when servicing Pump P-101.
    Warning: High pressure system.
    """)
    pdf.output(filepath)
    print(f"[+] Created sample PDF: {filepath}")

def run_pipeline():
    create_sample_pdf("sample_manual.pdf")
    
    # 1. Upload
    print("\n--- 1. Uploading ---")
    with open("sample_manual.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("sample_manual.pdf", f, "application/pdf")})
    assert res.status_code == 200, res.text
    data = res.json()
    doc_id = data["data"]["document_id"]
    print(f"[+] Uploaded successfully. Doc ID: {doc_id}")
    
    # 2. Process
    print("\n--- 2. Processing (OCR/Text Extraction) ---")
    res = requests.post(f"{BASE_URL}/api/v1/documents/{doc_id}/process")
    assert res.status_code == 200, res.text
    print("[+] Processed successfully.")
    
    # 3. Embed
    print("\n--- 3. Embedding (ChromaDB) ---")
    res = requests.post(f"{BASE_URL}/api/v1/documents/{doc_id}/embed")
    assert res.status_code == 200, res.text
    print(f"[+] Embedded successfully. Chunks generated: {res.json()['data']['chunks_processed']}")
    
    # 4. Build Graph
    print("\n--- 4. Building Knowledge Graph (Neo4j) ---")
    res = requests.post(f"{BASE_URL}/api/v1/graph/build/{doc_id}")
    assert res.status_code == 200, res.text
    print(f"[+] Graph built successfully. Graph nodes added.")
    
    # 5. System Status
    print("\n--- 5. System Status Verification ---")
    res = requests.get(f"{BASE_URL}/api/v1/system/status")
    assert res.status_code == 200, res.text
    stats = res.json()["data"]
    print(json.dumps(stats, indent=2))
    assert stats["chromadb"] == "connected"
    
    # 6. Chat API - Route 1: Search
    print("\n--- 6a. Chat: Simple Search ---")
    payload = {"question": "What is Pump P-101?", "conversation_id": "test-run-1"}
    res = requests.post(f"{BASE_URL}/api/v1/chat/", json=payload)
    print(json.dumps(res.json(), indent=2))
    
    # 6. Chat API - Route 2: Maintenance
    print("\n--- 6b. Chat: Maintenance History ---")
    payload = {"question": "Show maintenance history for Pump P-101.", "conversation_id": "test-run-1"}
    res = requests.post(f"{BASE_URL}/api/v1/chat/", json=payload)
    print(json.dumps(res.json(), indent=2))
    
    # 6. Chat API - Route 3: Compliance
    print("\n--- 6c. Chat: Compliance Rules ---")
    payload = {"question": "Which regulation applies?", "conversation_id": "test-run-1"}
    res = requests.post(f"{BASE_URL}/api/v1/chat/", json=payload)
    print(json.dumps(res.json(), indent=2))
    
    print("\n[SUCCESS] Entire pipeline ran correctly!")

if __name__ == "__main__":
    run_pipeline()

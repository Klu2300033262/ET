import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.config.constants import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_document_text(text: str) -> List[Dict[str, Any]]:
    """
    Intelligently chunks normalized text.
    Uses RecursiveCharacterTextSplitter to ensure paragraphs, tables, 
    and equipment IDs (which lack splitting characters) stay together.
    """
    # Initialize the recursive splitter
    # The default separators ["\n\n", "\n", " ", ""] already prioritize keeping paragraphs and lines intact.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
        strip_whitespace=True
    )
    
    # Split the text into Document objects
    langchain_docs = splitter.create_documents([text])
    
    structured_chunks = []
    
    for i, doc in enumerate(langchain_docs):
        content = doc.page_content
        start_index = doc.metadata.get("start_index", 0)
        end_index = start_index + len(content)
        word_count = len(content.split())
        
        chunk_data = {
            "chunk_id": str(uuid.uuid4()),
            "chunk_number": i + 1,
            "start_offset": start_index,
            "end_offset": end_index,
            "character_count": len(content),
            "word_count": word_count,
            "content": content
        }
        structured_chunks.append(chunk_data)
        
    return structured_chunks

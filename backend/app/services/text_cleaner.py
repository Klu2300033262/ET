import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalizes unicode, quotes, dashes, and tabs.
    Crucially, it leaves standard ASCII characters intact so engineering IDs (e.g. Valve_A12) remain unchanged.
    """
    # Normalize unicode to NFKC
    text = unicodedata.normalize('NFKC', text)
    
    # Normalize quotes
    text = re.sub(r'[“”]', '"', text)
    text = re.sub(r'[‘’]', "'", text)
    
    # Normalize dashes (em-dash, en-dash to hyphen)
    text = re.sub(r'[—–]', '-', text)
    
    # Convert tabs to spaces
    text = text.replace('\t', ' ')
    
    return text

def clean_extracted_text(text: str) -> str:
    """
    Applies heuristics to remove artifacts like duplicate spaces, page numbers, and headers,
    while preserving paragraph structures, tables, and lists.
    """
    text = normalize_text(text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    # Regex for common page numbers (e.g., "Page 1", "- 12 -", or standalone numbers)
    page_num_regex = re.compile(r'^\s*(Page\s*\d+|[-]\s*\d+\s*[-]|^\d+$)\s*$', re.IGNORECASE)
    
    for line in lines:
        stripped_line = line.strip()
        
        # Skip empty lines but preserve them as paragraph breaks later
        if not stripped_line:
            cleaned_lines.append("")
            continue
            
        # Remove standalone page numbers
        if page_num_regex.match(stripped_line):
            continue
            
        # Clean multiple spaces within the line
        line_cleaned = re.sub(r' {2,}', ' ', stripped_line)
        cleaned_lines.append(line_cleaned)

    # Rejoin lines.
    # We want to remove unnecessary line breaks inside paragraphs, but keep line breaks for lists and tables.
    # A heuristic: if a line doesn't end with punctuation and the next line doesn't start with a bullet/number, they might be part of the same paragraph.
    # For robust chunking, it's safer to just condense multiple blank lines into double blank lines (paragraph breaks).
    
    joined_text = "\n".join(cleaned_lines)
    
    # Condense 3+ newlines into 2 newlines
    joined_text = re.sub(r'\n{3,}', '\n\n', joined_text)
    
    return joined_text.strip()

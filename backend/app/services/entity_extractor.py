import re
import logging
import spacy
from typing import List, Dict, Any
from backend.app.models.graph import GraphEntity, Offset

logger = logging.getLogger("indusmind-ai")

# Fallback Keyword Dictionary
INDUSTRIAL_KEYWORDS = {
    "Equipment": ["Pump", "Valve", "Motor", "Boiler", "Pipe", "Compressor", "Turbine", "Sensor"],
    "Department": ["Maintenance", "Engineering", "Safety", "Operations", "Compliance"],
    "Procedure": ["Inspection", "Maintenance", "Safety Procedure", "Lockout Tagout"]
}

def is_english_ascii(s: str) -> bool:
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

class EntityExtractor:
    """
    Modular 4-Tier Entity Extraction Pipeline.
    Designed so Stage 7 can easily inject an LLM extractor module here.
    """
    def __init__(self):
        self.nlp = None
        self._load_spacy()
        
        # Regex for common industrial IDs (e.g., P-101, Valve A-12, XJ-4420)
        self.id_pattern = re.compile(r'\b(?:[A-Za-z]+[- ]?[A-Z0-9]+)\b')

    def _load_spacy(self):
        try:
            # We use the free, offline small core web model for fast NER
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy NLP model: en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Will rely on Regex and Keywords.")
            self.nlp = None

    def _resolve_icon(self, ent_type: str) -> str:
        """Maps an entity type to a generic icon alias for the React Dashboard."""
        icon_map = {
            "Equipment/Component": "pump",
            "Equipment/ID": "settings",
            "Technician": "user",
            "Date": "calendar",
            "Department": "briefcase",
            "Procedure": "file-text"
        }
        return icon_map.get(ent_type, "circle")

    def extract_entities(self, text: str, chunk_id: str, document_id: str) -> List[GraphEntity]:
        """Runs the chunk through the multi-tier extraction pipeline."""
        entities = []
        extracted_spans = set() # To prevent overlapping duplicate extractions within the same offset

        # TIER 1: spaCy NER Extraction
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # Map standard spaCy labels to industrial concepts if possible
                ent_type = "Entity"
                if ent.label_ in ["ORG", "PRODUCT"]:
                    ent_type = "Equipment/Component"
                elif ent.label_ == "PERSON":
                    ent_type = "Technician"
                elif ent.label_ == "DATE":
                    ent_type = "Date"
                    
                if ent.label_ not in ["CARDINAL", "ORDINAL"]: # Ignore raw numbers
                    ent_text = ent.text.strip()
                    if not is_english_ascii(ent_text):
                        continue
                    entities.append(GraphEntity(
                        entity=ent_text,
                        type=ent_type,
                        icon=self._resolve_icon(ent_type),
                        confidence=0.85, # Base heuristic confidence for spaCy
                        source_chunk=chunk_id,
                        source_document=document_id,
                        offset=Offset(start=ent.start_char, end=ent.end_char)
                    ))
                    extracted_spans.add((ent.start_char, ent.end_char))

        # TIER 2: Regex Industrial ID Extraction
        for match in self.id_pattern.finditer(text):
            start, end = match.span()
            matched_text = match.group().strip()
            
            # Simple heuristic: must have at least one digit to be a complex industrial ID
            if any(char.isdigit() for char in matched_text):
                if not is_english_ascii(matched_text):
                    continue
                # Ensure we don't overlap with spaCy extractions
                if not any(s <= start and end <= e for s, e in extracted_spans):
                    entities.append(GraphEntity(
                        entity=matched_text,
                        type="Equipment/ID",
                        icon=self._resolve_icon("Equipment/ID"),
                        confidence=0.92, # High confidence for explicit pattern matches
                        source_chunk=chunk_id,
                        source_document=document_id,
                        offset=Offset(start=start, end=end)
                    ))
                    extracted_spans.add((start, end))

        # TIER 3: Keyword Dictionary Extraction
        lower_text = text.lower()
        for category, keywords in INDUSTRIAL_KEYWORDS.items():
            for kw in keywords:
                kw_lower = kw.lower()
                start_idx = 0
                while True:
                    idx = lower_text.find(kw_lower, start_idx)
                    if idx == -1:
                        break
                    
                    end_idx = idx + len(kw_lower)
                    if not any(s <= idx and end_idx <= e for s, e in extracted_spans):
                        entities.append(GraphEntity(
                            entity=text[idx:end_idx], # Preserve original casing
                            type=category,
                            icon=self._resolve_icon(category),
                            confidence=0.75, # Lower confidence for raw keyword matching
                            source_chunk=chunk_id,
                            source_document=document_id,
                            offset=Offset(start=idx, end=end_idx)
                        ))
                        extracted_spans.add((idx, end_idx))
                    start_idx = end_idx

        # TIER 4: Entity Normalization (Deduplication within chunk)
        # In a real app, 'Valve A' and 'valve a' should resolve to the same node ID, 
        # but here we just ensure we didn't duplicate exact exact offsets.
        return self._normalize_entities(entities)

    def _normalize_entities(self, entities: List[GraphEntity]) -> List[GraphEntity]:
        """Cleans and normalizes strings. (e.g., stripping trailing commas)"""
        for e in entities:
            e.entity = e.entity.strip(".,;:()[]{}").title()
        return entities

# Global Singleton
entity_extractor = EntityExtractor()

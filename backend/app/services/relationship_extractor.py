import logging
from typing import List
from backend.app.models.graph import GraphEntity, GraphRelationship

logger = logging.getLogger("indusmind-ai")

# Heuristic relationship mapping based on intervening signal words
RELATIONSHIP_SIGNALS = {
    "LOCATED_IN": ["located in", "installed in", "situated at", "found in"],
    "CONNECTED_TO": ["connected to", "attached to", "linked to", "wired to", "piped to"],
    "MAINTAINED_BY": ["maintained by", "serviced by", "repaired by"],
    "HAS_FAILURE": ["failed due to", "failure", "fault", "broken", "leak", "overheat"],
    "REQUIRES": ["requires", "needs", "must use"],
    "PART_OF": ["part of", "component of", "inside"]
}

class RelationshipExtractor:
    """
    Infers relationships between extracted entities based on text proximity and signal words.
    Designed so Stage 7 can swap this out for a pure LangGraph LLM extractor later.
    """
    
    def extract_relationships(self, text: str, entities: List[GraphEntity]) -> List[GraphRelationship]:
        relationships = []
        
        # We need at least 2 entities in a chunk to infer a relationship
        if len(entities) < 2:
            return relationships
            
        # Sort entities by their occurrence in the text
        sorted_ents = sorted(entities, key=lambda e: e.offset.start)
        
        lower_text = text.lower()
        
        # Sliding window proximity check
        for i in range(len(sorted_ents) - 1):
            ent_a = sorted_ents[i]
            ent_b = sorted_ents[i+1]
            
            # Extract the text between the two entities
            intervening_text = lower_text[ent_a.offset.end : ent_b.offset.start].strip()
            
            # If they are too far apart, assume they aren't directly related in this sentence
            if len(intervening_text) > 100:
                continue
                
            relationship_type = "RELATED_TO" # Default fallback
            confidence = 0.50
            
            # Check for strong signal words
            for rel_type, signals in RELATIONSHIP_SIGNALS.items():
                if any(signal in intervening_text for signal in signals):
                    relationship_type = rel_type
                    confidence = 0.88 # High confidence due to explicit signal word
                    break
                    
            # If no signal words, use basic type-based inference (Industrial Rules)
            if relationship_type == "RELATED_TO":
                if "Equipment" in ent_a.type and "Department" in ent_b.type:
                    relationship_type = "MAINTAINED_BY"
                    confidence = 0.70
                elif "Equipment" in ent_a.type and "Fault" in ent_b.type:
                    relationship_type = "HAS_FAILURE"
                    confidence = 0.70
            
            relationships.append(GraphRelationship(
                source=ent_a.entity,
                relationship=relationship_type,
                target=ent_b.entity,
                confidence=confidence
            ))
            
        return relationships

# Global Singleton
relationship_extractor = RelationshipExtractor()

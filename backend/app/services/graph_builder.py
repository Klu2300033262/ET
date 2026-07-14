import os
import json
import logging
from typing import Dict, Any
from backend.app.services.neo4j_service import neo4j_db
from backend.app.services.entity_extractor import entity_extractor
from backend.app.services.relationship_extractor import relationship_extractor
from backend.app.models.graph import GraphExtractionResult

logger = logging.getLogger("indusmind-ai")

class GraphBuilderService:
    """
    Orchestrates the conversion of Stage 4 chunks into Neo4j Knowledge Graph elements.
    """
    
    def build_graph_from_document(self, document_id: str) -> GraphExtractionResult:
        """Reads a document's chunk payload, extracts relationships, and merges into Neo4j."""
        chunks_json_path = os.path.join("data", "processed", "chunks", document_id, "chunks.json")
        
        if not os.path.exists(chunks_json_path):
            raise FileNotFoundError(f"Missing chunk payload for {document_id}. Has Stage 4 completed?")
            
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
            
        chunks = payload.get("chunks", [])
        
        result = GraphExtractionResult(document_id=document_id)
        
        logger.info(f"[{document_id}] Lifecycle: Graph Build Started. Analyzing {len(chunks)} chunks...")
        
        # 1. Extraction Pipeline
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            text = chunk["content"]
            
            # Extract Entities
            entities = entity_extractor.extract_entities(text, chunk_id, document_id)
            result.entities.extend(entities)
            
            # Extract Relationships
            relationships = relationship_extractor.extract_relationships(text, entities)
            result.relationships.extend(relationships)
            
        logger.info(f"[{document_id}] Extraction complete: {len(result.entities)} Entities, {len(result.relationships)} Relationships found.")
        
        # 2. Database Insertion (if online)
        if neo4j_db.is_online():
            logger.info(f"[{document_id}] Lifecycle: Neo4j Insert Started...")
            self._merge_into_neo4j(result)
            logger.info(f"[{document_id}] Lifecycle: Neo4j Insert Finished.")
        else:
            logger.warning(f"[{document_id}] Neo4j is offline. Extraction completed but NOT saved to database.")
            
        logger.info(f"[{document_id}] Lifecycle: Graph Build Completed.")
        return result

    def _merge_into_neo4j(self, result: GraphExtractionResult):
        """Executes safe MERGE operations into Neo4j to avoid graph duplication."""
        
        # Cypher for Nodes
        # We MERGE on the entity name and type. We update the source_chunk metadata
        # to ensure it points back to the Vector DB for GraphRAG.
        node_query = """
        UNWIND $entities AS ent
        MERGE (n:IndustrialNode {name: ent.entity, type: ent.type})
        SET n.confidence = ent.confidence,
            n.document_id = ent.document_id,
            n.source_chunk = ent.source_chunk
        """
        
        # Convert Pydantic to dicts for Neo4j driver
        ent_dicts = [e.model_dump() for e in result.entities]
        
        if ent_dicts:
            neo4j_db.execute_write(node_query, {"entities": ent_dicts})
            
        # Cypher for Relationships
        # We must iterate since dynamic relationship types (rel.relationship) can't be parameterized directly in MERGE
        for rel in result.relationships:
            # We sanitize the relationship type to ensure valid Cypher syntax (e.g. no spaces)
            rel_type = rel.relationship.upper().replace(" ", "_")
            
            edge_query = f"""
            MATCH (a:IndustrialNode {{name: $source}})
            MATCH (b:IndustrialNode {{name: $target}})
            MERGE (a)-[r:{rel_type}]->(b)
            SET r.confidence = $confidence
            """
            
            neo4j_db.execute_write(edge_query, {
                "source": rel.source,
                "target": rel.target,
                "confidence": rel.confidence
            })

# Global singleton
graph_builder = GraphBuilderService()

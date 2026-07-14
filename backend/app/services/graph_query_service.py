import logging
from typing import Dict, Any, List
from backend.app.services.neo4j_service import neo4j_db
from backend.app.models.graph import GraphQueryResponse

logger = logging.getLogger("indusmind-ai")

class GraphQueryService:
    """Provides reusable graph queries without exposing Cypher directly to the frontend/APIs."""
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Returns the total volume metrics of the Neo4j Graph."""
        if not neo4j_db.is_online():
            return {"status": "offline", "nodes": 0, "relationships": 0}
            
        node_query = "MATCH (n:IndustrialNode) RETURN count(n) as node_count"
        edge_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
        
        nodes = neo4j_db.execute_read(node_query)
        edges = neo4j_db.execute_read(edge_query)
        
        return {
            "status": "online",
            "nodes": nodes[0]["node_count"] if nodes else 0,
            "relationships": edges[0]["rel_count"] if edges else 0
        }

    def execute_custom_query(self, cypher: str, parameters: Dict[str, Any] = None) -> GraphQueryResponse:
        """Executes a Cypher query and formats the result for React Visualization (Nodes/Edges array)."""
        if not neo4j_db.is_online():
            return GraphQueryResponse(nodes=[], edges=[], statistics=self.get_database_statistics())
            
        results = neo4j_db.execute_read(cypher, parameters)
        return self._format_for_frontend(results)

    def find_all_equipment(self) -> GraphQueryResponse:
        """Finds all core hardware entities."""
        query = """
        MATCH (n:IndustrialNode)
        WHERE n.type CONTAINS 'Equipment' OR n.type = 'Machine' OR n.type = 'Pump'
        RETURN n
        LIMIT 100
        """
        return self.execute_custom_query(query)
        
    def find_connected_components(self, entity_name: str) -> GraphQueryResponse:
        """Finds all nodes within a 2-hop radius of a specific component."""
        query = """
        MATCH path = (n:IndustrialNode {name: $entity_name})-[*1..2]-(m)
        RETURN path
        """
        return self.execute_custom_query(query, {"entity_name": entity_name})

    def _format_for_frontend(self, neo4j_results: List[Dict[str, Any]]) -> GraphQueryResponse:
        """
        Translates raw Neo4j Paths/Nodes/Relationships into a standard
        {nodes: [...], edges: [...]} JSON topology consumed by React libraries (like vis.js).
        """
        nodes_dict = {}
        edges_dict = {}
        
        for record in neo4j_results:
            # Result could be a node ('n') or a path ('path')
            for key, value in record.items():
                if hasattr(value, "nodes") and hasattr(value, "relationships"): # It's a Path
                    for node in value.nodes:
                        n_id = str(node.element_id)
                        nodes_dict[n_id] = {"id": n_id, "label": node.get("name"), "category": node.get("type"), "properties": dict(node)}
                    for rel in value.relationships:
                        e_id = str(rel.element_id)
                        edges_dict[e_id] = {"id": e_id, "source": str(rel.start_node.element_id), "target": str(rel.end_node.element_id), "label": rel.type}
                elif hasattr(value, "labels"): # It's a single Node
                    n_id = str(value.element_id)
                    nodes_dict[n_id] = {"id": n_id, "label": value.get("name"), "category": value.get("type"), "properties": dict(value)}

        return GraphQueryResponse(
            nodes=list(nodes_dict.values()),
            edges=list(edges_dict.values()),
            statistics={"total_returned": len(nodes_dict)}
        )

# Global Singleton
graph_query = GraphQueryService()

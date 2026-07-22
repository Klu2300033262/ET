import logging
from typing import Dict, Any, List
from backend.app.services.neo4j_service import neo4j_db
from backend.app.models.graph import GraphQueryResponse

logger = logging.getLogger("indusmind-ai")

class GraphQueryService:
    """Provides reusable graph queries without exposing Cypher directly to the frontend/APIs."""
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Returns detailed volume metrics and distributions of the Neo4j Graph."""
        if not neo4j_db.is_online():
            return {
                "status": "offline", 
                "nodes": 0, 
                "relationships": 0,
                "entity_types": [],
                "relationship_types": [],
                "average_degree": 0.0
            }
            
        node_query = "MATCH (n:IndustrialNode) RETURN count(n) as node_count"
        edge_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
        
        # Aggregations for dashboard widgets
        entity_types_query = "MATCH (n:IndustrialNode) RETURN n.type as type, count(n) as count ORDER BY count DESC"
        rel_types_query = "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC"
        avg_degree_query = "MATCH (n:IndustrialNode) OPTIONAL MATCH (n)-[r]-() WITH n, count(r) as degree RETURN avg(degree) as avg_degree"
        
        nodes = neo4j_db.execute_read(node_query)
        edges = neo4j_db.execute_read(edge_query)
        entity_types = neo4j_db.execute_read(entity_types_query)
        rel_types = neo4j_db.execute_read(rel_types_query)
        avg_degree = neo4j_db.execute_read(avg_degree_query)
        
        return {
            "status": "online",
            "nodes": nodes[0]["node_count"] if nodes else 0,
            "relationships": edges[0]["rel_count"] if edges else 0,
            "entity_types": entity_types,
            "relationship_types": rel_types,
            "average_degree": round(avg_degree[0]["avg_degree"] or 0.0, 2)
        }

    def execute_custom_query(self, cypher: str, parameters: Dict[str, Any] = None) -> GraphQueryResponse:
        """Executes a Cypher query and formats the result for React Visualization (Nodes/Edges array)."""
        if not neo4j_db.is_online():
            return GraphQueryResponse(nodes=[], edges=[], statistics=self.get_database_statistics())
            
        results = neo4j_db.execute_read_raw(cypher, parameters)
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

    def _format_for_frontend(self, neo4j_results: List[Any]) -> GraphQueryResponse:
        """
        Translates raw Neo4j Paths/Nodes/Relationships into a standard
        {nodes: [...], edges: [...]} JSON topology consumed by React libraries (like vis.js).
        """
        nodes_dict = {}
        edges_dict = {}
        
        for record in neo4j_results:
            # Result could be a node ('n'), path ('path'), or relationship ('r')
            for key, value in record.items():
                if not value:
                    continue
                # 1. Path
                if hasattr(value, "nodes") and hasattr(value, "relationships"):
                    for node in value.nodes:
                        n_id = str(node.element_id)
                        nodes_dict[n_id] = {"id": n_id, "label": node.get("name"), "category": node.get("type"), "properties": dict(node)}
                    for rel in value.relationships:
                        e_id = str(rel.element_id)
                        edges_dict[e_id] = {"id": e_id, "source": str(rel.start_node.element_id), "target": str(rel.end_node.element_id), "label": rel.type}
                # 2. Node
                elif hasattr(value, "labels"):
                    n_id = str(value.element_id)
                    nodes_dict[n_id] = {"id": n_id, "label": value.get("name"), "category": value.get("type"), "properties": dict(value)}
                # 3. Relationship
                elif hasattr(value, "start_node") and hasattr(value, "end_node"):
                    e_id = str(value.element_id)
                    edges_dict[e_id] = {"id": e_id, "source": str(value.start_node.element_id), "target": str(value.end_node.element_id), "label": value.type}

        return GraphQueryResponse(
            nodes=list(nodes_dict.values()),
            edges=list(edges_dict.values()),
            statistics={"total_returned": len(nodes_dict)}
        )

# Global Singleton
graph_query = GraphQueryService()

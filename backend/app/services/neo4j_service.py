import os
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, exceptions
from dotenv import load_dotenv

logger = logging.getLogger("indusmind-ai")
load_dotenv()

class Neo4jService:
    """
    Core connection service for Neo4j AuraDB. 
    Handles connection pooling, transactions, and graceful degradation.
    """
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "")
        self.user = os.getenv("NEO4J_USERNAME", "")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.driver = None
        self._connect()

    def _connect(self):
        """Attempts to establish connection to AuraDB."""
        if not self.uri or not self.user or not self.password:
            logger.warning("Neo4j Credentials missing in .env. Graph Database is currently OFFLINE.")
            return

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password), connection_timeout=5.0)
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j AuraDB.")
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j. Check URI and network. Error: {e}")
            self.driver = None
        except exceptions.AuthError as e:
            logger.error(f"Failed to connect to Neo4j. Invalid credentials. Error: {e}")
            self.driver = None
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j. Database is offline. Error: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def is_online(self) -> bool:
        return self.driver is not None

    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Executes a write transaction safely."""
        if not self.is_online():
            logger.warning("Attempted Neo4j write while DB is offline.")
            return None
            
        try:
            with self.driver.session() as session:
                result = session.execute_write(self._execute_tx, query, parameters)
                return result
        except Exception as e:
            logger.error(f"Neo4j Write Transaction Failed: {e}")
            raise

    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a read transaction safely and returns a list of dictionaries."""
        if not self.is_online():
            logger.warning("Attempted Neo4j read while DB is offline.")
            return []
            
        try:
            with self.driver.session() as session:
                result = session.execute_read(self._execute_tx, query, parameters)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Neo4j Read Transaction Failed: {e}")
            raise

    @staticmethod
    def _execute_tx(tx, query: str, parameters: Optional[Dict[str, Any]] = None):
        """Internal transaction execution wrapper."""
        result = tx.run(query, parameters or {})
        return result.data()

# Global Singleton
neo4j_db = Neo4jService()

from fastapi import Depends
from backend.app.config.settings import Settings, settings

# Placeholder for dependency injection framework
# For example, injecting Neo4j sessions or ChromaDB clients

def get_settings() -> Settings:
    """Dependency injection for application settings."""
    return settings

import re
from typing import Any, Dict

def sanitize_filename(filename: str) -> str:
    """Removes unsafe characters from a filename."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def merge_metadata(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merges two metadata dictionaries gracefully."""
    merged = base.copy()
    for key, value in updates.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_metadata(merged[key], value)
        else:
            merged[key] = value
    return merged

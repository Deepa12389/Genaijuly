"""
small helper functions for the applciation
"""

def task_doc_to_response(doc: dict) -> dict:
    """
    MongoDB documents use `_id` (an ObjectId). Our API responses need a
    plain string `id`. This function converts one to the other.
    """
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "description": doc.get("description", ""),
        "status": doc["status"],
        "priority": doc["priority"],
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }
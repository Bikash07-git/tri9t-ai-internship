from pydantic import BaseModel
from typing import List, Optional

# --- BROWSE SCHEMAS ---
class NodeResponse(BaseModel):
    id: int
    heading: Optional[str] = None
    level: str
    body_text: Optional[str] = None
    logical_node_id: str
    content_hash: str
    parent_id: Optional[int] = None
    
    # This empty list will hold any child subsections!
    children: List['NodeResponse'] = [] 

    class Config:
        from_attributes = True

# This line is a Pydantic requirement when a model refers to itself (children)
NodeResponse.model_rebuild()

# --- SELECTION SCHEMAS ---
class SelectionCreate(BaseModel):
    name: str
    node_ids: List[int]
    version_id: int

class SelectionResponse(BaseModel):
    id: int
    name: str
    node_ids: str
    version_id: int

    class Config:
        from_attributes = True
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String, unique=True) # e.g., "v1" or "v2"
    
    # Links this version to all its nodes
    nodes = relationship("DocumentNode", back_populates="version")

class DocumentNode(Base):
    __tablename__ = "document_nodes"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("document_versions.id"))
    
    # This is for the tree structure. A node can have a parent (like a subsection belonging to a section)
    parent_id = Column(Integer, ForeignKey("document_nodes.id"), nullable=True)
    
    # This identifier stays the SAME across v1 and v2 so we know they are the same logical section
    logical_node_id = Column(String, index=True) 
    
    heading = Column(String)
    level = Column(String) # e.g., "H1", "H2", "Paragraph"
    body_text = Column(Text)
    
    # A digital fingerprint of the text. If the text changes in v2, the hash changes.
    content_hash = Column(String) 

    version = relationship("DocumentVersion", back_populates="nodes")

class Selection(Base):
    __tablename__ = "selections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    
    # We will store the list of IDs as a simple comma-separated string (e.g., "1,4,5")
    node_ids = Column(String) 
    
    # Selections must be "version-pinned" according to the assignment
    version_id = Column(Integer, ForeignKey("document_versions.id"))
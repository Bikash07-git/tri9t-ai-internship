import fitz
import hashlib
import re
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def generate_hash(text: str) -> str:
    """Creates a digital fingerprint of the text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def identify_level(text: str, font_size: float) -> str:
    """Guess the level based on numbering and font size."""
    text = text.strip()
    # Matches "1.", "2.", etc.
    if re.match(r'^\d+\.\s', text) or font_size > 14:
        return "H1"
    # Matches "1.1", "2.1", etc.
    elif re.match(r'^\d+\.\d+\s', text) or font_size > 12:
        return "H2"
    # Matches "2.1.1.1", etc.
    elif re.match(r'^\d+\.\d+\.\d+', text):
        return "H3"
    else:
        return "Paragraph"

def parse_and_ingest(pdf_path: str, version_name: str):
    db: Session = SessionLocal()
    
    # 1. Create the Document Version
    db_version = models.DocumentVersion(version_name=version_name)
    db.add(db_version)
    db.commit()
    db.refresh(db_version)

    doc = fitz.open(pdf_path)
    
    # This keeps track of the current parent for H1, H2, H3
    # e.g., current_parents["H1"] = node_id
    current_parents = {"H1": None, "H2": None, "H3": None}
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                # Combine all text in a block to form a full paragraph or heading
                block_text = ""
                max_font_size = 0
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span['text'] + " "
                        if span['size'] > max_font_size:
                            max_font_size = span['size']
                
                block_text = block_text.strip()
                if not block_text:
                    continue
                
                level = identify_level(block_text, max_font_size)
                content_hash = generate_hash(block_text)
                
                # Determine Parent ID
                parent_id = None
                if level == "H2":
                    parent_id = current_parents["H1"]
                elif level == "H3":
                    parent_id = current_parents["H2"] or current_parents["H1"]
                elif level == "Paragraph":
                    # Paragraph belongs to the deepest current heading
                    parent_id = current_parents["H3"] or current_parents["H2"] or current_parents["H1"]

                # Create the node
                # We use a simplified logical_node_id based on the heading text/numbering for now
                node = models.DocumentNode(
                    version_id=db_version.id,
                    parent_id=parent_id,
                    logical_node_id=block_text[:20].strip(), # Simplified for tutorial
                    heading=block_text if "H" in level else None,
                    level=level,
                    body_text=block_text if level == "Paragraph" else None,
                    content_hash=content_hash
                )
                
                db.add(node)
                db.commit()
                db.refresh(node)
                
                # Update the stack if it's a heading
                if "H" in level:
                    current_parents[level] = node.id
                    # Clear deeper levels
                    if level == "H1":
                        current_parents["H2"] = None
                        current_parents["H3"] = None
                    elif level == "H2":
                        current_parents["H3"] = None

    print(f"Successfully ingested {version_name} into the database!")
    db.close()

if __name__ == "__main__":
    parse_and_ingest("data/ct200_manual.pdf", "v1")
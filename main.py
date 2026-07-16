import json
import nosql_db


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import SessionLocal, engine

# Ensure database tables are created
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tri9T Document API")

# Dependency: This opens a database session for a request and closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/nodes/top-level", response_model=List[schemas.NodeResponse])
def get_top_level_sections(db: Session = Depends(get_db)):
    """Fetch all top-level (H1) sections for the latest version."""
    # We filter where level is "H1"
    nodes = db.query(models.DocumentNode).filter(models.DocumentNode.level == "H1").all()
    return nodes

@app.get("/nodes/{node_id}", response_model=schemas.NodeResponse)
def get_node_by_id(node_id: int, db: Session = Depends(get_db)):
    """Fetch a specific node by its exact ID."""
    node = db.query(models.DocumentNode).filter(models.DocumentNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@app.get("/nodes/{node_id}", response_model=schemas.NodeResponse)
def get_node_by_id(node_id: int, db: Session = Depends(get_db)):
    """Fetch a specific node by its exact ID, including its children."""
    node = db.query(models.DocumentNode).filter(models.DocumentNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Manually fetch the children and attach them to the node object
    children = db.query(models.DocumentNode).filter(models.DocumentNode.parent_id == node_id).all()
    node.children = children
    
    return node

@app.post("/selections/", response_model=schemas.SelectionResponse)
def create_selection(selection: schemas.SelectionCreate, db: Session = Depends(get_db)):
    """Creates a version-pinned selection of nodes."""
    
    # Convert the Python list of integers [1, 2, 3] into a string "1,2,3" for SQLite
    ids_string = ",".join(map(str, selection.node_ids))
    
    new_selection = models.Selection(
        name=selection.name,
        node_ids=ids_string,
        version_id=selection.version_id
    )
    
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)
    
    return new_selection





def mock_llm_call(prompt: str) -> dict:
    """
    Simulates a structured JSON response from an LLM.
    Later, you will replace this with an actual call to Gemini or Groq.
    """
    print("Sending prompt to Mock LLM...")
    # Simulating a perfect, structured JSON output
    mock_response = {
        "test_cases": [
            {
                "description": "Simulate overpressure condition",
                "steps": "1. Power on device. 2. Artificially block cuff to force pressure above 299 mmHg.",
                "expected_result": "Device should display E3 and auto-deflate."
            },
            {
                "description": "Test low battery indication",
                "steps": "1. Insert batteries depleted below 10% capacity. 2. Power on device.",
                "expected_result": "Device displays low-battery icon."
            }
        ]
    }
    return mock_response

@app.post("/generate/{selection_id}")
def generate_test_cases(selection_id: int, db: Session = Depends(get_db)):
    """Fetches a selection, reconstructs the text, calls the LLM, and saves the output."""
    
    # 1. Get the selection
    selection = db.query(models.Selection).filter(models.Selection.id == selection_id).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection not found")
        
    # 2. Reconstruct the text
    node_ids = [int(id.strip()) for id in selection.node_ids.split(",")]
    combined_text = ""
    for n_id in node_ids:
        node = db.query(models.DocumentNode).filter(models.DocumentNode.id == n_id).first()
        if node:
            if node.heading:
                combined_text += f"\n\n{node.heading}\n"
            if node.body_text:
                combined_text += f"{node.body_text}\n"
                
    if not combined_text.strip():
        raise HTTPException(status_code=400, detail="Selected nodes contain no text.")

    # 3. Formulate the Prompt
    prompt = f"""
    You are an expert QA engineer for medical devices. 
    Based on the following manual extract, generate 2 specific QA test cases.
    Each test case must include steps and an expected result.
    
    Manual Extract:
    {combined_text}
    """
    
    # 4. Call the (Mock) LLM
    try:
        # We pretend this is the real AI giving us perfectly formatted JSON
        llm_output = mock_llm_call(prompt) 
    except Exception as e:
        # The assignment requires you to decide what happens if the AI fails
        raise HTTPException(status_code=502, detail=f"LLM Generation failed: {str(e)}")

    # 5. Save the generated output to our "NoSQL" JSON store
    # We link it to the selection_id and the version it was generated against
    nosql_db.save_test_cases(
        selection_id=selection.id, 
        test_cases=llm_output["test_cases"], 
        version_id=selection.version_id
    )
    
    return {
        "message": "Test cases generated successfully!", 
        "selection_id": selection.id,
        "data": llm_output
    }


@app.get("/retrieval/{selection_id}")
def retrieve_and_check_staleness(selection_id: int, db: Session = Depends(get_db)):
    """Fetches saved test cases and checks if the underlying document text has changed."""
    
    # 1. Fetch the generated test cases from the JSON store
    saved_data = nosql_db.get_test_cases(selection_id)
    if not saved_data:
        raise HTTPException(status_code=404, detail="No test cases found for this selection.")
        
    # 2. Get the original selection from the database
    selection = db.query(models.Selection).filter(models.Selection.id == selection_id).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection record missing in database.")
        
    # 3. Find the LATEST version of the document in the database
    latest_version = db.query(models.DocumentVersion).order_by(models.DocumentVersion.id.desc()).first()
    
    node_ids = [int(id.strip()) for id in selection.node_ids.split(",")]
    
    staleness_report = []
    is_overall_stale = False
    
    # 4. Compare the original nodes to the latest nodes
    for n_id in node_ids:
        # Get the original node the AI read
        original_node = db.query(models.DocumentNode).filter(models.DocumentNode.id == n_id).first()
        if not original_node:
            continue
            
        # If we are already on the latest version, it can't be stale
        if original_node.version_id == latest_version.id:
            staleness_report.append({
                "logical_node_id": original_node.logical_node_id,
                "status": "up-to-date"
            })
            continue
            
        # Look for this exact same logical section in the newer version
        newer_node = db.query(models.DocumentNode).filter(
            models.DocumentNode.logical_node_id == original_node.logical_node_id,
            models.DocumentNode.version_id == latest_version.id
        ).first()
        
        if not newer_node:
            is_overall_stale = True
            staleness_report.append({
                "logical_node_id": original_node.logical_node_id,
                "status": "stale (node was deleted in new version)"
            })
        elif original_node.content_hash != newer_node.content_hash:
            is_overall_stale = True
            staleness_report.append({
                "logical_node_id": original_node.logical_node_id,
                "status": "stale (content changed in new version)"
            })
        else:
            staleness_report.append({
                "logical_node_id": original_node.logical_node_id,
                "status": "up-to-date (content unchanged)"
            })

    return {
        "selection_id": selection_id,
        "original_version_id": selection.version_id,
        "latest_version_id": latest_version.id,
        "is_stale": is_overall_stale,
        "node_analysis": staleness_report,
        "test_cases": saved_data["test_cases"]
    }
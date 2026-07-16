import json
import os

JSON_STORE_PATH = "test_cases_store.json"

def init_store():
    """Creates the JSON file if it doesn't exist."""
    if not os.path.exists(JSON_STORE_PATH):
        with open(JSON_STORE_PATH, "w") as f:
            json.dump({}, f)

def save_test_cases(selection_id: int, test_cases: list, version_id: int):
    """Saves the LLM output linked to the selection ID."""
    init_store()
    
    with open(JSON_STORE_PATH, "r") as f:
        data = json.load(f)
        
    # We store it under the selection_id so we can look it up later
    data[str(selection_id)] = {
        "version_id": version_id,
        "test_cases": test_cases
    }
    
    with open(JSON_STORE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_test_cases(selection_id: int):
    """Retrieves saved test cases."""
    init_store()
    with open(JSON_STORE_PATH, "r") as f:
        data = json.load(f)
    return data.get(str(selection_id))
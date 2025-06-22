from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from models.pydantic_models import ResolutionCreate
from models.enums import IssueStatus
from utils.firebase import db
from utils.timestamps import add_timestamps
from google.cloud.firestore import transactional

router = APIRouter()

def find_issue_project(issue_id: str) -> str | None:
    """Helper to find the project_id for a given issue_id."""
    projects = db.collection("projects").stream()
    for proj in projects:
        issue_ref = db.collection("projects").document(proj.id).collection("issues").document(issue_id)
        if issue_ref.get().exists:
            return proj.id
    return None

@transactional
def update_in_transaction(transaction, issue_ref, resolution_data):
    """Transactional function to add resolution and update issue status."""
    new_res_ref = issue_ref.collection("resolutions").document()
    transaction.set(new_res_ref, resolution_data)
    transaction.update(issue_ref, {
        "status": IssueStatus.RESOLVED.value,
        "updated_at": resolution_data["updated_at"]
    })

@router.post("/", status_code=201)
def add_resolution(res: ResolutionCreate = Body(...)) -> Dict[str, str]:
    # Validate parent document existence
    project_id = find_issue_project(res.issue_id)
    if not project_id:
        raise HTTPException(status_code=404, detail=f"Issue with ID '{res.issue_id}' not found in any project.")

    resolution_data = res.model_dump(exclude={"issue_id"})
    resolution_data = add_timestamps(resolution_data)
    
    issue_ref = db.collection("projects").document(project_id).collection("issues").document(res.issue_id)
    
    try:
        transaction = db.transaction()
        update_in_transaction(transaction, issue_ref, resolution_data)
        return {"message": "Resolution logged and issue marked as resolved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")
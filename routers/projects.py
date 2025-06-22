from fastapi import APIRouter, HTTPException, Path, Body
from typing import List, Dict
from uuid import uuid4
from models.pydantic_models import ProjectCreate, ProjectUpdate, AchievementUpdate
from utils.firebase import db, doc_exists
from utils.timestamps import add_timestamps
from datetime import datetime
from firebase_admin import firestore
from datetime import timezone

router = APIRouter()

@router.post("/", status_code=201)
def create_project(project: ProjectCreate) -> Dict[str, str]:
    project_id = str(uuid4())
    project_data = project.model_dump()
    project_data = add_timestamps(project_data)
    
    try:
        db.collection("projects").document(project_id).set(project_data)
        return {"message": "Project created successfully", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@router.get("/")
def list_projects() -> Dict[str, List[Dict]]:
    try:
        projects_ref = db.collection("projects").stream()
        projects = [{"id": doc.id, **doc.to_dict()} for doc in projects_ref]
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@router.patch("/{project_id}", status_code=200)
def update_project(
    project_id: str = Path(...),
    update_data: ProjectUpdate = Body(...)
) -> Dict[str, str]:
    """
    1. General Project Update Endpoint
    """
    if not doc_exists("projects", project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    project_ref = db.collection("projects").document(project_id)
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_dict = add_timestamps(update_dict, is_update=True)
    
    try:
        project_ref.update(update_dict)
        return {"message": f"Project {project_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@router.patch("/{project_id}/achievements", status_code=200)
def add_project_achievement(
    project_id: str = Path(...),
    payload: AchievementUpdate = Body(...)
) -> Dict[str, str]:
    """
    3. Timestamp Achievements
    """
    if not doc_exists("projects", project_id):
        raise HTTPException(status_code=404, detail="Project not found")
        
    project_ref = db.collection("projects").document(project_id)
    
    # Prepend the date to the achievement
    timestamped_achievement = f"[{datetime.now().strftime('%Y-%m-%d')}] {payload.new_achievement}"
    
    update_data = {
        "achievements": firestore.ArrayUnion([timestamped_achievement]),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        project_ref.update(update_data)
        return {"message": "Achievement added successfully", "achievement": timestamped_achievement}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")
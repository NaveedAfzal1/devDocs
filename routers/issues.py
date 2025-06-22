import random
import string
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Query
from models.pydantic_models import IssueCreate
from models.enums import IssueStatus
from utils.firebase import db, doc_exists
from utils.imgbb import upload_image_to_imgbb
from utils.timestamps import add_timestamps

router = APIRouter()

def generate_short_id(prefix: str = "ISSUE") -> str:
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_str}"

@router.post("/", status_code=201)
async def create_issue(
    project_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    steps_to_reproduce: str = Form(...),
    severity: str = Form(...),
    priority: str = Form(...),
    reporter: str = Form(...),
    frequency: int = Form(...),
    screenshot: Optional[UploadFile] = File(None)
) -> Dict[str, str]:
    # 7. Validate parent document existence
    if not doc_exists("projects", project_id):
        raise HTTPException(status_code=404, detail=f"Project with ID '{project_id}' not found.")

    image_url = None
    if screenshot:
        try:
            image_url = await upload_image_to_imgbb(screenshot)
        except HTTPException as e:
            # Re-raise image upload specific errors
            raise e
        except Exception as e:
            # 4. Improve Error Messaging
            raise HTTPException(status_code=500, detail=f"Failed to process screenshot: {e}")

    issue_id = generate_short_id()
    issue_data = {
        "project_id": project_id,
        "title": title,
        "description": description,
        "steps_to_reproduce": steps_to_reproduce,
        "severity": severity,
        "priority": priority,
        "reporter": reporter,
        "frequency": frequency,
        "screenshot_url": image_url,
        "status": IssueStatus.OPEN.value
    }
    
    issue_data = add_timestamps(issue_data)
    
    try:
        db.collection("projects").document(project_id).collection("issues").document(issue_id).set(issue_data)
        return {"message": "Issue logged successfully", "issue_id": issue_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@router.get("/")
def get_issues(
    project_id: Optional[str] = Query(None),
    status: Optional[IssueStatus] = Query(None),
    reporter: Optional[str] = Query(None)
) -> Dict[str, List[Dict]]:
    issues = []
    
    try:
        if project_id:
            if not doc_exists("projects", project_id):
                 raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
            projects_to_scan = [project_id]
        else:
            projects_to_scan = [doc.id for doc in db.collection("projects").stream()]

        for pid in projects_to_scan:
            query = db.collection("projects").document(pid).collection("issues")
            if status:
                query = query.where("status", "==", status.value)
            if reporter:
                query = query.where("reporter", "==", reporter)
            
            for doc in query.stream():
                issues.append({"id": doc.id, **doc.to_dict()})
                
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@router.get("/search")
def search_issues(q: str = Query(..., min_length=3)) -> Dict[str, List[Dict]]:
    """
    10. Full-Text Search Endpoint
    Searches issues by title, description, or ID.
    """
    matching_issues = []
    query_lower = q.lower()
    
    try:
        project_docs = db.collection("projects").stream()
        for project in project_docs:
            issue_docs = project.reference.collection("issues").stream()
            for issue in issue_docs:
                issue_data = issue.to_dict()
                if (query_lower in issue_data.get("title", "").lower() or
                    query_lower in issue_data.get("description", "").lower() or
                    query_lower == issue.id.lower()):
                    matching_issues.append({"id": issue.id, **issue_data})
                    
        return {"results": matching_issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during search: {e}")
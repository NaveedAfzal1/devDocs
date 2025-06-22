from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from .enums import ProjectStatus, IssueStatus, IssueSeverity, IssuePriority

# --- Project Models ---
class ProjectBase(BaseModel):
    name: str = Field(..., example="Project Phoenix")
    tech_stack: str = Field(..., example="FastAPI, React, PostgreSQL")
    description: str = Field(..., example="A next-gen issue tracking system.")
    team_members: List[str] = Field(..., example=["Alice", "Bob"])
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, example="Active")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Project Phoenix V2")
    tech_stack: Optional[str] = Field(None, example="FastAPI, Vue, MongoDB")
    description: Optional[str] = Field(None, example="An enhanced issue tracker.")
    team_members: Optional[List[str]] = Field(None, example=["Alice", "Bob", "Charlie"])
    status: Optional[ProjectStatus] = Field(None, example="On Hold")

class AchievementUpdate(BaseModel):
    new_achievement: str = Field(..., example="Launched beta version to 100 users.")

class Project(ProjectBase):
    id: UUID = Field(default_factory=uuid4)
    achievements: List[str] = Field([], example=["[2025-06-23] Initial commit"])
    created_at: str
    updated_at: str

# --- Issue Models ---
class IssueBase(BaseModel):
    title: str = Field(..., example="Database connection error on startup")
    description: str = Field(..., example="The main server fails to connect to the database.")
    steps_to_reproduce: str = Field(..., example="1. Start the server. 2. Observe logs.")
    severity: IssueSeverity = Field(..., example="Critical")
    priority: IssuePriority = Field(..., example="P0")
    reporter: str = Field(..., example="dev_alice@example.com")
    frequency: int = Field(..., example=10)
    status: IssueStatus = Field(IssueStatus.OPEN, example="Open")

class IssueCreate(IssueBase):
    project_id: str = Field(..., example="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6")

class Issue(IssueBase):
    id: str
    project_id: str
    screenshot_url: Optional[str] = None
    created_at: str
    updated_at: str

# --- Resolution Models ---
class ResolutionBase(BaseModel):
    resolver: str = Field(..., example="dev_bob@example.com")
    resolution_summary: str = Field(..., example="Fixed incorrect DB credentials in config.")
    root_cause: str = Field(..., example="Environment variables were not loaded correctly.")
    modules_affected: Optional[str] = Field(None, example="auth_service, user_service")
    time_spent_hours: Optional[float] = Field(None, example=2.5)
    commit_id: Optional[str] = Field(None, example="a1b2c3d4e5f6")

class ResolutionCreate(ResolutionBase):
    issue_id: str = Field(..., example="ISSUE-250623114709-ABCD")

class Resolution(ResolutionBase):
    id: str
    issue_id: str
    resolved_at: str
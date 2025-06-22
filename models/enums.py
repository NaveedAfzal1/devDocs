from enum import Enum

class IssueStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    UNDER_REVIEW = "Under Review"
    TESTING = "Testing"
    RESOLVED = "Resolved"
    REOPENED = "Reopened"
    CLOSED = "Closed"

class IssueSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class IssuePriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class ProjectStatus(str, Enum):
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    ARCHIVED = "Archived"
    COMPLETED = "Completed"
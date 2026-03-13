"""Data models for incident management."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    """Incident severity levels."""
    SEV1 = "sev1"  # Critical
    SEV2 = "sev2"  # High
    SEV3 = "sev3"  # Medium
    SEV4 = "sev4"  # Low


class Status(str, Enum):
    """Incident status."""
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(str, Enum):
    """Action item priority."""
    P0 = "p0"  # Critical
    P1 = "p1"  # High
    P2 = "p2"  # Medium
    P3 = "p3"  # Low


class Config(BaseModel):
    """Configuration for incident management."""
    team: str = "Engineering"
    default_severity: Severity = Severity.SEV3
    timezone: str = "UTC"
    postmortem_template: str = "default"
    notification_channels: list[str] = Field(default_factory=list)


class Event(BaseModel):
    """Timeline event."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    timestamp: datetime
    description: str
    author: Optional[str] = None


class ActionItem(BaseModel):
    """Action item from postmortem."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    description: str
    owner: str
    due_date: Optional[datetime] = None
    priority: Priority = Priority.P2
    status: str = "open"
    jira_ticket: Optional[str] = None


class Impact(BaseModel):
    """Incident impact metrics."""
    duration_minutes: Optional[int] = None
    users_affected: Optional[int] = None
    sla_breached: bool = False
    revenue_impact: Optional[str] = None
    description: str = ""


class RootCause(BaseModel):
    """Root cause analysis."""
    summary: str
    contributing_factors: list[str] = Field(default_factory=list)
    detection_method: Optional[str] = None


class Incident(BaseModel):
    """Main incident model."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    id: str
    title: str
    severity: Severity
    status: Status = Status.INVESTIGATING
    created_at: datetime = Field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    owner: Optional[str] = None
    team: str = "Engineering"

    # Detailed information
    description: str = ""
    impact: Impact = Field(default_factory=lambda: Impact(description=""))
    root_cause: Optional[RootCause] = None

    # Timeline and actions
    events: list[Event] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)

    # Links and references
    links: dict[str, str] = Field(default_factory=dict)  # dashboard, logs, PRs, etc.
    tags: list[str] = Field(default_factory=list)

    # Retrospective
    what_went_well: list[str] = Field(default_factory=list)
    what_went_wrong: list[str] = Field(default_factory=list)

    def add_event(self, description: str, author: Optional[str] = None) -> Event:
        """Add a timeline event."""
        event = Event(
            timestamp=datetime.now(),
            description=description,
            author=author
        )
        self.events.append(event)
        return event

    def add_action_item(
        self,
        description: str,
        owner: str,
        priority: Priority = Priority.P2,
        due_date: Optional[datetime] = None
    ) -> ActionItem:
        """Add an action item."""
        action = ActionItem(
            description=description,
            owner=owner,
            priority=priority,
            due_date=due_date
        )
        self.action_items.append(action)
        return action

    def close(self) -> None:
        """Close the incident."""
        self.status = Status.CLOSED
        self.closed_at = datetime.now()

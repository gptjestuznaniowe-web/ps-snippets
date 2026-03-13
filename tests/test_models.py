"""Tests for data models."""
from datetime import datetime

import pytest

from inc.models import (
    ActionItem,
    Event,
    Impact,
    Incident,
    Priority,
    RootCause,
    Severity,
    Status,
)


def test_incident_creation():
    """Test creating a basic incident."""
    incident = Incident(
        id="inc-001",
        title="Test Incident",
        severity=Severity.SEV2,
        team="Engineering"
    )

    assert incident.id == "inc-001"
    assert incident.title == "Test Incident"
    assert incident.severity == Severity.SEV2
    assert incident.status == Status.INVESTIGATING
    assert incident.team == "Engineering"
    assert len(incident.events) == 0
    assert len(incident.action_items) == 0


def test_add_event():
    """Test adding events to incident timeline."""
    incident = Incident(
        id="inc-001",
        title="Test",
        severity=Severity.SEV3,
    )

    event = incident.add_event("Something happened", "Alice")

    assert len(incident.events) == 1
    assert incident.events[0].description == "Something happened"
    assert incident.events[0].author == "Alice"
    assert isinstance(incident.events[0].timestamp, datetime)


def test_add_action_item():
    """Test adding action items."""
    incident = Incident(
        id="inc-001",
        title="Test",
        severity=Severity.SEV3,
    )

    action = incident.add_action_item(
        description="Fix the bug",
        owner="Bob",
        priority=Priority.P1
    )

    assert len(incident.action_items) == 1
    assert incident.action_items[0].description == "Fix the bug"
    assert incident.action_items[0].owner == "Bob"
    assert incident.action_items[0].priority == Priority.P1
    assert incident.action_items[0].status == "open"


def test_close_incident():
    """Test closing an incident."""
    incident = Incident(
        id="inc-001",
        title="Test",
        severity=Severity.SEV3,
    )

    assert incident.status == Status.INVESTIGATING
    assert incident.closed_at is None

    incident.close()

    assert incident.status == Status.CLOSED
    assert incident.closed_at is not None
    assert isinstance(incident.closed_at, datetime)


def test_impact_model():
    """Test impact model."""
    impact = Impact(
        duration_minutes=45,
        users_affected=1000,
        sla_breached=True,
        description="Service was down"
    )

    assert impact.duration_minutes == 45
    assert impact.users_affected == 1000
    assert impact.sla_breached is True
    assert impact.description == "Service was down"


def test_root_cause_model():
    """Test root cause model."""
    root_cause = RootCause(
        summary="Database connection pool exhausted",
        contributing_factors=["High traffic", "Small pool size"],
        detection_method="Automated monitoring alert"
    )

    assert root_cause.summary == "Database connection pool exhausted"
    assert len(root_cause.contributing_factors) == 2
    assert root_cause.detection_method == "Automated monitoring alert"

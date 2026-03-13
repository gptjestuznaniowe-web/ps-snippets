"""Tests for template rendering."""
from datetime import datetime

from inc.models import Incident, Priority, Severity
from inc.templates import render_postmortem


def test_render_basic_postmortem():
    """Test rendering a basic postmortem."""
    incident = Incident(
        id="inc-001",
        title="Database Outage",
        severity=Severity.SEV1,
        description="Primary database became unresponsive",
        owner="Alice",
        team="Infrastructure"
    )

    postmortem = render_postmortem(incident)

    assert "Database Outage" in postmortem
    assert "inc-001" in postmortem
    assert "SEV1" in postmortem
    assert "Alice" in postmortem
    assert "Infrastructure" in postmortem


def test_render_postmortem_with_events():
    """Test rendering postmortem with timeline events."""
    incident = Incident(
        id="inc-002",
        title="API Degradation",
        severity=Severity.SEV2,
    )

    incident.add_event("Alert received", "Bob")
    incident.add_event("Investigation started", "Bob")
    incident.add_event("Issue resolved", "Alice")

    postmortem = render_postmortem(incident)

    assert "Alert received" in postmortem
    assert "Investigation started" in postmortem
    assert "Issue resolved" in postmortem
    assert "Bob" in postmortem
    assert "Alice" in postmortem


def test_render_postmortem_with_actions():
    """Test rendering postmortem with action items."""
    incident = Incident(
        id="inc-003",
        title="Cache Failure",
        severity=Severity.SEV3,
    )

    incident.add_action_item(
        "Add monitoring for cache health",
        "Charlie",
        Priority.P1
    )

    incident.add_action_item(
        "Update runbook",
        "Diana",
        Priority.P2
    )

    postmortem = render_postmortem(incident)

    assert "Add monitoring for cache health" in postmortem
    assert "Update runbook" in postmortem
    assert "Charlie" in postmortem
    assert "Diana" in postmortem
    assert "P1" in postmortem
    assert "P2" in postmortem

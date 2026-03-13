"""Tests for utility functions."""
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from inc.models import Config, Incident, Severity
from inc.utils import (
    generate_incident_id,
    load_config,
    load_incident,
    save_config,
    save_incident,
)


def test_generate_incident_id():
    """Test incident ID generation."""
    inc_id = generate_incident_id()

    assert inc_id.startswith("inc-")
    assert len(inc_id) > 4
    # Should contain timestamp
    assert inc_id[4:].isdigit()


def test_config_save_load(tmp_path, monkeypatch):
    """Test saving and loading configuration."""
    # Change working directory to temp
    monkeypatch.chdir(tmp_path)

    config = Config(
        team="Test Team",
        timezone="America/New_York"
    )

    save_config(config)

    loaded = load_config()

    assert loaded.team == "Test Team"
    assert loaded.timezone == "America/New_York"


def test_incident_save_load(tmp_path, monkeypatch):
    """Test saving and loading incidents."""
    # Change working directory to temp
    monkeypatch.chdir(tmp_path)

    incident = Incident(
        id="inc-test123",
        title="Test Incident",
        severity=Severity.SEV2,
        description="Test description"
    )

    # Add some data
    incident.add_event("Event 1")
    incident.add_action_item("Action 1", "Alice")

    # Save
    incident_dir = save_incident(incident)

    assert incident_dir.exists()
    assert (incident_dir / "incident.yaml").exists()

    # Load
    loaded = load_incident("inc-test123")

    assert loaded.id == incident.id
    assert loaded.title == incident.title
    assert loaded.severity == incident.severity
    assert loaded.description == incident.description
    assert len(loaded.events) == 1
    assert len(loaded.action_items) == 1


def test_load_nonexistent_incident(tmp_path, monkeypatch):
    """Test loading non-existent incident raises error."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        load_incident("inc-nonexistent")

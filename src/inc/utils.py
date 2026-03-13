"""Utility functions for incident management."""
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

from .models import Config, Incident

yaml = YAML()
yaml.default_flow_style = False
yaml.preserve_quotes = True


def get_config_path() -> Path:
    """Get the configuration file path."""
    return Path.cwd() / ".inc" / "config.yaml"


def get_incidents_dir() -> Path:
    """Get the incidents directory."""
    return Path.cwd() / "incidents"


def load_config() -> Config:
    """Load configuration from .inc/config.yaml."""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(
            "Configuration not found. Run 'inc init' first."
        )

    with open(config_path, "r") as f:
        data = yaml.load(f)

    return Config(**data)


def save_config(config: Config) -> None:
    """Save configuration to .inc/config.yaml."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        # Use mode='json' to serialize enums and datetime objects properly
        yaml.dump(config.model_dump(mode='json'), f)


def generate_incident_id() -> str:
    """Generate a unique incident ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"inc-{timestamp}"


def get_incident_dir(incident_id: str) -> Path:
    """Get the directory for a specific incident."""
    incidents_dir = get_incidents_dir()
    # Find incident directory (may have different date prefix)
    for dir_path in incidents_dir.glob(f"*{incident_id}*"):
        if dir_path.is_dir():
            return dir_path

    # Return the expected path if not found
    date_str = datetime.now().strftime("%Y-%m-%d")
    return incidents_dir / f"{date_str}_{incident_id}_new"


def load_incident(incident_id: str) -> Incident:
    """Load an incident from its YAML file."""
    incident_dir = get_incident_dir(incident_id)
    incident_file = incident_dir / "incident.yaml"

    if not incident_file.exists():
        raise FileNotFoundError(f"Incident {incident_id} not found at {incident_file}")

    with open(incident_file, "r") as f:
        data = yaml.load(f)

    # Convert datetime strings back to datetime objects
    if data.get("created_at"):
        data["created_at"] = datetime.fromisoformat(data["created_at"])
    if data.get("closed_at"):
        data["closed_at"] = datetime.fromisoformat(data["closed_at"])

    if data.get("events"):
        for event in data["events"]:
            if event.get("timestamp"):
                event["timestamp"] = datetime.fromisoformat(event["timestamp"])

    if data.get("action_items"):
        for action in data["action_items"]:
            if action.get("due_date"):
                action["due_date"] = datetime.fromisoformat(action["due_date"])

    return Incident(**data)


def save_incident(incident: Incident) -> Path:
    """Save an incident to its YAML file."""
    incident_dir = get_incident_dir(incident.id)
    incident_dir.mkdir(parents=True, exist_ok=True)

    incident_file = incident_dir / "incident.yaml"

    # Use mode='json' to serialize enums and datetime objects properly
    data = incident.model_dump(mode='json')

    with open(incident_file, "w") as f:
        yaml.dump(data, f)

    return incident_dir


def save_timeline(incident: Incident, incident_dir: Path) -> None:
    """Save timeline to markdown file."""
    timeline_file = incident_dir / "timeline.md"

    lines = [
        f"# Timeline: {incident.title}",
        "",
        f"**Incident ID:** {incident.id}",
        f"**Severity:** {incident.severity.value.upper()}",
        f"**Status:** {incident.status.value.capitalize()}",
        "",
        "## Events",
        ""
    ]

    for event in sorted(incident.events, key=lambda e: e.timestamp):
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        author = f" ({event.author})" if event.author else ""
        lines.append(f"- **{timestamp}**{author}: {event.description}")

    if not incident.events:
        lines.append("*No events recorded yet*")

    with open(timeline_file, "w") as f:
        f.write("\n".join(lines))


def create_export_bundle(incident: Incident) -> Path:
    """Create a ZIP bundle with all incident files."""
    incident_dir = get_incident_dir(incident.id)
    export_file = incident_dir / f"{incident.id}_export.zip"

    # Create summary JSON
    summary = {
        "id": incident.id,
        "title": incident.title,
        "severity": incident.severity.value,
        "status": incident.status.value,
        "created_at": incident.created_at.isoformat(),
        "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
        "owner": incident.owner,
        "team": incident.team,
        "action_items_count": len(incident.action_items),
        "events_count": len(incident.events)
    }

    summary_file = incident_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Create ZIP
    with zipfile.ZipFile(export_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in incident_dir.glob("*"):
            if file.is_file() and not file.name.endswith("_export.zip"):
                zf.write(file, file.name)

    return export_file

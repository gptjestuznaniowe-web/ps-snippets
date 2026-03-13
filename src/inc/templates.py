"""Templates for postmortem generation."""
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from .models import Incident


DEFAULT_POSTMORTEM_TEMPLATE = """# Postmortem: {{ incident.title }}

**Incident ID:** {{ incident.id }}
**Date:** {{ incident.created_at.strftime('%Y-%m-%d') }}
**Severity:** {{ incident.severity.value.upper() }}
**Status:** {{ incident.status.value.capitalize() }}
**Owner:** {{ incident.owner or 'TBD' }}
**Team:** {{ incident.team }}

---

## Summary

{{ incident.description or '*To be filled*' }}

---

## Impact

{{ incident.impact.description or '*To be filled*' }}

{% if incident.impact.duration_minutes %}
**Duration:** {{ incident.impact.duration_minutes }} minutes
{% endif %}
{% if incident.impact.users_affected %}
**Users Affected:** {{ incident.impact.users_affected }}
{% endif %}
{% if incident.impact.sla_breached %}
**SLA Breach:** Yes
{% endif %}
{% if incident.impact.revenue_impact %}
**Revenue Impact:** {{ incident.impact.revenue_impact }}
{% endif %}

---

## Timeline

{% if incident.events %}
{% for event in incident.events|sort(attribute='timestamp') %}
- **{{ event.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}**{% if event.author %} ({{ event.author }}){% endif %}: {{ event.description }}
{% endfor %}
{% else %}
*No events recorded*
{% endif %}

---

## Detection

{% if incident.root_cause and incident.root_cause.detection_method %}
{{ incident.root_cause.detection_method }}
{% else %}
*How was this incident detected? (alert, monitoring, user report, etc.)*
{% endif %}

---

## Root Cause

{% if incident.root_cause %}
{{ incident.root_cause.summary }}
{% else %}
*To be filled*
{% endif %}

---

## Contributing Factors

{% if incident.root_cause and incident.root_cause.contributing_factors %}
{% for factor in incident.root_cause.contributing_factors %}
- {{ factor }}
{% endfor %}
{% else %}
*What factors contributed to this incident?*
{% endif %}

---

## What Went Well

{% if incident.what_went_well %}
{% for item in incident.what_went_well %}
- {{ item }}
{% endfor %}
{% else %}
*What worked well during this incident?*
{% endif %}

---

## What Went Wrong

{% if incident.what_went_wrong %}
{% for item in incident.what_went_wrong %}
- {{ item }}
{% endfor %}
{% else %}
*What could have been better?*
{% endif %}

---

## Action Items

{% if incident.action_items %}
| Priority | Description | Owner | Due Date | Status | Ticket |
|----------|-------------|-------|----------|--------|--------|
{% for action in incident.action_items|sort(attribute='priority') %}
| {{ action.priority.value.upper() }} | {{ action.description }} | {{ action.owner }} | {{ action.due_date.strftime('%Y-%m-%d') if action.due_date else 'TBD' }} | {{ action.status }} | {{ action.jira_ticket or '-' }} |
{% endfor %}
{% else %}
*No action items yet*
{% endif %}

---

## Links & References

{% if incident.links %}
{% for key, url in incident.links.items() %}
- **{{ key.capitalize() }}:** {{ url }}
{% endfor %}
{% else %}
*Dashboards, logs, PRs, deployment records, etc.*
{% endif %}

{% if incident.tags %}

---

**Tags:** {{ incident.tags|join(', ') }}
{% endif %}

---

*Generated: {{ now.strftime('%Y-%m-%d %H:%M:%S') }}*
"""


def render_postmortem(incident: Incident) -> str:
    """Render postmortem markdown from incident data."""
    template = Template(DEFAULT_POSTMORTEM_TEMPLATE)
    return template.render(
        incident=incident,
        now=datetime.now()
    )


def save_postmortem(incident: Incident, incident_dir: Path) -> Path:
    """Save postmortem to markdown file."""
    postmortem_file = incident_dir / "postmortem.md"
    content = render_postmortem(incident)

    with open(postmortem_file, "w") as f:
        f.write(content)

    return postmortem_file

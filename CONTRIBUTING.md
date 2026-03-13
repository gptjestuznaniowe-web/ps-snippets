# Contributing to Incident CLI

## Development Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Project Structure

```
.
├── src/inc/              # Main package
│   ├── cli.py           # CLI commands (typer)
│   ├── models.py        # Data models (pydantic)
│   ├── utils.py         # Utility functions
│   └── templates.py     # Postmortem templates (jinja2)
├── tests/               # Test suite
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_templates.py
├── pyproject.toml       # Package configuration
└── README.md            # Documentation
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=inc --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_incident_creation -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and small

## Adding New Features

### Adding a New Command

1. Add the command function in `src/inc/cli.py`:
```python
@app.command()
def mycommand(
    arg: str = typer.Argument(..., help="Description"),
    option: str = typer.Option(None, help="Optional parameter"),
):
    """Command description."""
    # Implementation
    pass
```

2. Add tests in `tests/test_cli.py`

### Adding New Fields to Incident

1. Update the `Incident` model in `src/inc/models.py`:
```python
class Incident(BaseModel):
    # ... existing fields
    new_field: str = ""
```

2. Update the postmortem template in `src/inc/templates.py`
3. Add tests in `tests/test_models.py`

### Customizing the Postmortem Template

Edit `DEFAULT_POSTMORTEM_TEMPLATE` in `src/inc/templates.py`. It uses Jinja2 syntax:

```jinja2
## New Section

{% if incident.new_field %}
{{ incident.new_field }}
{% else %}
*To be filled*
{% endif %}
```

## Testing Checklist

Before submitting a PR:

- [ ] All tests pass (`pytest`)
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation updated (README.md)
- [ ] Type hints added
- [ ] Docstrings added

## Future Ideas

### Integrations
- Jira integration (auto-create tickets from action items)
- Slack notifications
- PagerDuty webhook
- ServiceNow sync

### Features
- `inc diff` - show changes between incident versions
- `inc search` - search incidents by text/tags
- `inc stats` - incident statistics and trends
- `inc template` - custom postmortem templates
- `inc review` - review checklist before closing
- Support for incident severity auto-escalation
- Timeline visualization (ASCII art or export to timeline tools)

### Improvements
- Add incident categories/types
- Support for multiple teams
- SLO tracking integration
- Incident relationship tracking (parent/child incidents)
- Export to PDF
- Web UI for viewing incidents

## Questions?

Open an issue or reach out to the team.

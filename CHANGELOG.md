# Changelog

All notable changes to the Incident CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-24

### Added
- Initial release of Incident CLI
- Core incident management commands:
  - `inc init` - Initialize configuration
  - `inc create` - Create new incident
  - `inc update` - Update incident details
  - `inc add` - Add timeline events
  - `inc close` - Close incident
  - `inc show` - Display incident details
  - `inc list` - List all incidents
  - `inc export` - Export incident bundle
- Postmortem generation:
  - `inc postmortem render` - Generate postmortem from incident data
  - `inc postmortem action` - Add action items
- Data models:
  - Incident with full lifecycle tracking
  - Timeline events with timestamps
  - Action items with priorities and due dates
  - Impact metrics (duration, users affected, SLA breach)
  - Root cause analysis
  - Retrospective fields (what went well/wrong)
- YAML as single source of truth
- Automatic Markdown generation (timeline, postmortem)
- JSON summary export for integrations
- ZIP bundle export
- Rich terminal UI with colors and tables
- Complete test suite with pytest
- Comprehensive documentation

### Technical Details
- Python 3.11+ support
- Pydantic v2 for data validation
- Typer for CLI framework
- Rich for terminal output
- Jinja2 for templating
- ruamel.yaml for YAML handling

## [Unreleased]

### Planned Features
- Jira integration for action items
- Slack notifications
- Custom postmortem templates
- Incident search and filtering
- Statistics and trends
- Multi-team support
- SLO tracking
- PDF export

"""CLI commands for incident management."""
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .models import (
    ActionItem,
    Config,
    Impact,
    Incident,
    Priority,
    RootCause,
    Severity,
    Status,
)
from .templates import render_postmortem, save_postmortem
from .utils import (
    create_export_bundle,
    generate_incident_id,
    get_config_path,
    get_incident_dir,
    load_config,
    load_incident,
    save_config,
    save_incident,
    save_timeline,
)

app = typer.Typer(help="Incident management and postmortem generator CLI")
postmortem_app = typer.Typer(help="Postmortem commands")
app.add_typer(postmortem_app, name="postmortem")

console = Console()


@app.command()
def init(
    team: str = typer.Option("Engineering", help="Team name"),
    timezone: str = typer.Option("UTC", help="Timezone"),
):
    """Initialize incident management configuration."""
    config_path = get_config_path()

    if config_path.exists():
        if not typer.confirm(f"Config already exists at {config_path}. Overwrite?"):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()

    config = Config(team=team, timezone=timezone)
    save_config(config)

    console.print(Panel.fit(
        f"[green]✓[/green] Configuration initialized at [cyan]{config_path}[/cyan]\n\n"
        f"Team: {team}\n"
        f"Timezone: {timezone}",
        title="Incident CLI Initialized",
        border_style="green"
    ))


@app.command()
def create(
    title: str = typer.Argument(..., help="Incident title"),
    severity: Severity = typer.Option(Severity.SEV3, help="Incident severity"),
    owner: Optional[str] = typer.Option(None, help="Incident owner"),
    description: Optional[str] = typer.Option(None, help="Incident description"),
):
    """Create a new incident."""
    try:
        config = load_config()
    except FileNotFoundError:
        console.print("[red]Error: Configuration not found. Run 'inc init' first.[/red]")
        raise typer.Exit(1)

    # Generate incident
    incident_id = generate_incident_id()
    date_str = datetime.now().strftime("%Y-%m-%d")

    incident = Incident(
        id=incident_id,
        title=title,
        severity=severity,
        owner=owner,
        team=config.team,
        description=description or "",
    )

    # Add initial event
    incident.add_event(
        description=f"Incident created with severity {severity.value.upper()}",
        author=owner
    )

    # Save incident
    incident_dir = save_incident(incident)

    # Update directory name with title (sanitized)
    sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
    sanitized_title = sanitized_title.replace(' ', '-')[:50]
    new_dir_name = f"{date_str}_{incident_id}_{sanitized_title}"
    new_incident_dir = incident_dir.parent / new_dir_name

    if new_incident_dir != incident_dir:
        incident_dir.rename(new_incident_dir)
        incident_dir = new_incident_dir

    # Save timeline and postmortem
    save_timeline(incident, incident_dir)
    save_postmortem(incident, incident_dir)

    console.print(Panel.fit(
        f"[green]✓[/green] Incident created\n\n"
        f"ID: [cyan]{incident_id}[/cyan]\n"
        f"Title: {title}\n"
        f"Severity: {severity.value.upper()}\n"
        f"Directory: [cyan]{incident_dir}[/cyan]",
        title="New Incident",
        border_style="green"
    ))


@app.command()
def update(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    status: Optional[Status] = typer.Option(None, help="Update status"),
    owner: Optional[str] = typer.Option(None, help="Update owner"),
    severity: Optional[Severity] = typer.Option(None, help="Update severity"),
    description: Optional[str] = typer.Option(None, help="Update description"),
    impact_desc: Optional[str] = typer.Option(None, help="Impact description"),
    duration: Optional[int] = typer.Option(None, help="Duration in minutes"),
    users_affected: Optional[int] = typer.Option(None, help="Number of users affected"),
    sla_breached: bool = typer.Option(False, help="Mark SLA as breached"),
):
    """Update incident details."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    # Update fields
    updated = []
    if status:
        incident.status = status
        updated.append(f"Status → {status.value}")
    if owner:
        incident.owner = owner
        updated.append(f"Owner → {owner}")
    if severity:
        incident.severity = severity
        updated.append(f"Severity → {severity.value.upper()}")
    if description:
        incident.description = description
        updated.append("Description updated")

    # Update impact
    if any([impact_desc, duration, users_affected, sla_breached]):
        if impact_desc:
            incident.impact.description = impact_desc
        if duration:
            incident.impact.duration_minutes = duration
        if users_affected:
            incident.impact.users_affected = users_affected
        if sla_breached:
            incident.impact.sla_breached = True
        updated.append("Impact updated")

    if not updated:
        console.print("[yellow]No changes specified.[/yellow]")
        raise typer.Exit()

    # Save
    incident_dir = save_incident(incident)
    save_timeline(incident, incident_dir)

    console.print(Panel.fit(
        f"[green]✓[/green] Incident updated\n\n" + "\n".join(f"• {u}" for u in updated),
        title=f"Updated {incident_id}",
        border_style="green"
    ))


@app.command("add")
def add_event(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    description: str = typer.Argument(..., help="Event description"),
    author: Optional[str] = typer.Option(None, help="Event author"),
):
    """Add an event to the incident timeline."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    event = incident.add_event(description, author)
    incident_dir = save_incident(incident)
    save_timeline(incident, incident_dir)

    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    console.print(
        f"[green]✓[/green] Event added at {timestamp}: {description}"
    )


@app.command()
def close(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    root_cause: Optional[str] = typer.Option(None, help="Root cause summary"),
):
    """Close an incident."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    if root_cause:
        if not incident.root_cause:
            incident.root_cause = RootCause(summary=root_cause)
        else:
            incident.root_cause.summary = root_cause

    incident.close()
    incident.add_event("Incident closed", None)

    incident_dir = save_incident(incident)
    save_timeline(incident, incident_dir)
    save_postmortem(incident, incident_dir)

    console.print(Panel.fit(
        f"[green]✓[/green] Incident closed\n\n"
        f"ID: {incident_id}\n"
        f"Duration: {(incident.closed_at - incident.created_at).total_seconds() / 60:.1f} minutes",
        title="Incident Closed",
        border_style="green"
    ))


@postmortem_app.command("render")
def postmortem_render(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    show: bool = typer.Option(False, "--show", help="Display postmortem in terminal"),
):
    """Render postmortem from incident data."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    incident_dir = get_incident_dir(incident_id)
    postmortem_file = save_postmortem(incident, incident_dir)

    console.print(
        f"[green]✓[/green] Postmortem rendered: [cyan]{postmortem_file}[/cyan]"
    )

    if show:
        console.print("\n" + "="*80 + "\n")
        with open(postmortem_file) as f:
            md = Markdown(f.read())
            console.print(md)


@postmortem_app.command("action")
def postmortem_action(
    incident_id: str = typer.Argument(..., help="Incident ID"),
    description: str = typer.Argument(..., help="Action item description"),
    owner: str = typer.Option(..., help="Action item owner"),
    priority: Priority = typer.Option(Priority.P2, help="Priority"),
    due_date: Optional[str] = typer.Option(None, help="Due date (YYYY-MM-DD)"),
    jira: Optional[str] = typer.Option(None, help="Jira ticket ID"),
):
    """Add an action item to the postmortem."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    due = None
    if due_date:
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Error: Invalid date format. Use YYYY-MM-DD.[/red]")
            raise typer.Exit(1)

    action = incident.add_action_item(description, owner, priority, due)
    if jira:
        action.jira_ticket = jira

    incident_dir = save_incident(incident)
    save_postmortem(incident, incident_dir)

    console.print(
        f"[green]✓[/green] Action item added: {description} ({owner}, {priority.value.upper()})"
    )


@app.command()
def export(
    incident_id: str = typer.Argument(..., help="Incident ID"),
):
    """Export incident as a ZIP bundle."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    export_file = create_export_bundle(incident)

    console.print(Panel.fit(
        f"[green]✓[/green] Export created\n\n"
        f"File: [cyan]{export_file}[/cyan]\n"
        f"Size: {export_file.stat().st_size / 1024:.1f} KB",
        title="Export Complete",
        border_style="green"
    ))


@app.command()
def list():
    """List all incidents."""
    from .utils import get_incidents_dir

    incidents_dir = get_incidents_dir()
    if not incidents_dir.exists():
        console.print("[yellow]No incidents directory found.[/yellow]")
        return

    incident_dirs = sorted(incidents_dir.glob("*inc-*"), reverse=True)

    if not incident_dirs:
        console.print("[yellow]No incidents found.[/yellow]")
        return

    table = Table(title="Incidents")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Severity", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Created", style="blue")

    for inc_dir in incident_dirs:
        try:
            # Extract incident ID from directory name
            parts = inc_dir.name.split("_")
            inc_id = next((p for p in parts if p.startswith("inc-")), None)
            if not inc_id:
                continue

            incident = load_incident(inc_id)
            table.add_row(
                incident.id,
                incident.title[:50],
                incident.severity.value.upper(),
                incident.status.value.capitalize(),
                incident.created_at.strftime("%Y-%m-%d %H:%M"),
            )
        except Exception:
            continue

    console.print(table)


@app.command()
def show(
    incident_id: str = typer.Argument(..., help="Incident ID"),
):
    """Show incident details."""
    try:
        incident = load_incident(incident_id)
    except FileNotFoundError:
        console.print(f"[red]Error: Incident {incident_id} not found.[/red]")
        raise typer.Exit(1)

    # Build info panel
    info = [
        f"[bold]ID:[/bold] {incident.id}",
        f"[bold]Title:[/bold] {incident.title}",
        f"[bold]Severity:[/bold] {incident.severity.value.upper()}",
        f"[bold]Status:[/bold] {incident.status.value.capitalize()}",
        f"[bold]Team:[/bold] {incident.team}",
        f"[bold]Owner:[/bold] {incident.owner or 'TBD'}",
        f"[bold]Created:[/bold] {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if incident.closed_at:
        duration = (incident.closed_at - incident.created_at).total_seconds() / 60
        info.append(f"[bold]Closed:[/bold] {incident.closed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"[bold]Duration:[/bold] {duration:.1f} minutes")

    console.print(Panel("\n".join(info), title="Incident Details", border_style="cyan"))

    # Impact
    if incident.impact.description or incident.impact.users_affected:
        impact_info = []
        if incident.impact.description:
            impact_info.append(f"[bold]Description:[/bold] {incident.impact.description}")
        if incident.impact.duration_minutes:
            impact_info.append(f"[bold]Duration:[/bold] {incident.impact.duration_minutes} minutes")
        if incident.impact.users_affected:
            impact_info.append(f"[bold]Users Affected:[/bold] {incident.impact.users_affected}")
        if incident.impact.sla_breached:
            impact_info.append("[bold]SLA:[/bold] [red]BREACHED[/red]")

        console.print(Panel("\n".join(impact_info), title="Impact", border_style="yellow"))

    # Timeline
    if incident.events:
        console.print("\n[bold]Timeline:[/bold]")
        for event in sorted(incident.events, key=lambda e: e.timestamp):
            timestamp = event.timestamp.strftime("%H:%M:%S")
            author = f" [{event.author}]" if event.author else ""
            console.print(f"  {timestamp}{author}: {event.description}")

    # Action Items
    if incident.action_items:
        table = Table(title="Action Items")
        table.add_column("Priority", style="yellow")
        table.add_column("Description")
        table.add_column("Owner", style="cyan")
        table.add_column("Due", style="blue")
        table.add_column("Status", style="green")

        for action in sorted(incident.action_items, key=lambda a: a.priority):
            table.add_row(
                action.priority.value.upper(),
                action.description,
                action.owner,
                action.due_date.strftime("%Y-%m-%d") if action.due_date else "TBD",
                action.status,
            )

        console.print("\n")
        console.print(table)


if __name__ == "__main__":
    app()

# inc - Incident Management CLI

Narzędzie CLI do zarządzania incydentami i automatycznego generowania postmortemów.

## Cel

Skrócenie czasu od alertu do sensownego ticketu/postmortemu i standaryzacja procesu zarządzania incydentami.

## Funkcje

- Tworzenie i śledzenie incydentów z timeline'em
- Automatyczne generowanie postmortemów w formacie Markdown
- Zarządzanie action items z priorytetami
- Export incydentów do ZIP (z JSON summary dla integracji)
- Ładny, kolorowy output w terminalu
- YAML jako single source of truth (łatwe do edycji ręcznie)

## Instalacja

```bash
# Z repozytorium
git clone <repo-url>
cd notes

# Instalacja w trybie development
pip install -e .

# Lub z zależnościami dev (testy)
pip install -e ".[dev]"
```

## Szybki start

```bash
# 1. Inicjalizacja konfiguracji
inc init --team "Backend Team"

# 2. Stworzenie nowego incydentu
inc create "Database connection timeout" --severity sev1 --owner "alice@example.com"

# 3. Dodanie wydarzeń do timeline
inc add inc-20260124120000 "Started investigation"
inc add inc-20260124120000 "Identified root cause in connection pool" --author alice

# 4. Aktualizacja szczegółów incydentu
inc update inc-20260124120000 \
  --status monitoring \
  --impact-desc "API response time increased by 200%" \
  --duration 45 \
  --users-affected 5000

# 5. Dodanie action items
inc postmortem action inc-20260124120000 \
  "Increase connection pool size" \
  --owner bob \
  --priority p0 \
  --due-date 2026-01-25

# 6. Zamknięcie incydentu
inc close inc-20260124120000 --root-cause "Connection pool exhausted under high load"

# 7. Wygenerowanie postmortem
inc postmortem render inc-20260124120000 --show

# 8. Export do ZIP
inc export inc-20260124120000
```

## Komendy

### Inicjalizacja

```bash
inc init [OPTIONS]
```

Tworzy `.inc/config.yaml` z konfiguracją zespołu.

**Opcje:**
- `--team TEXT` - Nazwa zespołu (domyślnie: "Engineering")
- `--timezone TEXT` - Strefa czasowa (domyślnie: "UTC")

**Przykład:**
```bash
inc init --team "SRE Team" --timezone "Europe/Warsaw"
```

### Tworzenie incydentu

```bash
inc create TITLE [OPTIONS]
```

Zakłada nowy incident i generuje:
- `incidents/2026-01-24_inc-{id}_{title}/incident.yaml`
- `timeline.md`
- `postmortem.md` (szablon)

**Opcje:**
- `--severity [sev1|sev2|sev3|sev4]` - Poziom ważności (domyślnie: sev3)
- `--owner TEXT` - Właściciel incydentu
- `--description TEXT` - Opis incydentu

**Przykłady:**
```bash
inc create "API Gateway timeout" --severity sev1 --owner alice
inc create "Slow query performance" --severity sev3 --description "Users reporting slow dashboard loads"
```

### Aktualizacja incydentu

```bash
inc update INCIDENT_ID [OPTIONS]
```

Aktualizuje szczegóły incydentu.

**Opcje:**
- `--status [investigating|identified|monitoring|resolved|closed]` - Status
- `--owner TEXT` - Właściciel
- `--severity [sev1|sev2|sev3|sev4]` - Poziom ważności
- `--description TEXT` - Opis
- `--impact-desc TEXT` - Opis wpływu
- `--duration INTEGER` - Czas trwania w minutach
- `--users-affected INTEGER` - Liczba dotkniętych użytkowników
- `--sla-breached` - Oznacz naruszenie SLA

**Przykład:**
```bash
inc update inc-20260124120000 \
  --status monitoring \
  --impact-desc "Service degraded, 30% of requests failing" \
  --duration 30 \
  --users-affected 10000 \
  --sla-breached
```

### Dodawanie wydarzeń

```bash
inc add INCIDENT_ID DESCRIPTION [OPTIONS]
```

Dodaje wydarzenie do timeline incydentu z automatycznym timestampem.

**Opcje:**
- `--author TEXT` - Autor wydarzenia

**Przykłady:**
```bash
inc add inc-20260124120000 "Alert received from PagerDuty"
inc add inc-20260124120000 "Rolled back deployment to v1.2.3" --author bob
inc add inc-20260124120000 "Service fully recovered"
```

### Zamykanie incydentu

```bash
inc close INCIDENT_ID [OPTIONS]
```

Zamyka incydent i generuje finalny postmortem.

**Opcje:**
- `--root-cause TEXT` - Podsumowanie głównej przyczyny

**Przykład:**
```bash
inc close inc-20260124120000 \
  --root-cause "Memory leak in cache layer caused OOM errors"
```

### Postmortem - renderowanie

```bash
inc postmortem render INCIDENT_ID [OPTIONS]
```

Generuje postmortem.md z danych YAML i timeline.

**Opcje:**
- `--show` - Wyświetl postmortem w terminalu

**Przykład:**
```bash
inc postmortem render inc-20260124120000 --show
```

### Postmortem - action items

```bash
inc postmortem action INCIDENT_ID DESCRIPTION [OPTIONS]
```

Dodaje action item do postmortem.

**Opcje:**
- `--owner TEXT` - Właściciel (wymagane)
- `--priority [p0|p1|p2|p3]` - Priorytet (domyślnie: p2)
- `--due-date TEXT` - Termin w formacie YYYY-MM-DD
- `--jira TEXT` - ID ticketu w Jira

**Przykłady:**
```bash
inc postmortem action inc-20260124120000 \
  "Add circuit breaker to API calls" \
  --owner alice \
  --priority p0 \
  --due-date 2026-01-26 \
  --jira INFRA-1234

inc postmortem action inc-20260124120000 \
  "Update runbook with new troubleshooting steps" \
  --owner bob \
  --priority p2
```

### Export

```bash
inc export INCIDENT_ID
```

Tworzy paczkę ZIP zawierającą:
- `incident.yaml`
- `timeline.md`
- `postmortem.md`
- `summary.json` (dla integracji z Jira/ServiceNow)

**Przykład:**
```bash
inc export inc-20260124120000
# Creates: incidents/2026-01-24_inc-20260124120000_*/inc-20260124120000_export.zip
```

### Lista incydentów

```bash
inc list
```

Wyświetla wszystkie incydenty w tabeli.

**Przykład:**
```bash
inc list
```

### Szczegóły incydentu

```bash
inc show INCIDENT_ID
```

Wyświetla pełne informacje o incydencie.

**Przykład:**
```bash
inc show inc-20260124120000
```

## Struktura plików

Po inicjalizacji i utworzeniu incydentu:

```
.
├── .inc/
│   └── config.yaml              # Konfiguracja zespołu
├── incidents/
│   └── 2026-01-24_inc-{id}_{title}/
│       ├── incident.yaml        # Single source of truth (YAML)
│       ├── timeline.md          # Timeline wydarzeń (auto)
│       ├── postmortem.md        # Postmortem (auto + szablon)
│       ├── summary.json         # Export summary (do integracji)
│       └── inc-{id}_export.zip  # Bundle (po export)
```

## Poziomy ważności (Severity)

- **SEV1** - Critical - Pełna awaria usługi, wpływ na wszystkich użytkowników
- **SEV2** - High - Znacząca degradacja, wpływ na wielu użytkowników
- **SEV3** - Medium - Częściowa degradacja, ograniczony wpływ
- **SEV4** - Low - Niewielki wpływ, nie wpływa na użytkowników końcowych

## Priorytety action items

- **P0** - Critical - Do zrobienia natychmiast
- **P1** - High - Do zrobienia w ciągu tygodnia
- **P2** - Medium - Do zrobienia w ciągu miesiąca
- **P3** - Low - Backlog, do rozważenia

## Format postmortem

Automatycznie generowany postmortem zawiera:

1. **Summary** - Podsumowanie incydentu
2. **Impact** - Wpływ (czas, użytkownicy, SLA, przychód)
3. **Timeline** - Automatyczny timeline z YAML
4. **Detection** - Jak wykryto incident (alert/monitoring)
5. **Root Cause** - Główna przyczyna
6. **Contributing Factors** - Czynniki przyczyniające się
7. **What Went Well** - Co zadziałało dobrze
8. **What Went Wrong** - Co można poprawić
9. **Action Items** - Tabela z action items (auto)
10. **Links** - Dashboardy, logi, PRs, deploys

## Ręczna edycja

Wszystkie pliki YAML można edytować ręcznie:

```yaml
# incidents/2026-01-24_inc-{id}_{title}/incident.yaml
id: inc-20260124120000
title: Database connection timeout
severity: sev1
status: closed
owner: alice@example.com
team: Backend Team
description: Primary database connection pool exhausted

impact:
  duration_minutes: 45
  users_affected: 5000
  sla_breached: true
  description: API response time degraded by 200%

events:
  - timestamp: '2026-01-24T12:00:00'
    description: Alert received
    author: alice

action_items:
  - description: Increase connection pool size
    owner: bob
    priority: p0
    due_date: '2026-01-25'
    status: open

what_went_well:
  - Quick detection via monitoring
  - Fast rollback

what_went_wrong:
  - No runbook for this scenario
  - Lack of capacity planning
```

Po edycji uruchom:
```bash
inc postmortem render inc-20260124120000
```

## Integracja z innymi narzędziami

`summary.json` jest przygotowany do łatwej integracji:

```json
{
  "id": "inc-20260124120000",
  "title": "Database connection timeout",
  "severity": "sev1",
  "status": "closed",
  "created_at": "2026-01-24T12:00:00",
  "closed_at": "2026-01-24T12:45:00",
  "owner": "alice@example.com",
  "team": "Backend Team",
  "action_items_count": 3,
  "events_count": 8
}
```

Można to użyć do:
- Automatycznego tworzenia ticketów w Jira
- Powiadomień w Slack/MS Teams
- Aktualizacji ServiceNow
- Dashboardów incident metrics

## Development

```bash
# Instalacja z dev dependencies
pip install -e ".[dev]"

# Uruchomienie testów
pytest

# Testy z coverage
pytest --cov=inc --cov-report=html

# Formatowanie
black src/ tests/

# Type checking
mypy src/
```

## Przykładowy workflow

```bash
# 1. Alert przychodzi z PagerDuty
inc create "High error rate on /api/users" --severity sev1 --owner alice

# 2. Podczas investigacji dodawaj wydarzenia
inc add inc-XXX "Started investigating logs"
inc add inc-XXX "Found spike in database connections" --author alice
inc add inc-XXX "Identified memory leak in connection pooling"

# 3. Podczas mitigation
inc update inc-XXX --status identified
inc add inc-XXX "Deployed hotfix v1.2.4"
inc update inc-XXX --status monitoring

# 4. Po rozwiązaniu
inc add inc-XXX "Error rate back to normal"
inc update inc-XXX \
  --status resolved \
  --impact-desc "Users experienced 500 errors on user profile page" \
  --duration 37 \
  --users-affected 2500

# 5. Dodaj action items
inc postmortem action inc-XXX \
  "Fix memory leak in connection pool" \
  --owner bob --priority p0 --due-date 2026-01-25 --jira INFRA-456

inc postmortem action inc-XXX \
  "Add monitoring for connection pool health" \
  --owner charlie --priority p1 --due-date 2026-01-27

inc postmortem action inc-XXX \
  "Update runbook with troubleshooting steps" \
  --owner diana --priority p2

# 6. Zamknij i wygeneruj postmortem
inc close inc-XXX --root-cause "Memory leak in connection pool under high concurrent load"

# 7. Zobacz postmortem
inc postmortem render inc-XXX --show

# 8. Export do wysłania zespołowi
inc export inc-XXX
```

## Technologie

- **Python 3.11+**
- **typer** - Framework CLI
- **pydantic** - Walidacja danych i modele
- **ruamel.yaml** - Obsługa YAML (zachowuje formatowanie)
- **jinja2** - Templating postmortem
- **rich** - Ładny output w terminalu
- **pytest** - Testy

## Licencja

MIT

## Autor

Internal Tools Team

#!/bin/bash
# Example workflow demonstrating the incident CLI

set -e

echo "=== Incident Management CLI - Example Workflow ==="
echo ""

# 1. Initialize
echo "1. Initializing configuration..."
inc init --team "SRE Team" --timezone "UTC"
echo ""

# 2. Create incident
echo "2. Creating new SEV1 incident..."
inc create "API Gateway timeout" \
  --severity sev1 \
  --owner alice@example.com \
  --description "Users experiencing timeouts when accessing API gateway"
echo ""

# Extract incident ID from the most recent incident
INCIDENT_ID=$(ls -t incidents/ | head -1 | grep -o 'inc-[0-9]*')
echo "Created incident: $INCIDENT_ID"
echo ""

# 3. Add events to timeline
echo "3. Adding events to timeline..."
inc add $INCIDENT_ID "Alert received from DataDog - 95th percentile latency > 5s" --author alice@example.com
inc add $INCIDENT_ID "Investigated nginx logs, seeing connection pool exhaustion" --author alice@example.com
inc add $INCIDENT_ID "Identified memory leak in API Gateway service" --author bob@example.com
inc add $INCIDENT_ID "Deployed hotfix v2.3.1 with memory leak fix" --author bob@example.com
inc add $INCIDENT_ID "Monitoring recovery - latency returning to normal" --author alice@example.com
echo ""

# 4. Update incident details
echo "4. Updating incident impact and status..."
inc update $INCIDENT_ID \
  --status monitoring \
  --impact-desc "95th percentile API latency increased from 200ms to 8000ms, causing timeout errors for users" \
  --duration 67 \
  --users-affected 25000 \
  --sla-breached
echo ""

# 5. Add action items
echo "5. Adding action items..."
inc postmortem action $INCIDENT_ID \
  "Add memory profiling to API Gateway service" \
  --owner charlie@example.com \
  --priority p0 \
  --due-date 2026-01-26 \
  --jira INFRA-2001

inc postmortem action $INCIDENT_ID \
  "Implement circuit breaker pattern for downstream services" \
  --owner diana@example.com \
  --priority p1 \
  --due-date 2026-01-30 \
  --jira INFRA-2002

inc postmortem action $INCIDENT_ID \
  "Update runbook with memory leak troubleshooting steps" \
  --owner alice@example.com \
  --priority p2
echo ""

# 6. Close incident
echo "6. Closing incident..."
inc add $INCIDENT_ID "Service fully recovered, monitoring shows normal behavior"
inc close $INCIDENT_ID \
  --root-cause "Memory leak in connection handling code caused gradual memory exhaustion over 48 hours. Under peak load, the service ran out of memory and became unresponsive."
echo ""

# 7. Generate postmortem
echo "7. Generating postmortem..."
inc postmortem render $INCIDENT_ID
echo ""

# 8. Show incident details
echo "8. Showing incident details..."
inc show $INCIDENT_ID
echo ""

# 9. Export
echo "9. Exporting incident bundle..."
inc export $INCIDENT_ID
echo ""

# 10. List all incidents
echo "10. Listing all incidents..."
inc list
echo ""

echo "=== Workflow Complete ==="
echo "Check the incidents/ directory for generated files:"
echo "  - incident.yaml (single source of truth)"
echo "  - timeline.md (auto-generated timeline)"
echo "  - postmortem.md (complete postmortem)"
echo "  - summary.json (for integrations)"
echo "  - *_export.zip (bundle for sharing)"

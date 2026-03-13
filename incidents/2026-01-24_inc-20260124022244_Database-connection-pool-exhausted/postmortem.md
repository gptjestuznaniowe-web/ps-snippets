# Postmortem: Database connection pool exhausted

**Incident ID:** inc-20260124022244
**Date:** 2026-01-24
**Severity:** SEV1
**Status:** Closed
**Owner:** alice@example.com
**Team:** Backend Team

---

## Summary

API experiencing 500 errors due to database connection timeouts

---

## Impact

API error rate spiked to 35%, affecting user login and data retrieval


**Duration:** 45 minutes


**Users Affected:** 15000


**SLA Breach:** Yes



---

## Timeline



- **2026-01-24 02:22:44** (alice@example.com): Incident created with severity SEV1

- **2026-01-24 02:22:54** (alice@example.com): Alert received from PagerDuty - high error rate

- **2026-01-24 02:22:54** (alice@example.com): Identified connection pool at max capacity

- **2026-01-24 02:22:54** (bob@example.com): Increased pool size from 10 to 50

- **2026-01-24 02:23:24**: Error rate back to normal levels

- **2026-01-24 02:23:25**: Incident closed



---

## Detection


*How was this incident detected? (alert, monitoring, user report, etc.)*


---

## Root Cause


Database connection pool size (10) was insufficient for peak traffic load. Under high concurrent requests, all connections were exhausted, causing new requests to timeout.


---

## Contributing Factors


*What factors contributed to this incident?*


---

## What Went Well


*What worked well during this incident?*


---

## What Went Wrong


*What could have been better?*


---

## Action Items


| Priority | Description | Owner | Due Date | Status | Ticket |
|----------|-------------|-------|----------|--------|--------|

| P0 | Implement connection pool monitoring alerts | charlie@example.com | 2026-01-25 | open | INFRA-1234 |



---

## Links & References


*Dashboards, logs, PRs, deployment records, etc.*




---

*Generated: 2026-01-24 02:23:41*
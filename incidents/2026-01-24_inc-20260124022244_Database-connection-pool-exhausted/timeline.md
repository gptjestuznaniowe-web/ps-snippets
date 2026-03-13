# Timeline: Database connection pool exhausted

**Incident ID:** inc-20260124022244
**Severity:** SEV1
**Status:** Closed

## Events

- **2026-01-24 02:22:44** (alice@example.com): Incident created with severity SEV1
- **2026-01-24 02:22:54** (alice@example.com): Alert received from PagerDuty - high error rate
- **2026-01-24 02:22:54** (alice@example.com): Identified connection pool at max capacity
- **2026-01-24 02:22:54** (bob@example.com): Increased pool size from 10 to 50
- **2026-01-24 02:23:24**: Error rate back to normal levels
- **2026-01-24 02:23:25**: Incident closed
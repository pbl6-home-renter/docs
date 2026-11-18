# P10-32 - Removed: tenant-link maintenance/bootstrap tools

**Status:** Removed at the user's explicit request (P10-D91, 2026-11-18).

The maintenance CLI, bootstrap/snapshot API, dry-run/apply path, helper, dedicated tests and runbooks have been deleted. Do not implement a fallback/replay/repair script for this task.

The existing RabbitMQ lifecycle consumer is restored. Tenant linking during contract creation/activation remains in P10-31; the other backend fixes and normal regression tests remain in scope.

See [decision log](../decisions.md) and [current implementation](../discovery/mobile-backend-implementation.md).

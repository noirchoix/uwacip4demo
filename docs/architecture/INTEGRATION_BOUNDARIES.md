# UWACI Integration Boundaries

Standalone adapters make the reference service independently runnable. UWACI integration replaces those adapters with approved owner-module contracts.

| Port | Standalone | UWACI target |
|---|---|---|
| Authorization | JWT + local grants | Identity |
| Entity catalog | reference entity registry | Presence / approved owner |
| Locator | PostGIS | Locator |
| Provenance/source trust | local provenance/source tables | Knowledge |
| AI interpretation | provider-neutral HTTP gateway | Core AI Gateway |
| Usage | local limiter | Usage |
| Notifications | logging/event handoff | Notification |
| Jobs | Celery/Redis | approved host worker |

No integration adapter may directly mutate another module's private tables.

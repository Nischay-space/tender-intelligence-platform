# Engineering Decisions

---

## Decision #001

### Title

Documentation Before Implementation

### Decision

The project will prioritize documentation, architecture, and planning before writing production code.

### Rationale

Building a maintainable production system requires clear requirements and architecture before implementation begins. This reduces future redesigns and provides a shared understanding of project goals.

### Status

Accepted

### Date

28 July 2026


---

## Decision #002

### Title

No Authentication — Local-Only Deployment

### Decision

The API and dashboard will not implement authentication (no API keys, no user accounts, no login) while the system remains local-only, bound to 127.0.0.1 and never exposed beyond the developer's own machine.

### Rationale

Authentication protects against unauthorized access from *somewhere else* — it has no value when nothing outside the local machine can reach the API in the first place. Building it now would be complexity with no corresponding risk it defends against. Revisited explicitly rather than silently deferred: if this system is ever deployed anywhere reachable off the local machine (a shared server, cloud host, any URL other people can hit), authentication becomes mandatory before that deployment, not after. At minimum: a shared API key if it stays single-team; real per-user accounts (signup, password hashing, sessions) only if genuinely distinct users need to be told apart or restricted.

### Status

Accepted

### Date

02 September 2026
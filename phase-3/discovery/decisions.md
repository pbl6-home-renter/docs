# Decisions Log — Phase 3

> Quyết định phát sinh trong Phase 3 được ghi tại đây.
> Quyết định Phase 0 (D1–D29): `../../phase-0/discovery/decisions.md`
> Quyết định Phase 1 (D30–D39): `../../phase-1/discovery/decisions.md`
> Quyết định Phase 2 (D39–D50): `../../phase-2/discovery/decisions.md`
> Báo cáo nghiên cứu sinh ra các quyết định này: `microservices-architecture.md` (P3-02)

## Index

| ID | Date | Decision | Status |
|---|---|---|---|
| D51 | 2026-09-29 | AI removed from MVP scope; OCR for meter readings becomes a local Tesseract step inside `tenancy-service` | ⏸ Pending (PM + GV PBL6) |
| D52 | 2026-09-29 | Backend split into 4 services by bounded context: `identity`, `tenancy`, `payment`, `community` | 🟡 Proposed |
| D53 | 2026-09-29 | Database-per-service on one Postgres instance: 4 databases, 4 Postgres roles, cross-service foreign keys forbidden | 🟡 Proposed |
| D54 | 2026-09-29 | RabbitMQ as the message broker; HTTP/JSON for synchronous calls, AMQP topic exchange for events | 🟡 Proposed |
| D55 | 2026-09-29 | API Gateway with server-side discovery; service registry on heartbeat 6s / TTL 2s | 🟡 Proposed |
| D56 | 2026-09-29 | Deploy everything on one EC2 with Docker Compose, replacing the Render + Neon + Vercel combination | 🟡 Proposed (needs budget) |
| D57 | 2026-09-29 | Saga uses Orchestration, with `tenancy-service` as orchestrator for the invoice issuance flow | 🟡 Proposed |
| D58 | 2026-09-29 | Each service is its own Git repo with no shared library; all peer URLs come from env vars | 🟡 Proposed |

---

## D51 - AI removed from MVP; meter-reading OCR becomes a local Tesseract step

- **Date:** 2026-09-29
- **Status:** Pending (PM + GV PBL6)
- **Context:** `PROJECT_PLAN.md` line 13 lists **AI (1) Auto-Description** as an MVP item and `requirement.md` line 10 only records AI as *"Khuyến khích: thêm AI"*, so the plan and the requirement never agreed on how much AI was actually committed. The team has not settled on a concrete AI feature, so the AI workstream is being dropped. That leaves `requirement.md` line 27 (F5, OCR on the electricity/water bill photo) without a home, and it removes `pbl6-ai` from the repo list in the root `AGENTS.md`.
- **Decision:** Remove AI from MVP scope. Keep OCR, but run it locally.
  - No `pbl6-ai` repo, no Python/FastAPI service, no OpenAI API call anywhere in the system.
  - `POST /meter-readings` accepts an optional bill photo through the existing `Media` flow (**D40**) and extracts the index with a local **Tesseract** process inside `tenancy-service`.
  - Extracted values are always shown back to the landlord for confirmation before being saved, per `requirement.md` line 27 ("OCR + xác nhận tay"). OCR never writes a reading on its own.
  - If OCR is judged out of scope for Phase 1+, the endpoint keeps working with manual entry only and the photo is stored as evidence — no schema change either way.
- **Reason:** AI was never a locked requirement, so removing it does not break a promise made to the teacher, only an aspiration in the plan. Running OCR locally rather than as a service is deliberate: it is the only remaining "smart" feature, its input is a small image, its output is four numbers a human confirms, and it needs no network round trip to a model. That is a workload which does not justify a process boundary — unlike the payment provider in **D52**, there is no third-party contract to insulate against.
- **Consequence:** `PROJECT_PLAN.md` line 13 must be edited or the schedule keeps advertising a scope the team dropped, which is a source-of-truth violation rather than a doc nit. `AGENTS.md` at the repo root must lose its `pbl6-ai` row. `requirement.md` needs no edit, because it only ever asked for AI to be encouraged.
- **Not decided / left to migration:** Whether Tesseract accuracy is acceptable for Vietnamese utility bills, and whether OCR ships in Phase 1 or is deferred. If deferred, the `MeterReading` table needs no column and the photo simply becomes an ordinary `Media` attachment. PM to confirm.
- **Cross-ref:** `requirement.md` lines 10, 27; `PROJECT_PLAN.md` line 13; `api-spec.md` §5, §16; `phase-1/discovery/database-design.md` §2.11; `phase-2/discovery/decisions.md` D40; `microservices-architecture.md` §2.3, §12 question 2.

## D52 - Backend split into 4 services

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** The SOA course requires at least 4 services in the project, and Phase 3 had not written a single line of application code yet, so this is the cheapest moment in the whole schedule to split. The existing contract is 109 endpoints in 24 domain groups (`api-spec.md`), which has to be partitioned without leaving any group unowned.
- **Decision:** Partition the 24 groups into 4 services, **5 + 13 + 1 + 5**:
  - `identity-service` — Auth, User, PushDevice, Media, AuditLog.
  - `tenancy-service` — Building, Room, FavoriteRoom, RoommateProfile, MatchRequest, RatePolicy, BillingSetting, ContractTemplate, Contract, ContractMember, MeterReading, Invoice, Dashboard.
  - `payment-service` — Payment.
  - `community-service` — Conversation, Message, IssueReport, Notification, NotificationPreference.
  - `tenancy-service` is the **Saga orchestrator** for invoice issuance (see **D57**).
- **Reason:** Three of the four boundaries are load-bearing rather than decorative. `payment` exists because the provider webhook is the single place in the contract that breaks the global response-wrapper convention (`api-spec.md` line 211) — that anomaly *is* a contract boundary, and it only has to be absorbed once. `community` exists because chat is the only WebSocket workload and it fans out to FCM at a different rate from ordinary record writes. `identity` exists because every other service verifies a token it cannot issue. `tenancy` is the deliberate counter-case: merging property and billing is what keeps Room → Contract → MeterReading → Invoice inside one ACID transaction, and it is what keeps the service count at 4 instead of 6.
- **Consequence:** `tenancy-service` holds 13 of 24 groups and is the largest service in the system. That is accepted on purpose, not by accident. `Media` stays inside `identity` even though it is a textbook separate resource (streaming, binary, legal retention), because `api-spec.md` line 55 makes Media access *inherited* from its parent through `ownerType`/`ownerId` — and those parents live in all four services, so a separate media service would add one to three network hops to the hottest read path in the app.
- **Not decided / left to migration:** Whether the course counts the API Gateway as one of the 4 services. If the instructor requires it, the split becomes 5. Must be confirmed with the instructor before any code is written. Also unconfirmed: whether one backend engineer can carry 4 services; see `microservices-architecture.md` §10 R1 and §12 question 4.
- **Cross-ref:** `api-spec.md` §1, §2–§25; `microservices-architecture.md` §3, §4, §10 R1, §12 questions 1 and 4.

## D53 - Database-per-service on one Postgres instance

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** `database-design.md` defines 25 entities in a single schema. Splitting the application into 4 services raises the question of whether the schema splits too, and the answer changes the cost of every join in the system.
- **Decision:** One Postgres instance, **4 databases** and **4 distinct Postgres roles**.
  - `identity_db`, `tenancy_db`, `payment_db`, `community_db`, with the table assignment listed in `microservices-architecture.md` §3.1 and §6.1.
  - Each service connects as its own role, which holds grants on its own database and nothing else.
  - **No cross-service foreign keys, and no cross-database joins.** A join that needs data owned by another service becomes an HTTP call or an event.
  - Display-only fields (a landlord's name on a room card) may be denormalised and kept in sync by `user.registered` / `user.updated` events. Decision data (status, balances, permissions) is never copied and always read from its owner.
- **Reason:** A separate role per service is what turns Service Autonomy from a convention into a mechanism: an accidental cross-service join fails with a permission error instead of quietly working, so the violation surfaces immediately instead of becoming a hidden runtime dependency. Denormalising display fields is the standard trade for read-heavy data in an event-driven system, and the rule is kept narrow on purpose — copying anything that decides behaviour would be how a distributed system starts lying about money.
- **Consequence:** `database-design.md` needs a `service` column on all 25 entities and an explicit statement of which tables must not carry foreign keys. The existing ERD is a single-schema diagram and will have to be split into four.
- **Cross-ref:** `phase-1/discovery/database-design.md`; `api-spec.md` §28.4; `microservices-architecture.md` §6, §9.

## D54 - RabbitMQ as the message broker

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** The services need asynchronous, at-least-once delivery for invoice issuance, payment results, and notification fan-out. MQTT, Kafka and Redis Streams were all on the table, and the course material names RabbitMQ and Kafka directly.
- **Decision:** **RabbitMQ**, topic exchange `pbl6.events`, one queue per consumer, dead-letter exchange `dlq.parking`. Synchronous service-to-service calls stay on HTTP/JSON; AMQP carries only events.
- **Reason:** The deciding requirement is the dead-letter queue, not throughput. The saga in **D57** has a compensation branch, so an event that cannot be processed has to land somewhere for inspection rather than vanish or block the queue. Kafka provides ordering and replay but needs a JVM and real disk, which does not fit a small EC2. Redis Streams would share the same instance already serving the Socket.io adapter, so a chat burst would compete with payment events. RabbitMQ also expresses consumer groups directly: `invoice.issued` must be handled by exactly one `payment-service` instance, while `invoice.activated` is fanned out to `community-service` — a queue-per-consumer model states both without extra configuration. MQTT was rejected because it targets constrained edge devices, and PBL6 has none: OCR replaced the utility-bill API in **D51**, and D9 limits the product to long-term rentals.
- **Consequence:** Delivery is at-least-once, so every consumer must be idempotent. Outbox tables are required in `tenancy_db` and `payment_db` to avoid losing an event when the broker is down. Retry policy: 3 attempts with 1s/4s/16s backoff, then dead-letter.
- **Not decided / left to migration:** Queue names, prefetch values, and whether the DLQ gets an admin screen before M4. If smart meters are ever added, revisit the MQTT comparison.
- **Cross-ref:** `api-spec.md` §18; `phase-2/discovery/decisions.md` D43; `requirement.md` lines 22, 33; `microservices-architecture.md` §5.6, §5.7, §5.8.

## D55 - API Gateway with server-side discovery

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** Five client apps (D13) need one entry point, and the SOA course asks specifically about client-side versus server-side discovery, heartbeats, lease TTL, and what happens when an instance dies.
- **Decision:** A NestJS `api-gateway` on port 3000 is the only public entry point, using **server-side discovery** against a `service_registry` table.
  - Each service writes a heartbeat every **6 seconds** with a **2 second** TTL lease; the gateway re-reads the registry every 1 second.
  - If no healthy instance exists for a route, the gateway returns `503` with `Retry-After` instead of letting the request hang until timeout.
  - The gateway verifies JWTs locally from a cached JWKS (**D58**) and forwards an `X-Service-Token` so internal calls cannot be forged from outside.
  - No service except the gateway exposes a port to the internet.
- **Reason:** With only one host, Docker service names are already static, so the registry is not required to route traffic — it is required because the course asks the question, and because the gateway still needs a way to refuse an instance that is up but unhealthy. Server-side rather than client-side discovery is chosen so the mobile and web clients carry no knowledge of internal topology, which keeps **D58** portability intact.
- **Consequence:** The 6s/2s ratio is not arbitrary: a heartbeat equal to the TTL means a single millisecond of network jitter causes an instance to be deregistered and re-registered continuously, and the gateway then routes over a flapping address list. Three times the TTL absorbs jitter and GC pauses. If a service is later moved to another host, only the registry changes.
- **Not decided / left to migration:** Whether the registry table lives in a fifth database or inside `identity_db`. Provisioned inside `identity_db` for now, since the gateway already talks to `identity`.
- **Cross-ref:** `microservices-architecture.md` §5.1, §5.4.1, §7.3.

## D56 - Single-EC2 deployment with Docker Compose

- **Date:** 2026-09-29
- **Status:** Proposed (needs budget confirmation)
- **Context:** `phase-3/README.md` line 13 and `PROJECT_PLAN.md` line 118 both plan a managed combo, and `phase-0/discovery/tech-feasibility.md` line 257 settles on Render + Neon + Vercel. Splitting the backend into 4 services invalidates that plan: a managed platform with one free service slot cannot host 4 services plus a broker plus a database without either upgrading or collapsing back to a monolith, and a student project cannot afford a paid tier.
- **Decision:** One EC2 instance running the whole system under Docker Compose, behind Caddy or Nginx terminating TLS.
  - Compose services: `api-gateway`, `identity-service`, `tenancy-service`, `payment-service`, `community-service`, `postgres`, `rabbitmq`, `redis`, `minio`.
  - Only port 443 is exposed. A reverse proxy routes everything else internally.
  - **Minimum `t3.small` (2 GB); `t3.medium` (4 GB) recommended.** `t3.micro` is rejected — Postgres, RabbitMQ, Redis, MinIO and five Node processes together hit its ceiling, and an out-of-memory kill during the defense demo would cost the whole presentation.
  - Every service exposes `GET /health` reporting `db` and `broker` connectivity, and Compose restarts unhealthy containers.
- **Reason:** One machine is the only configuration a 5-person student team can afford and debug, and Compose is already assumed for local development, so production and local then differ only in `docker-compose.prod.yml`. Putting the broker and the database on the same host as the services is the deliberate cost of that affordability.
- **Consequence:** `PROJECT_PLAN.md` line 118 and `phase-3/README.md` line 13 must be updated, and `tech-feasibility.md` line 257 is now obsolete. This is a single point of failure: if the instance dies mid-demo the system is gone, which is why the instance must be provisioned at least two weeks before the defense and why `t3.medium` is preferred over the minimum. No autoscaling, no multi-AZ, no blue-green deploy.
- **Not decided / left to migration:** Exact instance size and who pays for it; whether a nightly `pg_dump` to off-site storage is set up; backup and restore procedure. PM to confirm budget.
- **Cross-ref:** `PROJECT_PLAN.md` line 118; `phase-3/README.md` line 13; `phase-0/discovery/tech-feasibility.md` line 257; `microservices-architecture.md` §7, §10 R2, §12 question 5.

## D57 - Saga with Orchestration for invoice issuance

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** Issuing an invoice spans two services: `tenancy-service` writes the `Invoice`, then `payment-service` asks an external provider for a QR. If the provider times out, the invoice must not stay in a half state. The course material recommends Choreography for flows of 2–3 services and Orchestration for 5 or more, and this flow is 2.
- **Decision:** Use **Orchestration**, with `tenancy-service` as the orchestrator and `payment-service` as the participant.
  - Step 1 — local transaction in `tenancy-service`: create `Invoice` as `PENDING_ISSUE` and insert an `invoice.issued` event into an **outbox** table in the same transaction.
  - Step 2 — `payment-service` consumes it, creates a `PaymentIntent` keyed by `Idempotency-Key = invoiceId`, calls the provider with an 8 second timeout.
  - Happy path — `payment.intent_created` returns, the invoice moves to `ACTIVE`, `invoice.activated` is published, `community-service` creates the `invoice` notification and pushes to FCM.
  - Compensation path — `payment.intent_failed` returns, the invoice is cancelled, the meter-reading period reopens, an `AuditLog` entry records why, and `community-service` notifies the landlord.
- **Reason:** The course heuristic says Choreography, and it is overridden deliberately. `tenancy-service` already holds the saga state because it owns `invoices` and decides whether an invoice is valid, so Choreography would force it to *listen* for `payment.intent_failed` and infer that it must cancel — pushing business rules into a subscriber where nobody can see them. Compensation is also multi-step, and Orchestration gives one place that decides the order. This is the arrangement the course material lists as the advantage of Orchestration, and it is the arrangement that keeps a compensation branch auditable.
- **Consequence:** No two-phase commit, because `payment-service` and `tenancy-service` are separate databases — that is exactly the situation Saga exists for. The outbox is mandatory: without it, a service that commits and then dies before publishing leaves an invoice stuck forever. Delivery is at-least-once, so every consumer must ignore an event it has already applied, keyed on `eventId` or on current status.
- **Not decided / left to migration:** Whether the outbox is drained by a separate process or a scheduled job inside each service; exact backoff values; whether the compensation path also notifies the tenant or only the landlord. Not settled.
- **Cross-ref:** `api-spec.md` §17, §18; `phase-2/discovery/decisions.md` D43, D49; `requirement.md` line 40 (D29); `microservices-architecture.md` §5.5.1, §5.5.2, §10 R5.

## D58 - One Git repository per service, no shared library

- **Date:** 2026-09-29
- **Status:** Proposed
- **Context:** PBL6 is graded on portability, and a microservice split that lives inside one monorepo with a shared `libs/` folder does not survive being moved to another project. This decision exists so the 4-service split is real rather than cosmetic.
- **Decision:** Each service is its own Git repository with its own `Dockerfile`, its own migrations and its own `README.md` describing what it does and how to run it alone.
  - **No shared library, no `libs/`, no cross-repo imports.** Contract types are duplicated rather than imported; duplication is the accepted cost.
  - Every peer service URL comes from an environment variable, never a hardcoded host or port.
  - `payment-service` in particular must not carry PBL6 domain vocabulary. `create-intent` takes `referenceId` instead of `invoiceId`; `record-cash-payment` takes `referenceId`, `amount` and `transactionId` instead of `receiptMediaId`; and the landlord payment list, which currently filters through `Invoice → Contract → Room`, **moves to `tenancy-service`** so that `payment-service` can stand alone.
  - Internal calls authenticate with a shared internal token; public tokens are RS256 and validated against JWKS.
- **Reason:** Splitting repositories is mechanical; untangling a shared library is a rewrite. The contract sanitisation is the part that actually proves portability: a service that says `invoiceId` in its public signature has leaked the fact that it exists to serve one particular system, no matter how cleanly the code is packaged. Renaming it to `referenceId` costs nothing and makes the boundary honest.
- **Consequence:** Moving the landlord payment list to `tenancy-service` is a real change to `api-spec.md` line 208, and `GET /payments` as currently specified is impossible for a standalone service because it joins across three services. The OpenAPI spec in `api-docs/` must be split into 4 specs plus a gateway spec, and `api-docs/src/` has to be reorganised: it is currently split by artifact type — `paths/`, `requests/`, `responses/`, `schemas/`, `common/`, `parameters/` — with `paths/` and `requests/` divided by resource (`auth/`, `buildings/`, `contracts/`, `invoices/`, `payments/`, `rooms/`, `users/`) and `schemas/` divided by domain (`property/`, `billing/`, `contract/`, `matching/`, `chat/`, `notification/`, `user/`). Neither axis matches the service boundaries, because `buildings/`, `contracts/`, `invoices/` and `rooms/` all collapse into `tenancy`, so each service bundle has to be assembled by service rather than inherited from the existing folders. Apidog syncs 4 specs; mobile and web still point at the gateway, so the P3-01 Apidog Mock workflow is unaffected.
- **Not decided / left to migration:** Whether the team can actually maintain 5 repositories (4 services plus the gateway) or whether the gateway should live in one of the service repos. Not settled.
- **Cross-ref:** `api-docs/` structure; `api-spec.md` lines 207–211; `api-conventions.md` §1, §13; root `AGENTS.md` repo table; `P3-01-mobile-apidog-e2e-research.md`; `microservices-architecture.md` §8, §9, §12 question 6.

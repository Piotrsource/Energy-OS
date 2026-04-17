# COMMERCIAL ENERGY OS — Product Requirements Document

## Phase 0–9 — Full Product Roadmap

| Field | Value |
|-------|-------|
| **Version** | 1.0 — Initial Release |
| **Status** | APPROVED FOR DEVELOPMENT |
| **Date** | March 2026 |
| **Owner** | Product — Commercial Energy OS |
| **Target** | Hotels, offices, retail, hospitals — 50–5,000 zone buildings; residential prosumers for P2P trading |

---

## Table of Contents

> **PURPOSE:** Navigation index for a 900+ line document. Jump directly to any section. The numbering mirrors the header hierarchy — sections 1–5 are strategy, 6–15 are phase specs, 16–20 are technical references.

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [User Personas](#4-user-personas)
5. [Phase Roadmap Overview](#5-phase-roadmap-overview)
6. [Phase 0 — Foundation (COMPLETE)](#6-phase-0--foundation-complete)
7. [Phase 1 — Production Hardening](#7-phase-1--production-hardening)
8. [Phase 2 — Real-Time Intelligence](#8-phase-2--real-time-intelligence)
9. [Phase 3 — AI Optimization Engine](#9-phase-3--ai-optimization-engine)
10. [Phase 4 — Billing & Cost Analytics](#10-phase-4--billing--cost-analytics)
11. [Phase 5 — Multi-Tenant & Organizations](#11-phase-5--multi-tenant--organizations)
12. [Phase 6 — Guest Comfort & Occupancy](#12-phase-6--guest-comfort--occupancy)
13. [Phase 7 — Integrations & Protocols](#13-phase-7--integrations--protocols)
14. [Phase 8 — Scale, Compliance & Marketplace](#14-phase-8--scale-compliance--marketplace)
15. [Phase 9 — Peer-to-Peer Energy Trading](#15-phase-9--peer-to-peer-energy-trading)
16. [Data Model](#16-data-model)
17. [API Specifications](#17-api-specifications)
18. [Non-Functional Requirements](#18-non-functional-requirements)
19. [Technology Stack](#19-technology-stack)
20. [Risks & Mitigations](#20-risks--mitigations)

---

## 1. Executive Summary

> **PURPOSE:** Provide a one-page overview that lets any reader — investor, engineer, designer, or new team member — understand the product's scope, current state, and ambition in under 2 minutes.

Commercial Energy OS is an AI-powered energy management platform purpose-built for hotels, commercial buildings, and residential prosumers. It collects real-time data from sensors, HVAC systems, and energy meters, applies machine learning to detect waste and forecast demand, delivers actionable optimization recommendations that reduce energy costs by 15–30%, and enables peer-to-peer energy trading where homeowners with solar panels or batteries sell excess energy directly to neighbors — think "Airbnb for electricity."

### Mission

> **PURPOSE:** Anchor every product decision to a single guiding statement. When scoping a feature, ask: "Does this help building operators see, understand, or optimize energy in real time?"

Give every building operator — from a 50-room boutique hotel to a 500,000 sq ft office campus — a single platform to see, understand, and optimize their energy consumption in real time.

### What Exists Today (Phase 0 — Complete)

> **PURPOSE:** Establish the baseline so every phase description can assume what already works, avoiding redundancy and setting clear "start here" expectations for developers.

A working full-stack prototype:
- **Backend**: FastAPI (Python 3.12), PostgreSQL 16 + TimescaleDB, JWT authentication, role-based access control
- **Frontend**: React + TypeScript + Vite + Tailwind CSS dashboard with Recharts visualization
- **Models**: Buildings, Zones, Users, Sensor Readings, HVAC Status, Energy Meters, Forecasts, Recommendations
- **Analytics**: Energy summary (time_bucket aggregation), carbon emissions estimation, z-score anomaly detection
- **Infrastructure**: Docker Compose, multi-stage Dockerfile, GitHub Actions CI/CD
- **Tests**: Async test suite with pytest, in-memory SQLite, auth/CRUD/sensor coverage

### What This PRD Defines

> **PURPOSE:** Set scope boundaries — this document covers Phases 1–9 only. Phase 0 is documented as context, not as work to be done.

Phases 1–8 build on this foundation to deliver a production-grade, commercially viable platform across 9 total phases (Phase 0 + Phases 1–8).

---

## 2. Problem Statement

> **PURPOSE:** Justify the product's existence. If you can't articulate a painful, expensive, and widespread problem, no feature list matters. This section is the "why" behind every line of code.

### 2.1 Market Context

> **PURPOSE:** Quantify the opportunity with hard numbers so stakeholders understand the market size and why commercial buildings (not homes, not factories) are the target.

Commercial buildings consume 40% of total energy in the US and EU. Hotels are among the most energy-intensive building types — a typical 200-room hotel spends $500K–$2M annually on energy, with HVAC accounting for 40–60% of that cost.

Three structural problems define the opportunity:

**Blind Operations.** Most building managers receive a single monthly utility bill with no breakdown by zone, system, or time period. They cannot identify waste because they cannot see it.

**Dumb HVAC.** HVAC systems in 80%+ of commercial buildings run on fixed schedules regardless of actual occupancy, weather, or energy prices. Empty conference rooms are heated. Unoccupied hotel floors are cooled. This wastes 20–35% of HVAC energy.

**Manual Processes.** Energy audits are expensive ($10K–$50K), infrequent (annual at best), and produce static PDF reports. There is no continuous optimization loop. Recommendations become stale within weeks as building usage patterns change.

### 2.2 User Pain Points

> **PURPOSE:** Translate abstract market problems into concrete frustrations felt by real people. Each row maps to a persona (Section 4) and drives specific features in the roadmap.

| User | Primary Pain |
|------|-------------|
| **Hotel GM / Building Manager** | No visibility into real-time energy costs; monthly bill is a black box; cannot identify which floors or systems waste energy |
| **Facility Manager** | Responds to comfort complaints reactively; no predictive maintenance signals; manually adjusts HVAC schedules seasonally |
| **Sustainability Director** | Cannot produce accurate ESG reports; carbon calculations are manual and approximate; no audit trail for energy reduction initiatives |
| **Property Owner / CFO** | Energy is the largest controllable operating expense but has no optimization tooling; cannot benchmark buildings against each other |

---

## 3. Product Vision & Goals

> **PURPOSE:** Define where the product is headed long-term and how success is measured at each phase, so engineering priorities align with business outcomes.

### 3.1 Vision Statement

> **PURPOSE:** Paint the end-state picture. This is the North Star used to evaluate trade-offs — e.g., "Does adding feature X move us closer to being the intelligence layer between buildings and operators?"

Commercial Energy OS becomes the intelligence layer between a building's physical systems and its operators — continuously learning from sensor data, predicting energy demand, and recommending (then automating) optimizations that no human team could execute manually at scale.

### 3.2 Product Goals by Phase

> **PURPOSE:** Make success measurable. Each cell is a concrete number the team can verify — no ambiguity about whether a phase delivered value.

| Goal | Metric | Phase 0 (Done) | Phase 2 | Phase 4 | Phase 8 |
|------|--------|----------------|---------|---------|---------|
| Data Visibility | Sensor-to-dashboard latency | < 5 min (batch) | < 10 sec (real-time) | < 10 sec | < 5 sec |
| Cost Reduction | Energy savings vs baseline | — | 10% (anomaly alerts) | 20% (AI optimization) | 30% (automated control) |
| Uptime | Platform availability | Dev only | 99% | 99.5% | 99.9% |
| Scale | Buildings managed | 1 (demo) | 5 (pilot) | 50 | 500+ |
| Time to Value | Onboarding to first insight | Manual | < 1 day | < 4 hours | < 1 hour |

---

## 4. User Personas

> **PURPOSE:** Give every developer a mental picture of who they're building for. When designing a feature, you should be able to say "Sofia would use this on her iPad between meetings" or "Carlos needs this on a wall-mounted monitor in the boiler room." Personas prevent building for imaginary users.

### Persona 1 — Hotel General Manager (Sofia)

> **PURPOSE:** Represents the executive buyer — the person who approves the purchase and cares about cost reduction and brand reputation, not technical details.

| Field | Detail |
|-------|--------|
| **Role** | GM of a 200-room hotel, $1.2M annual energy spend |
| **Goals** | Reduce energy cost by 15%; satisfy brand sustainability targets; avoid guest comfort complaints |
| **Frustrations** | Monthly utility bill gives no detail; energy consultant reports are 6 months stale; staff forgets to adjust HVAC for empty event rooms |
| **Tech comfort** | Moderate — uses PMS and revenue management software daily |
| **Key feature use** | Dashboard overview, energy cost breakdown, monthly reports, recommendation approval |

### Persona 2 — Facility Manager (Carlos)

> **PURPOSE:** Represents the daily power user — the person who lives in the platform 8 hours/day. UX, drill-down capability, and real-time data matter most to this persona.

| Field | Detail |
|-------|--------|
| **Role** | Chief Engineer, manages HVAC, lighting, and BMS for a 3-building office campus |
| **Goals** | Prevent equipment failures; optimize HVAC schedules; respond to comfort complaints before they escalate |
| **Frustrations** | BMS interface is from 2008; no remote access; no predictive alerts; manually checks equipment logs daily |
| **Tech comfort** | High — comfortable with BMS, BACnet, Modbus, building automation |
| **Key feature use** | Zone-level monitoring, HVAC status, anomaly alerts, equipment health, sensor drill-down |

### Persona 3 — Sustainability Director (Maren)

> **PURPOSE:** Represents the compliance and reporting user — drives requirements for carbon tracking (Phase 0 analytics), PDF reports (Phase 4), and ESG integrations (Phase 8).

| Field | Detail |
|-------|--------|
| **Role** | VP Sustainability for a hospitality group with 12 properties |
| **Goals** | Produce accurate Scope 1 & 2 carbon reports; track YoY energy reduction; benchmark properties |
| **Frustrations** | Collects data manually via spreadsheets; emission factors are guesswork; no audit trail |
| **Tech comfort** | Moderate — uses Excel, BI tools, ESG reporting platforms |
| **Key feature use** | Carbon emissions dashboard, portfolio benchmarking, export reports, API for ESG integration |

### Persona 4 — Residential Prosumer (Jake)

> **PURPOSE:** Represents the P2P energy seller (Phase 9). A completely different user type from commercial building operators — drives the marketplace, wallet, and automated trading rule features.

| Field | Detail |
|-------|--------|
| **Role** | Homeowner with 8 kW rooftop solar array + 13.5 kWh home battery (e.g., Tesla Powerwall) |
| **Goals** | Maximize return on solar investment; sell excess energy to neighbors at better-than-grid rates; reduce reliance on utility company |
| **Frustrations** | Net metering pays wholesale rates (3–5¢/kWh) for exported energy while neighbors buy at retail (15–30¢/kWh); no visibility into when his battery is most valuable; cumbersome utility paperwork |
| **Tech comfort** | High — uses smart home apps, monitors solar via manufacturer app, comfortable with digital payments |
| **Key feature use** | P2P marketplace, energy wallet, production/consumption dashboard, automated sell rules, neighbor matching, settlement history |

### Persona 5 — Energy Buyer / Neighbor (Diana)

> **PURPOSE:** Represents the P2P energy buyer (Phase 9). The demand side of the marketplace — drives the browse/buy UX, auto-buy rules, and the "cheaper than grid" value proposition.

| Field | Detail |
|-------|--------|
| **Role** | Renter in a townhouse community, no solar panels, environmentally conscious |
| **Goals** | Buy cheaper, cleaner energy from local producers instead of full retail grid rate; support neighborhood sustainability |
| **Frustrations** | Cannot install solar (rental); utility rate keeps increasing; wants green energy but community solar waitlists are long |
| **Tech comfort** | Moderate — uses mobile payment apps, online banking |
| **Key feature use** | Browse local energy offers, auto-buy at price threshold, consumption dashboard, payment history, carbon offset tracking |

---

## 5. Phase Roadmap Overview

> **PURPOSE:** Give a single-glance timeline so anyone can see the full journey from prototype to enterprise platform. Each phase is sequenced to build on the previous one — skipping phases creates missing dependencies.

| Phase | Name | Duration | Key Deliverable |
|-------|------|----------|----------------|
| **0** | Foundation | ✅ Complete | Working full-stack prototype with CRUD, auth, sensors, analytics, dashboard |
| **1** | Production Hardening | 3 weeks | Pagination, error handling, logging, input validation, created_at/updated_at, CORS config, test coverage with PostgreSQL |
| **2** | Real-Time Intelligence | 4 weeks | WebSocket live updates, Redis caching, continuous aggregates, configurable alert rules, notification system |
| **3** | AI Optimization Engine | 4 weeks | ML-based anomaly detection, energy demand forecasting (Prophet/LSTM), automated HVAC optimization recommendations |
| **4** | Billing & Cost Analytics | 3 weeks | Tariff configuration, cost-per-zone calculation, utility bill reconciliation, monthly cost reports, PDF export |
| **5** | Multi-Tenant & Organizations | 3 weeks | Organization → Building hierarchy, tenant isolation, API key management, admin portal, onboarding flow |
| **6** | Guest Comfort & Occupancy | 3 weeks | Occupancy-driven HVAC control, comfort scoring, PMS integration, guest room energy profiles |
| **7** | Integrations & Protocols | 4 weeks | MQTT ingestion, BACnet gateway, Modbus adapter, webhook system, third-party BMS integration |
| **8** | Scale, Compliance & Marketplace | 4 weeks | Multi-region deployment, GDPR/SOC2 compliance, partner API, white-label dashboard, app marketplace |
| **9** | Peer-to-Peer Energy Trading | 5 weeks | Prosumer onboarding, energy wallet & ledger, local marketplace with order matching, smart meter integration, settlement engine, neighbor discovery |

**Total estimated timeline: ~33 weeks from Phase 1 start**

---

## 6. Phase 0 — Foundation (COMPLETE)

> **PURPOSE:** Document the completed baseline so all subsequent phases have a clear starting point. This section is a reference, not a work item — it answers "what do we already have?" for any new contributor.

### What Was Built

> **PURPOSE:** Itemized inventory of every working component. If it's not listed here, it doesn't exist yet and must be built in a future phase.

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI backend | ✅ | Async Python 3.12, Pydantic v2 schemas, OpenAPI docs |
| PostgreSQL + TimescaleDB | ✅ | 3 hypertables (sensor_readings, hvac_status, energy_meter), Alembic migrations |
| JWT Authentication | ✅ | bcrypt password hashing, HS256 tokens, role-based access (admin, facility_manager, technician) |
| Building/Zone CRUD | ✅ | Full CRUD with UUID PKs, cascade deletes, partial updates |
| Sensor Data Ingestion | ✅ | Bulk insert endpoint, time-range queries with filters |
| HVAC Status Tracking | ✅ | Device status ingestion and query |
| Energy Meter Data | ✅ | kWh consumption tracking with voltage/current |
| Forecasts & Recommendations | ✅ | CRUD with lifecycle (pending → approved → applied → rejected) |
| Analytics Engine | ✅ | Energy summary (time_bucket), carbon emissions, z-score anomaly detection |
| React Dashboard | ✅ | Login, building selector, stat cards, temperature chart (Recharts), 7 pages |
| Docker Compose | ✅ | DB + API + Frontend services, health checks, named volumes |
| CI/CD | ✅ | GitHub Actions: backend tests, frontend type-check + build, Docker build |
| Test Suite | ✅ | pytest-asyncio, in-memory SQLite, auth/CRUD/sensor tests |

### Phase 0 Architecture

> **PURPOSE:** Visual map of how existing components connect. Each phase adds to this diagram — it serves as the architectural baseline that developers can extend without breaking existing flows.

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React + Vite + Tailwind)  :3000              │
│  ├── Login Page                                          │
│  ├── Dashboard (stat cards, temperature chart)           │
│  ├── Buildings / Zones / Sensors / HVAC pages            │
│  ├── Forecasts / Recommendations pages                   │
│  └── Analytics page                                      │
└─────────────────┬───────────────────────────────────────┘
                  │ /api/v1/*
┌─────────────────▼───────────────────────────────────────┐
│  Backend (FastAPI)  :8000                                │
│  ├── Auth (JWT + RBAC)                                   │
│  ├── Routes → Services → Models                          │
│  └── Analytics Service (time_bucket, z-score)            │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│  PostgreSQL 16 + TimescaleDB  :5433                      │
│  ├── buildings, zones, users (relational)                 │
│  ├── forecasts, recommendations (relational)             │
│  └── sensor_readings, hvac_status, energy_meter (hyper)  │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Phase 1 — Production Hardening

> **PURPOSE:** The prototype works in a demo but would fail under real traffic, real users, and real errors. This phase closes every gap between "it works on my machine" and "it survives production." No new features — only reliability, observability, and correctness.

**Goal:** Make the existing codebase production-worthy. Fix known issues, add missing fundamentals, increase test confidence.

**Duration:** 3 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **1.1 Pagination** — Prevent out-of-memory crashes and browser freezes when tables grow to thousands of rows. No list endpoint should ever return an unbounded result set.
> - **1.2 Input validation & error handling** — Garbage-in-garbage-out protection. Sensors can send corrupt data; users can submit malformed requests. Structured errors make debugging possible for both frontend devs and API consumers.
> - **1.3 `created_at` / `updated_at`** — Every record must be auditable. "When was this building added?" and "When was this user last modified?" are basic questions that unanswered created_at/updated_at columns answer.
> - **1.4 Structured logging** — When a user reports "the API is slow," you need request_id, user_id, and duration_ms to diagnose it. Unstructured text logs are unsearchable at scale.
> - **1.5 CORS from environment** — Hardcoded `allow_origins=*` is a security vulnerability. Default JWT secrets in production are a breach waiting to happen. This forces secure configuration before deployment.
> - **1.6 PostgreSQL test suite** — SQLite hides TimescaleDB-specific bugs (time_bucket, hypertables, enums). Tests must run against the real database engine to catch real bugs.
> - **1.7 Test coverage ≥ 80%** — Confidence that changes don't break existing features. Coverage below 80% means large parts of the codebase are untested and fragile.
> - **1.8 API rate limiting** — Prevents a single misbehaving client from overwhelming the API. Protects the database from query storms. Required before any public-facing deployment.
> - **1.9 Health check with DB ping** — Load balancers and orchestrators need to know if the service is healthy. A health check that doesn't ping the DB gives false confidence — the API may be running but unable to serve data.
> - **1.10 Frontend route protection** — Without this, unauthenticated users see broken dashboard pages with empty data. Token expiry detection prevents silent failures. Error boundaries prevent full-page crashes from a single component error.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 1.1 | **Pagination on all list endpoints** | Buildings, users, zones, recommendations, forecasts return cursor-based or offset pagination. Default limit=50, max=500. Response includes `total_count` and `next_cursor`. |
| 1.2 | **Input validation & error handling** | Sensor values validated against sane ranges per type (temperature: -50 to 80°C, humidity: 0–100%, etc.). Duplicate email returns 409 Conflict. Invalid FK returns 422. Global exception handler returns structured `{error, code, request_id}`. |
| 1.3 | **`created_at` / `updated_at` on all models** | All relational tables gain `created_at` (server default `now()`) and `updated_at` (auto-updated on modification) columns via Alembic migration. |
| 1.4 | **Structured logging** | JSON-formatted logs with `request_id`, `user_id`, `duration_ms` on every request. Log level configurable via environment variable. |
| 1.5 | **CORS from environment** | `ALLOWED_ORIGINS` env var (comma-separated) replaces hardcoded `"*"`. Startup assertion fails if `JWT_SECRET_KEY` is the default value and `DEBUG=false`. |
| 1.6 | **PostgreSQL test suite** | Replace SQLite test backend with `testcontainers-python` using a real PostgreSQL + TimescaleDB container. All analytics tests (time_bucket, anomaly detection) now run against the real DB engine. |
| 1.7 | **Test coverage ≥ 80%** | Add tests for: all service methods, error cases (404, 409, 422), role-based access (403), pagination, analytics endpoints. Coverage measured by pytest-cov. |
| 1.8 | **API rate limiting** | Configurable per-user rate limit (default: 100 req/min). Returns 429 with `Retry-After` header. Implemented as FastAPI middleware with in-memory sliding window (Redis-backed in Phase 2). |
| 1.9 | **Health check with DB ping** | `/health` returns `{"status": "ok", "db": "ok", "version": "0.2.0"}`. If DB is unreachable, returns `{"status": "degraded", "db": "unreachable"}` with HTTP 200 (not 503 — avoids restart loops). |
| 1.10 | **Frontend route protection** | Unauthenticated users redirected to `/login`. Token expiry detected on API 401 response. Building auto-selected on page load if only one exists. Error boundaries on all pages. |

### Phase 1 Graduation Gate

> **PURPOSE:** Binary pass/fail checklist. If any item is unchecked, Phase 1 is not complete and Phase 2 should not start. Prevents "good enough" from accumulating technical debt.

- [ ] All existing tests pass on PostgreSQL + TimescaleDB (not SQLite)
- [ ] Test coverage ≥ 80% as measured by pytest-cov
- [ ] No endpoint returns unbounded result sets
- [ ] Structured JSON logs visible in `docker compose logs api`
- [ ] Startup fails if JWT secret is default and DEBUG is false

---

## 8. Phase 2 — Real-Time Intelligence

> **PURPOSE:** Phase 0 shows historical data; Phase 2 makes the platform live. This is the shift from "look at what happened yesterday" to "see what's happening right now and get alerted when something goes wrong." This is the feature set that makes the platform sticky — users check it daily instead of monthly.

**Goal:** Transform from a batch data viewer into a real-time monitoring platform. Users see sensor data update live. Alerts fire automatically when anomalies occur.

**Duration:** 4 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **2.1 Redis integration** — The database is too slow for real-time dashboards (50–200ms per query). Redis caches the latest reading per sensor for sub-10ms access. Also becomes the rate-limit store and WebSocket pub/sub backbone.
> - **2.2 WebSocket real-time updates** — HTTP polling wastes bandwidth and adds 30-second latency. WebSockets push data to the browser the instant it arrives, making the dashboard feel alive.
> - **2.3 Continuous aggregates** — Querying raw sensor_readings for a 7-day chart scans millions of rows. Continuous aggregates pre-compute hourly and daily summaries, making dashboard queries 100× faster.
> - **2.4 Configurable alert rules** — Different buildings have different thresholds. A server room flagging 30°C is critical; a parking garage at 30°C is normal. Rules let facility managers define what "abnormal" means for their context.
> - **2.5 Alert evaluation engine** — Rules without enforcement are useless. The background engine checks every 60 seconds and creates alert records automatically — no human needs to watch a dashboard 24/7.
> - **2.6 Notification system** — Alerts that sit in a database unnoticed don't save energy. Notifications push alerts to the right person via the right channel (in-app, email) based on severity and their preferences.
> - **2.7 Data retention policy** — Raw 15-second sensor data accumulates at ~2 GB/day for a large building. Without automated cleanup, storage costs grow unbounded. Tiered retention keeps recent data detailed and old data summarized.
> - **2.8 Device health monitoring** — A sensor that stopped reporting 2 hours ago is worse than no sensor — it gives false confidence. Staleness tracking surfaces dead sensors before they cause blind spots.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 2.1 | **Redis integration** | Redis 7 added to docker-compose. Latest sensor reading per device cached in Redis with 5-min TTL. `GET /api/v1/sensors/latest?building_id=` serves from cache (< 10ms p95). |
| 2.2 | **WebSocket real-time updates** | Backend broadcasts sensor readings via WebSocket (FastAPI WebSocket endpoint). Frontend dashboard subscribes per building. New readings appear on chart within 5 seconds. Fallback: HTTP polling at 30s. |
| 2.3 | **Continuous aggregates** | TimescaleDB continuous aggregates: `sensor_readings_hourly` and `sensor_readings_daily`. Materialized within 30 seconds of new data. Dashboard queries > 24h use hourly aggregates. Queries > 7d use daily. |
| 2.4 | **Configurable alert rules** | New `alert_rules` table: `{id, building_id, zone_id, sensor_type, condition (gt/lt/eq), threshold, severity, enabled}`. New `alerts` table: `{id, rule_id, triggered_at, value, acknowledged_at}`. API: CRUD on rules, list/acknowledge alerts. |
| 2.5 | **Alert evaluation engine** | Background task (asyncio / APScheduler) evaluates rules every 60 seconds against latest readings. Matching readings create alert records. |
| 2.6 | **Notification system** | Alerts trigger notifications. Phase 2: in-app notification bell + optional email (SendGrid). Notification preferences per user (email on/off, severity filter). |
| 2.7 | **Data retention policy** | Raw sensor_readings auto-dropped after 90 days via TimescaleDB retention policy. Hourly aggregates retained 1 year. Daily aggregates retained indefinitely. |
| 2.8 | **Device health monitoring** | Dashboard shows "last seen" per sensor with staleness indicator (green < 5 min, yellow < 30 min, red > 30 min). API: `GET /api/v1/sensors/health?building_id=` returns per-sensor status. |

### Phase 2 Architecture Addition

> **PURPOSE:** Show exactly what new infrastructure Phase 2 adds to the existing stack. Redis is the only new service — everything else extends existing components.

```
┌───────────────────────────────────────┐
│  Redis 7  :6379                        │
│  ├── device:latest:{sensor_id}  (5m)   │
│  ├── ratelimit:{user_id}:{min}         │
│  └── channel:building:{id}:telemetry   │
└───────────────────────────────────────┘
```

### Phase 2 Graduation Gate

> **PURPOSE:** Prove real-time works end-to-end — data flows from sensor insert to dashboard chart within 5 seconds, and alerts fire within 90 seconds of a breach.

- [ ] Dashboard chart updates within 5 seconds of sensor data insert (WebSocket)
- [ ] Alert rule fires within 90 seconds of threshold breach
- [ ] `/api/v1/sensors/latest` returns in < 10ms from Redis
- [ ] 90-day retention policy actively dropping old chunks
- [ ] At least 3 alert rules configured and tested end-to-end

---

## 9. Phase 3 — AI Optimization Engine

> **PURPOSE:** This is where the product earns its "AI" label. Phases 0–2 show data; Phase 3 interprets data and tells operators what to do before problems happen. This is the core differentiator from traditional BMS dashboards — predictive, not reactive.

**Goal:** Move from reactive monitoring to proactive optimization. The platform predicts energy demand, detects complex anomalies that statistical methods miss, and generates HVAC optimization recommendations automatically.

**Duration:** 4 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **3.1 ML anomaly detection** — The z-score method from Phase 0 catches obvious spikes but misses subtle patterns (gradual drift, multi-variable correlations). Isolation Forest finds anomalies that humans and simple statistics can't.
> - **3.2 Energy demand forecasting** — You can't optimize what you can't predict. Forecasting next-24h demand lets the optimizer pre-position HVAC, shift loads to cheap tariff periods, and avoid demand charge penalties.
> - **3.3 HVAC optimization engine** — The money-saving feature. Instead of running HVAC on fixed schedules, the optimizer generates per-zone-per-hour setpoint recommendations that reduce energy use by 10%+ while maintaining comfort.
> - **3.4 Weather data integration** — Weather is the #1 predictor of energy demand. Without it, forecasts are blind guesses. Temperature, humidity, and solar radiation feed directly into the ML models.
> - **3.5 Recommendation auto-generation** — Manual analysis doesn't scale. The nightly batch job replaces a human energy consultant — it analyzes every zone in every building and generates actionable recommendations with estimated dollar savings.
> - **3.6 Model training pipeline** — ML models degrade over time as building usage patterns change. The training pipeline allows retraining when accuracy drops, keeping predictions fresh and reliable.
> - **3.7 Savings tracker** — Proves ROI. After a recommendation is applied, the system measures actual savings vs predicted savings. This is how customers justify continued subscription and how sales teams close new deals.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 3.1 | **ML anomaly detection** | Replace z-score method with Isolation Forest (scikit-learn). Trained per building on 30+ days of historical data. Detects: equipment drift, unusual consumption patterns, sensor failure modes. False positive rate < 5%. |
| 3.2 | **Energy demand forecasting** | Prophet or LSTM model predicts next-24h energy consumption per building at hourly granularity. MAPE < 15% on 7-day test set. Forecasts stored in `forecasts` table with `confidence_low`, `confidence_high` bounds. |
| 3.3 | **HVAC optimization engine** | Rule-based optimizer (Phase 3 — ML optimizer in Phase 6): given occupancy schedule + weather forecast + energy forecast → generate setpoint recommendations per zone per hour. Target: 10% reduction in HVAC energy vs fixed schedule baseline. |
| 3.4 | **Weather data integration** | Ingest hourly weather data (temperature, humidity, solar radiation) from OpenWeatherMap API. Stored in `weather_data` hypertable. Used as feature in forecasting models. |
| 3.5 | **Recommendation auto-generation** | Nightly batch job runs optimizer → generates recommendations for next day. Recommendations appear in dashboard with estimated savings (kWh and $). Facility manager approves/rejects via UI. |
| 3.6 | **Model training pipeline** | CLI command `python -m app.ml.train --building-id=X` trains/retrains models. Model artifacts stored locally (Phase 3) or S3 (Phase 8). Training metrics logged. Automatic retraining triggered when prediction error exceeds threshold. |
| 3.7 | **Savings tracker** | After a recommendation is applied, system measures actual vs predicted savings over next 7 days. Dashboard shows cumulative savings (kWh, $, kg CO2) per building per month. |

### Phase 3 Graduation Gate

> **PURPOSE:** Prove that AI delivers measurable value — forecasts are accurate (MAPE < 15%), anomaly detection finds real issues, and the optimizer produces valid recommendations that track actual savings.

- [ ] Demand forecast running for at least 1 building with MAPE < 15%
- [ ] ML anomaly detection finds at least 1 issue that z-score missed on historical data
- [ ] HVAC optimizer generates valid recommendations for a 7-day window
- [ ] Savings tracker shows actual vs predicted for at least 1 applied recommendation

---

## 10. Phase 4 — Billing & Cost Analytics

> **PURPOSE:** Energy data becomes commercially meaningful only when expressed in currency. This phase transforms the platform from a technical monitoring tool into a financial management tool — the language that executives, CFOs, and property owners actually speak.

**Goal:** Translate energy data into money. Building managers think in dollars, not kilowatt-hours.

**Duration:** 3 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **4.1 Tariff configuration** — Utility rates are complex (time-of-use, tiered, demand charges). Without accurate tariff modeling, cost calculations are meaningless. This is the foundation for all cost analytics.
> - **4.2 Cost calculation engine** — Converts raw kWh readings into dollar amounts per zone per hour. Makes energy cost visible at the granularity where managers can actually take action (e.g., "Floor 3 costs $200/day more than Floor 2").
> - **4.3 Cost analytics API** — Powers cost dashboards and reports. Answers: "How much did Building A cost this month?", "Which zone is most expensive?", "Is demand charge driving the bill?"
> - **4.4 Utility bill reconciliation** — Catches billing errors. Utilities overcharge more often than you'd think. Comparing platform-calculated costs against actual bills saves customers money and builds trust.
> - **4.5 Monthly energy report (PDF)** — The deliverable that gets printed and put on the GM's desk. Automated reports replace expensive consultant reports and demonstrate ongoing value every month.
> - **4.6 Budget tracking** — Turns reactive "we overspent" into proactive "we're on track to overspend by 12% — here's why." Budget alerts create urgency for adopting optimization recommendations.
> - **4.7 Cost allocation** — Multi-tenant buildings need to charge tenants fairly. Zone-level metering + tariff modeling enables accurate, defensible cost allocation instead of square-footage estimates.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 4.1 | **Tariff configuration** | `tariffs` table: supports flat rate, time-of-use (up to 8 blocks/day), tiered, and demand charge structures. Versioned with `effective_from` date. CRUD API. |
| 4.2 | **Cost calculation engine** | Background job applies active tariff to hourly energy_meter data → produces `energy_costs` records (zone, hour, kwh, cost_cents). All monetary values stored as BIGINT (integer cents). |
| 4.3 | **Cost analytics API** | `GET /api/v1/buildings/{id}/cost-summary?start=&end=` returns: total cost, cost by zone, cost by time-of-day, cost vs previous period, demand charges. |
| 4.4 | **Utility bill reconciliation** | CSV upload of utility bill line items. System compares utility charges against platform-calculated costs. Discrepancies > 5% flagged for review. |
| 4.5 | **Monthly energy report (PDF)** | Auto-generated PDF report per building: energy summary, cost breakdown, carbon emissions, top recommendations, month-over-month comparison. Generated via WeasyPrint. Downloadable via API and email. |
| 4.6 | **Budget tracking** | Building managers set annual energy budget. Dashboard shows budget consumed YTD, projected year-end, and variance. Alert when projected spend exceeds budget by > 10%. |
| 4.7 | **Cost allocation** | For multi-tenant buildings: allocate energy costs to tenants based on zone-level metering. Exportable as CSV for accounting integration. |

### Phase 4 Graduation Gate

> **PURPOSE:** Verify that cost calculations are accurate (within 1% of manual), reports generate correctly, and the utility bill reconciliation actually catches discrepancies — not just theoretical accuracy but proven accuracy on real data.

- [ ] Cost calculation matches manual spreadsheet within 1% for 3+ months of data
- [ ] Monthly PDF report generates correctly for at least 2 buildings
- [ ] Utility bill upload detects at least 1 discrepancy in test data
- [ ] Budget alert fires when projected spend exceeds threshold

---

## 11. Phase 5 — Multi-Tenant & Organizations

> **PURPOSE:** Convert the platform from a single-customer installation into a scalable SaaS business. Without multi-tenancy, every customer needs a separate deployment — that doesn't scale past 5 customers. This phase is the prerequisite for commercial viability.

**Goal:** Support multiple organizations on a single platform instance. Each organization sees only their own data. Enable SaaS deployment.

**Duration:** 3 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **5.1 Organization model** — The top-level entity that owns buildings, users, and billing. Without this, there's no concept of "customer" — just a flat pool of buildings.
> - **5.2 Tenant data isolation** — The most critical SaaS requirement. If Customer A can see Customer B's data, the product is dead. Row-Level Security enforces isolation at the database level — even a bug in the API can't leak data.
> - **5.3 User-Organization binding** — Users belong to an org, not a building. A facility manager for a hotel chain needs access to all 12 properties, not just one.
> - **5.4 API key management** — Sensors and IoT gateways can't authenticate with username/password. Machine-to-machine API keys with scopes and expiration enable automated data ingestion without human login.
> - **5.5 Admin portal** — Platform operators (us) need to manage customers, monitor usage, and troubleshoot. A super-admin view separate from tenant dashboards.
> - **5.6 Self-service onboarding** — If every new customer requires a support call, onboarding cost eats margins. A guided wizard gets customers from signup to first data in under 30 minutes.
> - **5.7 Auth0 integration** — Custom JWT implementation doesn't support SSO, MFA, or enterprise identity providers. Auth0 provides these out of the box and is trusted by enterprise procurement teams.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 5.1 | **Organization model** | New `organizations` table: `{id, name, slug, plan, timezone, country_code}`. Buildings gain `org_id` FK. All queries scoped by org. |
| 5.2 | **Tenant data isolation** | PostgreSQL Row-Level Security (RLS) policies on all tables. User can only query data belonging to their organization. API returns 404 (not 403) for cross-org resource access — no information leakage. |
| 5.3 | **User-Organization binding** | Users belong to an organization (not a building). `building_id` FK on users replaced with `org_id`. Users can access all buildings within their org. |
| 5.4 | **API key management** | Organizations can generate API keys for machine-to-machine access (sensor gateways, integrations). API keys have scopes (read, write, admin) and expiration. Tracked in `api_keys` table. |
| 5.5 | **Admin portal** | Super-admin dashboard for platform operators: list orgs, create orgs, view usage metrics, manage plans. Separate from tenant dashboard. |
| 5.6 | **Self-service onboarding** | New org → invite link → create account → add first building → add first sensors flow. Guided wizard in the frontend. Under 30 minutes from signup to first data. |
| 5.7 | **Auth0 integration** | Replace custom JWT with Auth0. SSO support (Google, Microsoft). Organization-scoped login. JWT claims include `org_id` and `role`. |

### Phase 5 Graduation Gate

> **PURPOSE:** Prove tenant isolation is bulletproof (verified with direct SQL, not just API tests) and that a real customer can onboard without engineering support.

- [ ] Two organizations with separate data; User A cannot see Org B data
- [ ] RLS policies verified with direct SQL (bypass API)
- [ ] API key used to push sensor data without user JWT
- [ ] New organization onboarded end-to-end in < 30 minutes via wizard

---

## 12. Phase 6 — Guest Comfort & Occupancy

> **PURPOSE:** Hotels are the primary target market, and their #1 constraint is "save energy without making guests uncomfortable." This phase adds the occupancy intelligence that makes HVAC optimization hotel-safe — you never cool down a room with a guest in it.

**Goal:** Hotel-specific intelligence. Optimize energy based on actual room occupancy and guest preferences while maintaining comfort.

**Duration:** 3 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **6.1 Occupancy tracking** — The missing input variable. HVAC optimization without occupancy data is guesswork. Knowing which rooms are occupied (and which aren't) enables 25%+ HVAC savings on unoccupied spaces.
> - **6.2 PMS integration** — Hotel PMS (Opera, etc.) already knows check-in/check-out times. Tapping into this existing data is cheaper and more reliable than installing occupancy sensors in every room.
> - **6.3 Occupancy-driven HVAC** — The flagship hotel feature. Pre-condition before arrival, setback after checkout, deep setback for unbooked rooms. This is where the 25% HVAC savings come from.
> - **6.4 Comfort scoring** — Quantifies guest experience (0–100) from sensor data. Prevents the optimizer from saving energy at the expense of comfort. Alert when score drops below 70 so staff can intervene before a complaint.
> - **6.5 Guest room energy profile** — Identifies rooms with equipment problems (e.g., "Room 412 uses 3× the average — likely a malfunctioning PTAC unit"). Also enables per-room-night cost accounting for revenue management.
> - **6.6 Event-driven scheduling** — Conference rooms and ballrooms have variable schedules. Integrating with calendars ensures HVAC pre-conditions for a 200-person banquet and shuts down after the last attendee leaves.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 6.1 | **Occupancy tracking** | New `occupancy_events` hypertable: `{time, zone_id, occupancy_count, source}`. Sources: PIR sensors, door sensors, PMS check-in/check-out, CO2 estimation. |
| 6.2 | **PMS integration** | REST API adapter for hotel Property Management Systems. Receive check-in, check-out, and room assignment events. Supported: Opera PMS (Oracle) via webhook, generic REST. Map PMS room IDs to platform zone IDs. |
| 6.3 | **Occupancy-driven HVAC** | When room is unoccupied: setback temperature to ±4°C from setpoint. When guest checks in: pre-condition room 30 minutes before arrival. When guest checks out: enter deep setback until next arrival. Target: 25% HVAC savings on unoccupied rooms. |
| 6.4 | **Comfort scoring** | Per-zone comfort score (0–100) based on: temperature deviation from setpoint, humidity range (40–60%), CO2 level (< 1000 ppm), lighting level. Score visible in dashboard. Alert when comfort drops below 70. |
| 6.5 | **Guest room energy profile** | Track energy consumption per room per stay. Show energy cost per occupied room-night. Benchmark against hotel average. Identify high-consumption rooms (potential equipment issues). |
| 6.6 | **Event-driven scheduling** | Conference rooms, ballrooms, restaurants: define schedule (Google Calendar / manual). Auto-condition before event start. Auto-setback after event end. |

### Phase 6 Graduation Gate

> **PURPOSE:** Prove the hotel-specific features work in a real operational flow — checkout triggers setback within 15 minutes, pre-conditioning starts before arrival, and comfort scoring matches actual conditions.

- [ ] Unoccupied room HVAC setback triggers within 15 minutes of checkout
- [ ] Pre-conditioning starts 30 minutes before check-in
- [ ] Comfort score accurately reflects measured conditions (manual verification)
- [ ] At least 1 PMS integration receiving live occupancy events

---

## 13. Phase 7 — Integrations & Protocols

> **PURPOSE:** Until now, data entry is manual or via REST API. Real buildings have MQTT sensors, BACnet building management systems, and Modbus energy meters. This phase connects the platform to the physical world — no more demo data.

**Goal:** Connect to real building hardware. Move from manual data entry to automated device ingestion.

**Duration:** 4 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **7.1 MQTT ingestion gateway** — MQTT is the IoT standard. Most modern sensors and gateways speak MQTT. This unlocks plug-and-play connectivity with thousands of off-the-shelf devices.
> - **7.2 BACnet gateway** — BACnet is the dominant protocol in commercial building automation (HVAC controllers, chillers, AHUs). Reading BACnet means controlling the systems that consume 40–60% of building energy.
> - **7.3 Modbus adapter** — Modbus is the protocol for energy meters, sub-meters, and industrial equipment. This enables granular sub-metering without replacing existing hardware.
> - **7.4 Webhook system** — Outbound webhooks let customers integrate platform events (alerts, recommendations) into their existing workflows (Slack, PagerDuty, ticketing systems) without custom code.
> - **7.5 Device registry** — As buildings connect dozens to hundreds of devices, a registry tracks what's installed, where, and how it's configured. Without this, device management is chaos.
> - **7.6 Protocol abstraction layer** — Different protocols produce different data formats. The canonical telemetry event normalizes everything so the rest of the platform doesn't care whether data came from MQTT, BACnet, or Modbus.
> - **7.7 Stream processing** — Raw telemetry needs validation (range checks), normalization (unit conversion), and quality flagging before storage. This async worker ensures only clean, normalized data enters the database.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 7.1 | **MQTT ingestion gateway** | MQTT 3.1.1 broker (EMQX) accepts sensor telemetry on port 8883 (TLS). Pre-shared key authentication per device. Messages normalized to canonical schema and inserted into TimescaleDB. Latency: MQTT publish to DB < 500ms. |
| 7.2 | **BACnet gateway** | BACnet/IP reader polls BMS controllers at configurable intervals (default 60s). Reads analog/binary values, trends, schedules. Maps BACnet object IDs to platform sensor IDs via configuration. |
| 7.3 | **Modbus adapter** | Modbus TCP client reads registers from energy meters and sub-meters. Register map configurable per meter model. Supports holding registers and input registers. |
| 7.4 | **Webhook system** | Outbound webhooks: POST event data to customer endpoints on alert, recommendation, or threshold breach. Configurable per org. Retry with exponential backoff (3 attempts). Signed payloads (HMAC-SHA256). |
| 7.5 | **Device registry** | New `devices` table: `{id, building_id, zone_id, device_type, protocol, external_id, manufacturer, model, config (JSONB encrypted)}`. Device CRUD API. Auto-provisioning via MQTT first-connect. |
| 7.6 | **Protocol abstraction layer** | Canonical telemetry event: `{device_id, org_id, time, metric, value, unit, quality, source_protocol}`. All protocol adapters produce this format. Quality flags: 1=good, 2=estimated, 3=invalid. |
| 7.7 | **Stream processing** | Async worker consumes incoming telemetry → validates ranges → normalizes units (all SI) → detects clock drift → flags quality → writes to TimescaleDB + publishes to WebSocket. Processing latency < 1 second. |

### Phase 7 Graduation Gate

> **PURPOSE:** Prove real hardware connectivity — MQTT data visible in 2 seconds, BACnet reads from a real controller, webhooks deliver alerts to external endpoints. No more simulated data.

- [ ] MQTT sensor publishes data visible in dashboard within 2 seconds
- [ ] BACnet gateway successfully reads from at least 1 real BMS controller
- [ ] Outbound webhook delivers alert to test endpoint within 30 seconds
- [ ] Quality flags correctly mark out-of-range readings as invalid

---

## 14. Phase 8 — Scale, Compliance & Marketplace

> **PURPOSE:** Transform from a product into a platform. Enterprise customers require multi-region data residency, SOC 2 compliance, and partner API access. Without this phase, the product is limited to SMB customers in a single geography.

**Goal:** Enterprise-ready platform. Multi-region deployment, regulatory compliance, partner ecosystem.

**Duration:** 4 weeks

### Deliverables

> **PURPOSE of each deliverable:**
> - **8.1 Kubernetes deployment** — Docker Compose doesn't scale past a single server. Kubernetes enables horizontal auto-scaling, zero-downtime deployments, and infrastructure-as-code across multiple environments.
> - **8.2 Multi-region support** — EU customers require data stored in Europe (GDPR). US government buildings require US data residency. Multi-region is a sales prerequisite for international expansion.
> - **8.3 GDPR compliance** — Legal requirement for any EU customer. Right to deletion, data processing agreements, and audit logs are table stakes for enterprise sales in Europe.
> - **8.4 SOC 2 Type II readiness** — Enterprise procurement won't sign without SOC 2. This isn't optional — it's the price of admission for Fortune 500 customers and large hotel chains.
> - **8.5 Partner API** — Enables an ecosystem of third-party integrations (energy consultants, BMS vendors, ESG platforms) that extend the platform's value without building everything in-house.
> - **8.6 White-label dashboard** — Large property management companies want the platform under their brand. White-labeling enables channel partnerships where partners resell the platform.
> - **8.7 App marketplace** — Third-party plugins extend the platform (custom report generators, niche BMS adapters, specialized alert channels). Reduces development burden and creates a partner ecosystem.
> - **8.8 Portfolio benchmarking** — Organizations with 10+ buildings need to compare performance. "Which building is most efficient?" and "Which property improved most this quarter?" are executive-level questions this answers.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 8.1 | **Kubernetes deployment** | Helm charts for all services. Horizontal pod autoscaling on API and worker. StatefulSet for PostgreSQL with Patroni failover. Tested on AWS EKS. |
| 8.2 | **Multi-region support** | Data residency per organization (EU, US). Database per region with cross-region admin API. Latency < 200ms for dashboard loads in target region. |
| 8.3 | **GDPR compliance** | Right to deletion (org data purge). Data processing agreement template. Audit log for all data access. Personal data encrypted at rest. Cookie consent on dashboard. |
| 8.4 | **SOC 2 Type II readiness** | Access controls documented. Change management via CI/CD only. Audit logs immutable. Encryption in transit (TLS 1.2+) and at rest (AES-256). Vendor assessment questionnaire complete. |
| 8.5 | **Partner API** | Versioned REST API with OAuth2 client credentials. Rate-limited and metered per partner. OpenAPI spec published. SDK for Python and JavaScript. |
| 8.6 | **White-label dashboard** | Customizable logo, color scheme, domain per organization. CSS theming via configuration (no code changes). Custom email sender domain. |
| 8.7 | **App marketplace** | Plugin system for third-party integrations (e.g., custom report generators, BMS adapters, alert channels). Plugin manifest format. Sandboxed execution. Review and approval process. |
| 8.8 | **Portfolio benchmarking** | Compare buildings within an organization: energy use intensity (EUI), cost per sq ft, comfort scores, equipment efficiency. Leaderboard view. Export for investor reporting. |

### Phase 8 Graduation Gate

> **PURPOSE:** Prove enterprise readiness — multi-region works with data residency enforced, SOC 2 evidence collection is underway, at least one partner integration uses the API, and white-label is deployed for a real customer.

- [ ] 2+ regions deployed with data residency enforced
- [ ] SOC 2 evidence collection at least 50% complete
- [ ] Partner API used by at least 1 external integration
- [ ] White-label deployed for at least 1 customer

---

## 15. Phase 9 — Peer-to-Peer Energy Trading

> **PURPOSE:** Expand the platform's addressable market from commercial buildings to residential prosumers. P2P trading is a completely new revenue stream and product category — it transforms Commercial Energy OS from a cost-reduction tool into a marketplace platform. This is the "Airbnb for electricity" vision.

**Goal:** Enable homeowners with solar panels or home batteries to sell excess energy directly to neighbors and local users, bypassing traditional utility models. Think "Airbnb for electricity" — a local energy marketplace where prosumers list surplus energy and buyers purchase it at rates better than retail grid prices.

**Duration:** 5 weeks

### Why P2P Energy Trading?

> **PURPOSE:** Justify why a commercial building energy platform should also do residential P2P. The answer: the grid is becoming bidirectional, the market opportunity is massive, and the platform's sensor/analytics infrastructure directly applies to this new use case.

The energy grid is becoming bidirectional. Millions of homes now generate electricity (solar) and store it (batteries). Today, prosumers sell excess back to the utility at wholesale rates (3–5¢/kWh) while their neighbor across the street buys from the same utility at retail (15–30¢/kWh). This 5–10× markup funds grid infrastructure neither party may need for a local transaction.

P2P trading creates a direct marketplace:
- **Sellers** earn 2–4× more than net metering for their surplus energy
- **Buyers** pay 10–40% less than retail grid rates for local clean energy
- **Platform** takes a small transaction fee (1–3%) for matching, settlement, and compliance
- **Grid** remains the backbone — P2P trades are settled virtually (no private wires needed)

### How It Works (Virtual Net Metering Model)

> **PURPOSE:** Demystify the physical mechanics. The most common question is "do you need private wires?" — the answer is no. This diagram shows that trades are virtual: the grid delivers electricity normally, the platform only handles the financial settlement.

```
┌──────────────┐                                      ┌──────────────┐
│  SELLER       │    ① Lists surplus energy            │   BUYER       │
│  (Solar +     │───────────────────────────────────▶  │  (No solar,   │
│   Battery)    │                                      │   wants cheap  │
│               │    ④ Receives payment                │   clean energy)│
│               │◀───────────────────────────────────  │               │
└──────┬───────┘                                      └──────┬───────┘
       │                                                      │
       │ ② Exports kWh                          ③ Imports kWh │
       │    to grid                                from grid   │
       ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHYSICAL ELECTRICITY GRID                        │
│  (Grid acts as the delivery infrastructure — energy flows normally) │
└─────────────────────────────────────────────────────────────────────┘
       │                                                      │
       ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMERCIAL ENERGY OS PLATFORM                     │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Marketplace │  │   Matching   │  │  Settlement  │  │  Wallet  │ │
│  │  (Offers &   │  │   Engine     │  │  Engine      │  │  & Ledger│ │
│  │   Requests)  │  │  (Price/Time │  │  (Reconcile  │  │  (Credits│ │
│  │              │  │   /Proximity)│  │   with meter) │  │   & $)   │ │
│  └─────────────┘  └─────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

Trades are **virtual**: the seller exports kWh to the grid, the buyer imports kWh from the grid, and the platform records the financial transaction. No private wires required. Settlement happens by reconciling smart meter data from both parties.

### Deliverables

> **PURPOSE of each deliverable:**
> - **9.1 Prosumer onboarding** — The entry point for residential users. Captures solar system specs, links smart meters, and gets legal agreements signed. If onboarding takes more than 15 minutes, users abandon — so it must be fast and guided.
> - **9.2 Smart meter integration** — P2P trading is meaningless without accurate production/consumption data. Smart meter reads every 15 minutes provide the ground truth for settlement. Multiple integration paths (utility API, manufacturer API, MQTT) ensure broad device compatibility.
> - **9.3 Energy wallet & ledger** — The financial backbone. Every user has an energy wallet with cash and energy credit balances. The double-entry ledger ensures every cent is accounted for — no money appears or disappears. Required for regulatory compliance and user trust.
> - **9.4 Local energy marketplace** — The core user experience. Sellers list offers, buyers browse and purchase. Geographic filtering ensures trades happen between neighbors (same grid segment). This is the "Airbnb listing page" for electricity.
> - **9.5 Order matching engine** — Automates the marketplace. Instead of buyers manually clicking "buy," the matching engine pairs compatible offers and requests based on price, time, proximity, and quantity. Runs every 15 minutes aligned with meter intervals.
> - **9.6 Settlement engine** — The most critical piece. After energy is delivered, the settlement engine reads actual meter data, calculates what was actually delivered (not just promised), handles shortfalls, deducts platform fees, and updates wallet balances. Must be idempotent — safe to re-run.
> - **9.7 Dynamic pricing engine** — Helps users price correctly. Without guidance, sellers overprice (no sales) or underprice (lost revenue). The pricing engine suggests optimal prices based on grid rates, supply/demand, weather, and historical clearing prices.
> - **9.8 Neighbor discovery & community** — Solves the cold-start problem. Users are more likely to trade with people they know. Energy communities (HOAs, neighborhoods) create trust and preferential trading. Map-based UI makes it tangible.
> - **9.9 Regulatory compliance layer** — P2P energy trading is regulated differently in every jurisdiction. This layer makes compliance rules configurable (not hardcoded) so the platform can launch in Texas, then Germany, then Australia without code changes.
> - **9.10 Trading analytics dashboard** — Users need to see their performance — revenue earned, kWh sold, money saved, carbon offset. Without dashboards, users can't evaluate whether P2P trading is worth their time.
> - **9.11 Automated trading rules** — Power users don't want to manually create offers every day. Automation rules ("sell excess above 80% battery at ≥12¢/kWh between 4–8 PM") run on autopilot. Kill switch provides safety net.

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 9.1 | **Prosumer onboarding** | Registration flow for residential users: address verification, solar system specs (capacity kW, battery kWh, inverter type), smart meter ID linking, grid connection agreement acceptance. Profile shows real-time generation, consumption, and net export. Onboarding < 15 minutes. |
| 9.2 | **Smart meter integration** | Read production and consumption data from smart meters via: (a) utility API (Green Button / ESPI standard), (b) manufacturer API (Enphase, SolarEdge, Tesla), (c) MQTT from home energy gateway. Data ingested into `meter_readings_p2p` hypertable at 15-minute intervals. |
| 9.3 | **Energy wallet & ledger** | Each user gets an energy wallet with two balances: **energy credits** (kWh available to sell) and **cash balance** (USD cents). Double-entry ledger: every trade creates debit + credit entries. Wallet supports: deposit (from bank/card via Stripe), withdrawal (to bank), and energy credit accrual (from meter readings). All monetary values in integer cents (BIGINT). |
| 9.4 | **Local energy marketplace** | Sellers create **offers**: quantity (kWh), price (¢/kWh), availability window (time range), minimum purchase, auto-renew flag. Buyers create **requests**: desired quantity, max price, preferred time window. Offers visible to buyers within configurable radius (default: 5 km). Marketplace UI shows available offers sorted by price, distance, and seller rating. |
| 9.5 | **Order matching engine** | Matching algorithm pairs offers and requests based on: (a) price compatibility (buyer max ≥ seller ask), (b) time window overlap, (c) geographic proximity, (d) available quantity. Matching runs every 15 minutes aligned with meter reading intervals. Supports partial fills — a 10 kWh offer can match 3 separate 3 kWh requests. Unmatched offers remain active until expiry. |
| 9.6 | **Settlement engine** | After each 15-minute interval: (a) read actual meter data for all active trades, (b) compare contracted kWh vs actual export/import, (c) settle at contracted price for actual delivered kWh (not contracted — actual delivery may differ), (d) handle shortfall (seller exported less than promised → partial settlement + penalty flag), (e) update wallet balances, (f) calculate platform fee (configurable, default 2%). Settlement is idempotent — safe to re-run. |
| 9.7 | **Dynamic pricing engine** | Suggest optimal sell/buy prices based on: (a) current grid retail rate, (b) time-of-use tariff period, (c) local supply/demand ratio, (d) weather forecast (solar production prediction), (e) historical clearing prices. Sellers see "suggested price" when creating offers. Buyers see "market rate" when placing requests. Optional: auto-pricing mode where platform sets price dynamically. |
| 9.8 | **Neighbor discovery & community** | Map-based UI showing nearby prosumers (privacy-preserving: show approximate location, not exact address). "Energy communities" — groups of neighbors who trade preferentially (lower fees, priority matching). Community creation, invites, and group dashboards. Leaderboard: top producers, biggest savers, greenest households. |
| 9.9 | **Regulatory compliance layer** | Configurable per jurisdiction: (a) trading license requirements, (b) maximum trading volume before utility notification, (c) tax reporting (1099 generation for US sellers earning > $600/year), (d) grid access fees passthrough, (e) renewable energy certificate (REC) tracking — each traded kWh can optionally generate/transfer a REC. Compliance rules stored as configuration, not hardcoded. |
| 9.10 | **Trading analytics dashboard** | Seller dashboard: total kWh sold, revenue earned, average sell price, production vs sold ratio, earnings projection. Buyer dashboard: total kWh bought, money saved vs grid rate, carbon offset from local clean energy. Community dashboard: total local trades, grid independence percentage, collective CO2 avoided. |
| 9.11 | **Automated trading rules** | Users configure automation: "Sell any excess above 80% battery charge at ≥ 12¢/kWh between 4–8 PM." "Buy up to 5 kWh if price drops below 10¢/kWh." Rules evaluated every 15 minutes alongside meter readings. Automation creates offers/requests on user's behalf. Kill switch to disable all automation instantly. |

### Phase 9 Architecture Addition

> **PURPOSE:** Show that P2P is built as a module within the existing platform (not a separate product). It reuses the same PostgreSQL, FastAPI, and frontend stack — extending the monolith rather than creating a microservice.

```
┌──────────────────────────────────────────────────────┐
│  P2P Trading Service (new FastAPI microservice)       │
│  ├── Marketplace API (offers, requests, orders)       │
│  ├── Matching Engine (runs every 15 min via Celery)   │
│  ├── Settlement Engine (reconciles meter + trades)    │
│  ├── Pricing Engine (dynamic price suggestions)       │
│  └── Wallet Service (ledger, balances, transfers)     │
└─────────────────┬────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────┐
│  PostgreSQL — P2P Schema                              │
│  ├── prosumer_profiles                                │
│  ├── energy_wallets + wallet_ledger                   │
│  ├── energy_offers + energy_requests                  │
│  ├── p2p_orders + p2p_settlements                     │
│  ├── meter_readings_p2p  [hypertable]                 │
│  ├── trading_rules                                    │
│  └── energy_communities + community_members           │
└──────────────────────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────┐
│  External Integrations                                │
│  ├── Stripe Connect (seller payouts, buyer charges)   │
│  ├── Smart Meter APIs (Enphase, SolarEdge, Tesla)     │
│  ├── Weather API (solar production forecast)          │
│  └── Geocoding API (proximity matching)               │
└──────────────────────────────────────────────────────┘
```

### Phase 9 Graduation Gate

> **PURPOSE:** End-to-end proof that the marketplace works — from prosumer onboarding through offer creation, matching, settlement, wallet update, and tax reporting. Every step must work, not just individual components.

- [ ] Prosumer onboarded with smart meter linked and producing real production data
- [ ] Seller creates offer → buyer matches → settlement completes within 30 minutes of meter reading
- [ ] Wallet balances update correctly after settlement (double-entry verified)
- [ ] Partial fill works: 1 offer matched by 3 buyers, all settled correctly
- [ ] Automated trading rule creates offer and matches without manual intervention
- [ ] Platform fee calculated and deducted correctly on every settlement
- [ ] Compliance: tax summary generates for seller with > $600 annual earnings
- [ ] At least 2 prosumers trading in a test energy community

---

## 16. Data Model

> **PURPOSE:** Single source of truth for every database table in the platform — past, present, and planned. Developers check this section to understand what data exists, what's coming, and which phase introduces each table. Prevents duplicate tables and naming conflicts.

### 16.1 Current Schema (Phase 0)

> **PURPOSE:** The existing tables that all code today depends on. Changing these requires Alembic migrations and backward compatibility consideration.

```
buildings          (id, name, address, type, timezone)
zones              (id, building_id, name, floor)
users              (id, building_id, name, email, role, password_hash)
sensor_readings    (time, sensor_id, building_id, zone_id, sensor_type, value)    [hypertable]
hvac_status        (time, device_id, building_id, zone_id, device_type, status, setpoint)  [hypertable]
energy_meter       (time, meter_id, building_id, kwh, voltage, current)           [hypertable]
forecasts          (id, zone_id, forecast_type, predicted_value, forecast_time, created_at)
recommendations    (id, zone_id, recommendation_type, value, status, created_at, applied_at)
```

### 16.2 Tables Added Per Phase

> **PURPOSE:** Forward-looking data model. When starting a new phase, check here for the exact tables to create. This prevents ad-hoc table design during implementation and ensures consistency across phases.

**Phase 1:**
- `created_at`, `updated_at` columns on buildings, zones, users

**Phase 2:**
- `alert_rules` (id, building_id, zone_id, sensor_type, condition, threshold, severity, enabled)
- `alerts` (id, rule_id, triggered_at, value, acknowledged_at, acknowledged_by)
- `notifications` (id, user_id, alert_id, channel, sent_at, read_at)
- Continuous aggregates: `sensor_readings_hourly`, `sensor_readings_daily`

**Phase 3:**
- `weather_data` (time, building_id, temperature, humidity, solar_radiation, source) [hypertable]
- `model_artifacts` (id, building_id, model_type, version, metrics, artifact_path, trained_at)
- `savings_records` (id, recommendation_id, predicted_kwh, actual_kwh, measured_at)

**Phase 4:**
- `tariffs` (id, building_id, tariff_type, schedule_json, effective_from, version)
- `energy_costs` (id, building_id, zone_id, period_start, period_end, kwh, cost_cents, tariff_id)
- `utility_bills` (id, building_id, period_start, period_end, total_cents, line_items_json)
- `billing_discrepancies` (id, bill_id, our_calc_cents, utility_cents, delta_cents, status)
- `energy_budgets` (id, building_id, year, annual_budget_cents, created_by)

**Phase 5:**
- `organizations` (id, name, slug, plan, timezone, country_code)
- `api_keys` (id, org_id, key_hash, scopes, expires_at, last_used_at)
- `org_id` FK added to buildings, users

**Phase 6:**
- `occupancy_events` (time, zone_id, occupancy_count, source) [hypertable]
- `comfort_scores` (time, zone_id, score, temperature_score, humidity_score, co2_score) [hypertable]
- `pms_mappings` (id, building_id, pms_room_id, zone_id, pms_type)

**Phase 7:**
- `devices` (id, building_id, zone_id, device_type, protocol, external_id, manufacturer, model, config_encrypted, is_active)
- `device_capabilities` (device_id, capability, parameters_json)
- `webhook_endpoints` (id, org_id, url, events, secret_hash, enabled)
- `webhook_deliveries` (id, endpoint_id, event_type, payload, status, attempts, last_attempt_at)

**Phase 9:**
- `prosumer_profiles` (id, user_id, address, lat, lng, solar_capacity_kw, battery_capacity_kwh, inverter_type, meter_id, meter_provider, grid_agreement_accepted_at, status)
- `energy_wallets` (id, user_id, energy_credits_wh, cash_balance_cents, currency, created_at, updated_at)
- `wallet_ledger` (id, wallet_id, entry_type, amount_cents, energy_wh, counterparty_wallet_id, order_id, description, created_at) — append-only double-entry
- `meter_readings_p2p` (time, meter_id, user_id, production_wh, consumption_wh, net_export_wh, source) [hypertable, 15-min intervals]
- `energy_offers` (id, seller_id, quantity_wh, price_cents_per_kwh, available_from, available_until, min_purchase_wh, remaining_wh, auto_renew, status, created_at)
- `energy_requests` (id, buyer_id, quantity_wh, max_price_cents_per_kwh, preferred_from, preferred_until, remaining_wh, status, created_at)
- `p2p_orders` (id, offer_id, request_id, seller_id, buyer_id, matched_wh, price_cents_per_kwh, status, matched_at, settled_at)
- `p2p_settlements` (id, order_id, interval_start, interval_end, contracted_wh, actual_delivered_wh, settlement_cents, platform_fee_cents, seller_credit_cents, buyer_debit_cents, shortfall_flag, created_at)
- `trading_rules` (id, user_id, rule_type, conditions_json, action_json, enabled, last_triggered_at, created_at)
- `energy_communities` (id, name, description, location_lat, location_lng, radius_km, fee_discount_pct, created_by, created_at)
- `community_members` (community_id, user_id, role, joined_at)
- `p2p_tax_summaries` (id, user_id, tax_year, total_earnings_cents, total_kwh_sold, report_generated_at)

---

## 17. API Specifications

> **PURPOSE:** Define every API endpoint — existing and planned — in one place. Frontend developers, integration partners, and QA teams reference this section. It serves as the contract between backend and all consumers.

### 17.1 Conventions

> **PURPOSE:** Establish non-negotiable API design rules that every endpoint must follow. Consistency reduces cognitive load for API consumers and prevents each developer from inventing their own patterns.

- Base URL: `/api/v1/`
- Authentication: Bearer JWT or X-API-Key header
- Timestamps: ISO 8601 UTC
- Monetary values: Integer cents (BIGINT)
- Pagination: cursor-based (`after=` param), default limit=50, max=500
- Error format: `{"error": "message", "code": "ERROR_CODE", "request_id": "uuid"}`
- Rate limiting: 100 req/min per user/key, 429 with Retry-After

### 17.2 Existing Endpoints (Phase 0)

> **PURPOSE:** Inventory of what's already built and working. These endpoints are stable — breaking changes require versioning (v2).

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | JWT token exchange |
| GET/POST/PATCH | `/users` | User management (admin only) |
| GET/POST/PATCH/DELETE | `/buildings` | Building CRUD |
| GET/POST | `/zones` | Zone CRUD |
| POST | `/sensors/readings` | Bulk sensor ingestion |
| GET | `/sensors/readings` | Query sensor data |
| POST/GET | `/hvac/status` | HVAC status ingestion/query |
| POST/GET | `/energy-meters/readings` | Energy meter ingestion/query |
| POST/GET | `/forecasts` | AI forecast management |
| POST/GET/PATCH | `/recommendations` | Recommendation lifecycle |
| GET | `/buildings/{id}/energy-summary` | Hourly energy aggregation |
| GET | `/buildings/{id}/carbon-emissions` | CO2 estimation |
| GET | `/anomalies` | Anomaly detection |
| GET | `/health` | Health check |

### 17.3 Endpoints Added Per Phase

> **PURPOSE:** Roadmap of API surface growth. When planning a phase, this shows exactly which endpoints to implement. Frontend developers can start designing UI against these contracts before backend implementation is complete.

**Phase 1:** Pagination params on all GET-list endpoints.

**Phase 2:**
- `GET /sensors/latest?building_id=` — Latest reading per sensor (from Redis)
- `WS /ws/telemetry/{building_id}` — Real-time sensor stream
- `GET/POST/PATCH/DELETE /alert-rules` — Alert rule CRUD
- `GET/PATCH /alerts` — List and acknowledge alerts
- `GET /sensors/health?building_id=` — Sensor health status

**Phase 3:**
- `POST /forecasts/generate?building_id=` — Trigger forecast generation
- `GET /buildings/{id}/savings` — Savings tracker summary
- `POST /ml/train?building_id=&model_type=` — Trigger model training

**Phase 4:**
- `GET/POST/PATCH /tariffs` — Tariff configuration
- `GET /buildings/{id}/cost-summary` — Cost analytics
- `POST /buildings/{id}/utility-bills` — Upload utility bill CSV
- `GET /buildings/{id}/billing-discrepancies` — List discrepancies
- `GET /buildings/{id}/reports/monthly?month=` — Monthly PDF report
- `GET/POST /buildings/{id}/budget` — Budget management

**Phase 5:**
- `GET/POST/PATCH /organizations` — Organization management
- `GET/POST/DELETE /api-keys` — API key management
- `POST /onboarding/start` — Begin onboarding wizard

**Phase 6:**
- `POST /occupancy/events` — Ingest occupancy data
- `GET /zones/{id}/comfort-score` — Current comfort score
- `GET /buildings/{id}/room-energy` — Per-room energy profiles
- `POST /pms/webhook` — PMS event receiver

**Phase 7:**
- `GET/POST/PATCH/DELETE /devices` — Device registry CRUD
- `POST /ingest` — Protocol-agnostic telemetry ingestion
- `GET/POST/DELETE /webhooks` — Webhook endpoint management
- `GET /webhooks/{id}/deliveries` — Webhook delivery log

**Phase 9:**
- `POST /p2p/prosumers` — Register as prosumer (onboarding)
- `GET /p2p/prosumers/me` — Get own prosumer profile + meter status
- `GET/POST /p2p/wallet` — Get wallet balance / deposit funds
- `POST /p2p/wallet/withdraw` — Withdraw cash to bank (via Stripe)
- `GET /p2p/wallet/ledger` — Transaction history (paginated)
- `GET/POST /p2p/offers` — Browse marketplace offers / create sell offer
- `DELETE /p2p/offers/{id}` — Cancel an offer
- `GET/POST /p2p/requests` — Browse buy requests / create buy request
- `DELETE /p2p/requests/{id}` — Cancel a request
- `GET /p2p/orders` — List my orders (as seller or buyer)
- `GET /p2p/orders/{id}` — Order detail with settlement history
- `GET /p2p/settlements?order_id=` — Settlement records for an order
- `GET/POST/PATCH/DELETE /p2p/trading-rules` — Automated trading rule CRUD
- `POST /p2p/trading-rules/{id}/test` — Dry-run a rule against current market
- `GET /p2p/market/price` — Current suggested buy/sell prices
- `GET /p2p/market/stats` — Market stats (volume, avg price, active offers)
- `GET/POST /p2p/communities` — List / create energy community
- `POST /p2p/communities/{id}/join` — Join a community
- `GET /p2p/communities/{id}/dashboard` — Community trading dashboard
- `GET /p2p/analytics/seller` — Seller analytics (revenue, kWh sold, projections)
- `GET /p2p/analytics/buyer` — Buyer analytics (savings, kWh bought, carbon offset)
- `GET /p2p/tax-summary?year=` — Annual tax summary for reporting

---

## 18. Non-Functional Requirements

> **PURPOSE:** Define the quality attributes that aren't features but determine whether the product is usable, reliable, and secure. A fast, correct feature that crashes under load is worthless. This section sets the performance, reliability, and security bars that every phase must meet.

### 18.1 Performance

> **PURPOSE:** Concrete latency and throughput targets. When a developer asks "is 500ms acceptable for this query?", they check this table. Each cell is a testable SLA.

| Operation | Phase 0 | Phase 2 Target | Phase 8 Target | Phase 9 Target |
|-----------|---------|---------------|---------------|---------------|
| Sensor ingestion (REST) | ~200 rows/sec | 1,000 rows/sec | 10,000 rows/sec | 10,000 rows/sec |
| GET /sensors/latest (Redis) | N/A | < 10ms p95 | < 5ms p95 | < 5ms p95 |
| GET /sensors/readings (24h, 1 device) | < 1s | < 500ms | < 200ms | < 200ms |
| Dashboard page load (FCP) | ~3s | < 2s | < 1.5s | < 1.5s |
| Alert evaluation cycle | N/A | < 90 seconds | < 30 seconds | < 30 seconds |
| Forecast generation (1 building) | N/A | < 5 minutes | < 1 minute | < 1 minute |
| P2P order matching cycle | N/A | N/A | N/A | < 60 seconds (every 15 min) |
| P2P settlement (per interval) | N/A | N/A | N/A | < 5 minutes for 1,000 active trades |
| Marketplace offer listing | N/A | N/A | N/A | < 200ms (geo-filtered, paginated) |
| Wallet balance query | N/A | N/A | N/A | < 50ms (cached) |

### 18.2 Reliability

> **PURPOSE:** Define uptime expectations per phase. Early phases tolerate more downtime; later phases require near-continuous availability. Each tier also specifies the monitoring tooling needed to actually enforce the target.

| Phase | Availability Target | Monitoring |
|-------|-------------------|-----------|
| 0–1 | Dev only | Docker health checks |
| 2–3 | 99% (7.3h/month downtime) | UptimeRobot + Grafana |
| 4–5 | 99.5% (3.6h/month downtime) | Prometheus + PagerDuty |
| 6–8 | 99.9% (43 min/month downtime) | Full observability stack |

### 18.3 Security

> **PURPOSE:** Enumerate every security control and when it's introduced. Security is not a phase — it's a layer that tightens at each stage. This checklist prevents "we'll add security later" thinking.

- All data in transit: TLS 1.2+ (enforced from Phase 1)
- Passwords: bcrypt with 12 rounds (done)
- JWT: 1-hour TTL, HS256 (Phase 0–4), RS256 via Auth0 (Phase 5+)
- Database: Not exposed to public internet (Phase 2+)
- Secrets: Environment variables (Phase 0–4), AWS Parameter Store (Phase 5+)
- Sensitive config: AES-256 encrypted JSONB (Phase 7 device credentials)
- Audit log: Append-only billing events (Phase 4), full audit trail (Phase 8)

---

## 19. Technology Stack

> **PURPOSE:** Canonical list of every technology used across all phases. When a developer asks "what do we use for caching?" or "which ML framework?", they check here. Prevents tool sprawl and ensures consistent choices. Each column shows what's added at each phase — nothing is replaced, only extended.

| Layer | Phase 0 (Current) | Phase 2+ Addition | Phase 5+ Addition | Phase 9 Addition |
|-------|-------------------|-------------------|-------------------|-------------------|
| **Backend** | Python 3.12, FastAPI | APScheduler, Celery | Auth0 SDK | Matching engine (Celery beat), Settlement worker |
| **Database** | PostgreSQL 16 + TimescaleDB | Continuous aggregates | Row-Level Security | P2P schema, double-entry ledger, PostGIS (proximity) |
| **Cache** | — | Redis 7 | Redis Cluster | Order book cache, price cache |
| **Frontend** | React, Vite, Tailwind, Recharts | WebSocket (native) | Auth0 React SDK | Marketplace UI, wallet UI, map view (Leaflet/Mapbox) |
| **ML** | — | scikit-learn, Prophet | MLflow | Price prediction, supply/demand forecasting |
| **PDF** | — | — (Phase 4: WeasyPrint) | — | Tax summary PDF (1099) |
| **Payments** | — | — | — | Stripe Connect (payouts, charges, escrow) |
| **Geospatial** | — | — | — | PostGIS extension, geocoding API |
| **MQTT** | — | — | EMQX Community | Home energy gateway telemetry |
| **BMS** | — | — | BAC0 (BACnet), pymodbus | — |
| **CI/CD** | GitHub Actions | + Docker Compose test | + Helm, ArgoCD | + P2P integration tests |
| **Monitoring** | — | UptimeRobot, Grafana | Prometheus, Loki, Tempo | Settlement audit dashboards |
| **Auth** | Custom JWT | Custom JWT | Auth0 | Auth0 + KYC verification for traders |
| **Deployment** | Docker Compose | Docker Compose | Kubernetes (EKS) | Kubernetes (EKS) |

---

## 20. Risks & Mitigations

> **PURPOSE:** Honest assessment of what could go wrong and how the team plans to handle it. Every risk has a probability, impact, and a concrete mitigation — not "we'll figure it out." Investors, stakeholders, and the engineering team should review this to avoid surprises. If a risk materializes, the mitigation plan is already documented.

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| **ML model accuracy insufficient** | Medium | High | Phase 3 starts with rule-based optimizer as fallback. ML enhances, doesn't replace. Always show confidence intervals. |
| **BMS integration complexity** | High | Medium | Phase 7 starts with BACnet/IP (most common). Modbus as second. Defer proprietary protocols. Maintain tested-compatible equipment list. |
| **PMS vendor cooperation** | Medium | Medium | Phase 6 uses webhook receiver (PMS pushes to us). Fallback: manual occupancy schedule upload. |
| **Scope creep from pilot customers** | High | Medium | Each phase has fixed scope. New requests go to future phase backlog. Weekly stakeholder sync. |
| **Single-tenant to multi-tenant migration** | Medium | High | Phase 5 uses Alembic migration to add org_id. RLS added incrementally. Feature-flagged rollout. |
| **TimescaleDB performance at scale** | Low | High | Continuous aggregates handle read scaling. Write scaling: vertical first (10K writes/sec), distributed TimescaleDB at 50K+. |
| **Test suite not catching DB-specific bugs** | Medium | Medium | Phase 1 switches to testcontainers (real PostgreSQL). Eliminates SQLite/Postgres behavior differences. |
| **Frontend complexity growth** | Medium | Low | Component library established in Phase 0. Storybook added in Phase 2. Design system documented. |
| **P2P regulatory uncertainty** | High | High | Energy trading regulations vary wildly by jurisdiction (US state-by-state, EU member states). Phase 9 compliance layer is configuration-driven, not hardcoded. Start in deregulated markets (Texas ERCOT, UK, Germany, Australia). Legal review before each market launch. |
| **P2P settlement accuracy** | Medium | High | Settlement depends on accurate smart meter data. Meters may report late or have gaps. Mitigation: 24-hour settlement finalization window. Provisional settlements updated when late meter data arrives. Idempotent settlement engine. |
| **Stripe/payment compliance** | Medium | Medium | P2P energy payments may trigger money transmitter regulations in some jurisdictions. Use Stripe Connect's platform model (Stripe is the regulated entity). Consult fintech counsel before launch. |
| **Smart meter data access** | High | Medium | Not all utilities or meter manufacturers provide real-time API access. Fallback: manual CSV upload of meter data, or optical reader attachments. Prioritize Enphase + SolarEdge (80%+ of US residential solar market). |
| **P2P liquidity (chicken-and-egg)** | High | Medium | Marketplace needs both sellers and buyers. Launch strategy: start with tight geographic communities (HOAs, apartment complexes, co-ops). Offer introductory zero-fee period. Seed marketplace with "virtual" utility offers at grid rate as a floor. |

---

*This document is the single source of truth for the Commercial Energy OS product. All phases build incrementally on the existing codebase. No rewrites — only extensions.*

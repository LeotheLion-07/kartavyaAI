# Kartavya AI
> **"Pass on what matters, with proof."**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016%20App%20Router-black.svg)](https://nextjs.org)
[![PostgreSQL + pgvector](https://img.shields.io/badge/Database-PostgreSQL%2016%20%2B%20pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![BFT Consensus Grounded](https://img.shields.io/badge/Verification-BFT%20Consensus%20%283%2F3%29-10B981.svg)](#)

---

## 1. Overview

**Kartavya AI** is an enterprise-grade, evidence-linked, permission-aware knowledge handover platform that prevents mission-critical project knowledge from being lost when engineers, tech leads, or key contributors depart or change roles.

Instead of scattered Slack threads, unmerged PR branches, lost RFC documents, or outdated meeting notes, Kartavya AI:
1. **Aggregates and Ingests** code repositories, PR diffs, Markdown RFCs, PDFs, CSV task boards, and communication threads.
2. **Reconstructs Project State** across 10 structured dimensions (Decisions & Rationale, Ownership, Task Status, Blockers, Dependencies, Risks, Open Inquiries, Next Actions, Deadlines, Unfinished Work).
3. **Verifies Every Fact**: Every assertion is strictly anchored to immutable Git commits, AST diffs, and verbatim source quotes with exact line spans.
4. **Enforces Data Loss Prevention (DLP)**: Server-level access control filters restricted credentials (e.g., Stripe keys, HSM tokens) and hides unauthorized items with `"1 related item hidden. Request access."`
5. **Detects & Resolves Conflicts**: Flags contradictions (e.g. PR assignee vs. Slack announcement) and directs them to human review.
6. **Produces Authoritative Transfer Packages**: Synthesizes a 13-section transition report with a 30-day onboarding plan and enables the successor to cryptographically sign receipt.

---

## 2. Technology Stack

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Recharts.
- **Backend**: Python FastAPI, Pydantic v2 validation, SQLAlchemy, Uvicorn.
- **Data & Vector Layer**: PostgreSQL 16 + pgvector (with fallback local SQLite database for zero-friction local execution).
- **Security & DLP**: JWT tokens, bcrypt password hashing, regular expression credential scrubbers, RBAC permissions.
- **Orchestration**: Redis 7.2, Docker Compose.

---

## 3. Sample Accounts (1-Click Role Switcher Available in UI)

The application provides instant 1-click role simulation directly from the top navigation bar avatar dropdown:

| User | Role | Title | Email | Default Password |
|---|---|---|---|---|
| **Alex Morgan** | Manager / Approver | Engineering Manager | `alex.morgan@company.internal` | `password123` |
| **Sarah Lin** | Departing Staff | Staff Lead L6 | `sarah.lin@company.internal` | `password123` |
| **Marcus Vance** | Incoming Successor | Senior L5 Successor | `marcus.vance@company.internal` | `password123` |
| **Sarah Admin** | System Admin | SecOps / Administrator | `admin@kartavya.ai` | `password123` |

---

## 4. Key Functional Modules

### 1. Role Handover View (`/role-handover`)
- Executive Transfer Order transferring system ownership from Sarah Lin to Marcus Vance.
- **Critical Architecture & Systems You Own**: Payment Settlement Worker (FastAPI/RQ Celery) with P99 metrics, active blocker alerts, and immediate 1st actions (`worker.py: line 84`).
- **30-Day Onboarding Plan**: Interactive week-by-week checklist (Phase 1: Ramp-up, Phase 2: First Deployment, Phase 3: Full Ownership).
- **Grounded Handover Q&A**: Zero-hallucination query assistant with prompt suggestions and verbatim citations.
- **Key Team Contacts**: Escalation grid with domain leads.
- **Acknowledge & Sign Receipt**: Successor signs receipt cryptographically.

### 2. Decisions Ledger & Evidence Inspector (`/timeline`)
- Filter pills: All Decisions, Verified, Conflicting, Inferred.
- Chronological cards with tags (`#GH-PR-1892`, `#RFC-044-DB`), AST diff badges, and human confirmation buttons for inferred decisions.
- **Evidence Inspector**: Side drawer rendering verbatim source quotes, merged PR diff syntax view, cryptographic SHA-256 root, and version history.

### 3. Sources & Ingestion (`/sources`)
- Ethical On-Demand Ingestion connectors: GitHub, Slack, Notion Wiki, Jira.
- **Proactive Knowledge Risk (Bus Factor Alerts)**: Bus Factor 1.0 (Critical 98% risk on Payment Webhook Engine), Bus Factor 1.5, Bus Factor 4+.
- **Knowledge Distribution Matrix**: Visual density bars across core modules.
- **File Upload & GitHub Sync**: Real file parsing (PDF, Markdown, TXT, CSV, JSON) and automatic knowledge extraction.

### 4. Evidence Board & Manager Gate (`/evidence`)
- Handover case state: `CASE-2024-884A`.
- **Unresolved Ambiguity (Conflict #882)**: Side-by-side discrepancy between Codebase PR #1420 and Slack sync notes with 1-click `[Accept Resolution]`.
- **Synthesized Handover Document**: Live draft with DLP token masks (`--force-token=[REDACTED_VAULT_KEY]`).
- **Manager Gate Checklist**: Citations validated, zero ungrounded text, DLP mask applied, conflict resolution check, and cutover authorization button.

### 5. Grounded AI Chat Assistant (`/chat`)
- Strictly grounded in approved, permitted sources.
- Displays verifiable citations with claim codes, source names, and exact quotes.
- If asked an ungrounded or fictitious question (e.g. cafeteria brownie recipe), it responds: *"No evidence found in the approved project sources."* Never hallucinates.

### 6. Targeted Knowledge Gaps (`/gaps`)
- Direct inquiries for departing staff (e.g., *"Why was the authentication module not completed?"*).
- Answering workflow recording respondent, timestamp, and distinguishing clarifications from source code.

### 7. Security Audit Ledger (`/audit`)
- Immutable log tracking logins, file uploads, claim modifications, approvals, conflict resolutions, access requests, and cutover signatures.

### 8. Full 13-Section PDF Export
- Generates clean, high-fidelity printable handover document covering all 13 sections with cryptographic transition package signature.

---

## 4. Mandatory Hackathon Implementations (Strict Scope Lock)

KartavyaAI provides production-grade implementations of the three core hackathon commitments:

### Commitment 1: Automated Conflict Detection Engine
- **Cross-Source Inconsistency Detection**: Automatically scans and compares structured claims extracted from uploaded documents, specs, architecture RFCs, GitHub activity, and task records.
- **5 Mandatory Conflict Categories**:
  - **Task Ownership**: Detects multiple contradictory assignees or leads for the same module/service.
  - **Project Decisions**: Identifies contradictory architectural decisions (e.g., PostgreSQL vs MongoDB).
  - **Task Completion Status**: Flags status disagreements (e.g., "completed" vs "in progress" or "blocked").
  - **Deadlines**: Catches due date discrepancies across schedules and roadmaps.
  - **Dependencies**: Flags conflicting prerequisites and service requirements.
- **Deterministic & Category-Aware**: Normalizes entity names and claim values; flags contradictions without silently overwriting or picking the newest claim.
- **Dual-Panel Resolution Workflow**: `/evidence` provides side-by-side evidence inspection (Source A vs Source B, verbatim quotes, timestamps, extracted values) and enables authorized managers to **Accept Supported Resolution**, **Reject Proposed Resolution**, or **Mark Unresolved** with human audit logging.

### Commitment 2: Permission-Aware Retrieval and Redaction System
- **Server-Side Pre-Retrieval Enforcement**: In Grounded Chat and API queries, unpermitted chunks and claims are strictly excluded *before* vector ranking or LLM synthesis occurs, preventing unauthorized content from leaking into prompt context.
- **Multi-Tier Classification**: Supports `Public`, `Team`, `Management Only`, and `Restricted Vault` classifications across sources, chunks, claims, and conflicts.
- **Real-Time DLP Token Scrubbing**: Scrubbers mask high-entropy secrets (private keys, database URLs, JWTs, HSM tokens, and `SECRET_MARKER_*` identifiers) across all user-facing endpoints.
- **RBAC & Project Membership Guardrails**: Enforces project-level isolation; restricts approval of access requests and handover packages to Managers/Admins, and limits handover receipt signing exclusively to the assigned Successor.
- **Comprehensive Audit Trail**: All authentication, access grants, denials, and redactions are permanently logged with ISO 8601 timestamps and user identity.

### Commitment 3: Evidence-Grounded Conversational Assistant & Knowledge Gaps Engine
- **Zero-Hallucination Retrieval**: Powered by hybrid TF-IDF vector space cosine similarity and exact keyword matching over permitted project claims.
- **Exact "No evidence found" Fallback**: When queries lack supporting evidence in permitted sources or probe for restricted content, the assistant strictly returns `"No evidence found"`.
- **Contradiction-Aware Assistant**: When querying an entity with conflicting evidence, the assistant surfaces the contradiction, citing both sources side-by-side without arbitrarily choosing one.
- **Automated 10-Dimension Gap Detection**: Scans project assets across 10 dimensions (Decisions, Ownership, Unfinished Tasks, Deadlines, Dependencies, Blockers, Operational Risks, Incomplete Work, Infrastructure Credentials, Escalation Contacts) and synthesizes targeted questions for departing staff.
- **Clarification Provenance**: When departing staff answer questions via `/gaps`, answers are anchored as verified claims with `verification_method="Human Clarification"`, preserving author identity and timestamp.

---

## 5. Local Setup & Quick Start

### Option A: Run Directly with Python & Node.js

#### 1. Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```
*Backend runs on `http://localhost:8000` (auto-syncs schema & seeds database on first boot).*

#### 2. Frontend:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`.*

---

### Option B: Run with Docker Compose
```bash
docker compose up --build
```
This spins up:
- PostgreSQL 16 with pgvector on port 5432
- Redis on port 6379
- FastAPI backend on port 8000
- Next.js frontend on port 3000

### Option C: Deploy both services on Vercel

Import the repository as **one Vercel project** and leave its **Root Directory** set to the repository root (`.`). Do not set it to `frontend/` or `backend/`: the root [`vercel.json`](./vercel.json) defines both services and routes `/api/*` to FastAPI.

The frontend uses the same-origin `/api/v1` path, so no `NEXT_PUBLIC_API_URL` or manually configured `BACKEND_URL` is needed. Vercel injects the backend binding automatically. Set a unique `SECRET_KEY` in Vercel project environment variables before deploying. For data that must survive function restarts, also configure `DATABASE_URL` to a persistent PostgreSQL database; the default Vercel SQLite file is temporary.

---

## 6. Running Automated Tests

Run the complete test suite verifying all 3 mandatory commitments, security rules, and end-to-end integration journeys:
```bash
cd backend
python -m pytest -v
```

### Test Suite Breakdown:
1. `tests/test_api.py` (7 tests): Core endpoints, authentication, project membership, and successor receipt signing.
2. `tests/test_conflicts.py` (3 tests): 5-category conflict detection, deduplication on repeated ingestion, and resolution lifecycle.
3. `tests/test_permissions.py` (5 tests): Unauthenticated blocks, non-member project isolation, unauthorized approval gates, successor-only receipt, and **Mandatory Negative Security Test** with secret markers.
4. `tests/test_chat_and_gaps.py` (5 tests): Citations & verbatim quotes, exact "No evidence found" zero-hallucination constraint, contradiction alerts, automated gap generation across 10 dimensions, and human clarification provenance.
5. `tests/test_e2e_journey.py` (1 test, 21 steps): Complete end-to-end hackathon journey executing all 21 verification steps continuously.

**Result**: 21 passed in ~6.5s (100% test pass rate).
Frontend production build: `npm run build` succeeds with zero TypeScript or lint errors.

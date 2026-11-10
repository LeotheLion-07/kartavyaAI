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

## 5. Local Setup & Quick Start

### Option A: Run Directly with Python & Node.js

#### 1. Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```
*Backend runs on `http://localhost:8000` (auto-seeds database on first boot).*

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

---

## 6. Running Automated Tests

Run the test suite to verify all endpoints, RBAC permissions, DLP redactions, and zero-hallucination grounded chat constraints:
```bash
cd backend
python -m pytest
```
All 7 unit and integration test suites pass with 100% success.

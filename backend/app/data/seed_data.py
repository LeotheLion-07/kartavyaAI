from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.models import (
    User, Project, ProjectMember, Source, SourceChunk, Claim, ClaimVersion,
    Decision, Task, Conflict, KnowledgeGapQuestion, AccessRequest,
    HandoverCase, HandoverReport, HandoverAcknowledgement, AuditLog, Notification
)
from app.core.security import get_password_hash

def seed_database(db: Session):
    # Check if database is already seeded
    if db.query(User).count() > 0:
        return

    print("Seeding database with enterprise demo records...")

    # 1. Create Users
    default_pw = get_password_hash("password123")
    
    alex = User(
        email="alex.morgan@company.internal",
        hashed_password=default_pw,
        full_name="Alex Morgan",
        role="Manager",
        title="Engineering Manager",
        department="Core Platform & Payments",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    sarah = User(
        email="sarah.lin@company.internal",
        hashed_password=default_pw,
        full_name="Sarah Lin",
        role="Departing",
        title="Staff Lead (Departing Lead L6)",
        department="Core Platform & Payments",
        avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    marcus = User(
        email="marcus.vance@company.internal",
        hashed_password=default_pw,
        full_name="Marcus Vance",
        role="Incoming",
        title="Senior L5 Successor (Incoming Lead)",
        department="Core Platform & Payments",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    admin = User(
        email="admin@kartavya.ai",
        hashed_password=default_pw,
        full_name="Sarah Admin",
        role="Admin",
        title="System Administrator / SecOps",
        department="Information Security",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    david = User(
        email="david.k@company.internal",
        hashed_password=default_pw,
        full_name="David K.",
        role="Manager",
        title="Backend Peer (Webhook Engine & RQ)",
        department="Core Platform",
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    elena = User(
        email="elena.r@company.internal",
        hashed_password=default_pw,
        full_name="Elena Rostova",
        role="Manager",
        title="Infra Lead (Terraform, EKS & IAM Security)",
        department="Cloud Infrastructure",
        avatar_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    
    db.add_all([alex, sarah, marcus, admin, david, elena])
    db.commit()

    # 2. Projects
    p1 = Project(
        name="Core Platform & Payment Gateway Transition",
        slug="core-platform-payments",
        description="High-throughput payment settlement engine (4,500 req/s), pgvector HNSW ledger, and webhook distribution services.",
        status="Active Cutover",
        bus_factor_score=1.0,
        owner_id=sarah.id
    )
    p2 = Project(
        name="AI-Powered Campus Management System",
        slug="campus-management-system",
        description="Comprehensive university portal handling student biometric authentication, cafeteria point-of-sale ledgers, course registration RAG.",
        status="Handover Review",
        bus_factor_score=1.2,
        owner_id=sarah.id
    )
    db.add_all([p1, p2])
    db.commit()

    # Add Project Members
    db.add_all([
        ProjectMember(project_id=p1.id, user_id=sarah.id, role_in_project="Departing Lead"),
        ProjectMember(project_id=p1.id, user_id=marcus.id, role_in_project="Incoming Successor"),
        ProjectMember(project_id=p1.id, user_id=alex.id, role_in_project="Engineering Manager"),
        ProjectMember(project_id=p1.id, user_id=david.id, role_in_project="Backend Peer"),
        ProjectMember(project_id=p1.id, user_id=elena.id, role_in_project="Infra Lead"),
        ProjectMember(project_id=p2.id, user_id=sarah.id, role_in_project="Departing Lead"),
        ProjectMember(project_id=p2.id, user_id=marcus.id, role_in_project="Incoming Successor"),
    ])
    db.commit()

    # 3. Handover Cases
    case1 = HandoverCase(
        case_number="CASE-2024-884A",
        project_id=p1.id,
        title="Core Platform & Payment Gateway Transition",
        departing_user_id=sarah.id,
        successor_user_id=marcus.id,
        approver_user_id=alex.id,
        stage="Stage 4 of 5 · Sign-off & Verification",
        status="Pending Sign-off",
        target_cutover_date=datetime.now(timezone.utc) + timedelta(days=14),
        grounded_pct=94.0,
        consensus_status="BFT Consensus Verified (3/3)"
    )
    case2 = HandoverCase(
        case_number="CASE-2024-501C",
        project_id=p2.id,
        title="AI-Powered Campus Management System Handover",
        departing_user_id=sarah.id,
        successor_user_id=marcus.id,
        approver_user_id=alex.id,
        stage="Stage 3 of 5 · Gap Resolution",
        status="In Review",
        target_cutover_date=datetime.now(timezone.utc) + timedelta(days=21),
        grounded_pct=88.5,
        consensus_status="BFT Consensus Verified (3/3)"
    )
    db.add_all([case1, case2])
    db.commit()

    # 4. Sources
    s1 = Source(
        source_code="#PR-1892",
        project_id=p1.id,
        name="GitHub PR #1892: feat(db): migrate ledger to PostgreSQL + pgvector",
        source_type="GitHub PR",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=sarah.id,
        external_url="https://github.com/org/core-platform/pull/1892",
        raw_content="""@@ -14,6 +14,8 @@ alembic/env.py
- from dynamodb_client import SyncDriver
+ from pgvector.sqlalchemy import Vector
+ class LedgerVectorEmbedding(Base):
We agreed in architecture review that pgvector eliminates dual-database synchronization latency while maintaining transactional guarantees for payments ledger cutover."""
    )
    s2 = Source(
        source_code="#PR-1420",
        project_id=p1.id,
        name="GitHub PR #1420: feat(core): Kafka dual-dispatch partition failover & circuit breaker",
        source_type="GitHub PR",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=sarah.id,
        external_url="https://github.com/org/core-platform/pull/1420",
        raw_content="""// circuit_breaker.go: line 104
// Delegated to Core Infra SRE
circuit.Notify("pagerduty:core-sre");
The primary transaction pipeline relies on asynchronous double-dispatch via Kafka topic payments.events.settlement.v2. Under peak loads exceeding 4,500 TPS, backpressure mitigation shifts buffering to the secondary Redis cluster."""
    )
    s3 = Source(
        source_code="#SLACK-payments",
        project_id=p1.id,
        name="Slack #eng-payments Thread: Webhook Retry & Manual Drain Ownership",
        source_type="Slack Thread",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=alex.id,
        raw_content="""[Oct 11 14:20] David K.: "David K. has taken over the webhook retry mechanism and dead-letter queue config starting this sprint."
[Oct 11 14:24] Sarah Lin: "Sarah agreed Payments Pod owns manual drain triggers until Q1-25. SRE only receives metric pings." """
    )
    s4 = Source(
        source_code="#RFC-044-DB",
        project_id=p1.id,
        name="Notion Wiki: RFC-044 PostgreSQL Connection Pool & HNSW Indexing Specs",
        source_type="Notion Wiki",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=sarah.id,
        raw_content="""Database connection pooling is initialized via SQLAlchemy's async engine in app/core/database.py with pool_size=20, max_overflow=10, and pool_pre_ping=True to protect against vector stream disconnections.
Main transaction storage & RAG index configured with HNSW (m=16, ef_construction=64). Houses all user vectors and contextual decision history. Scaling Imperative: Monitor memory footprint as index crosses 800k vectors. Provisioning upgrade to 32GB RAM recommended before reaching 1,000,000 threshold."""
    )
    s5 = Source(
        source_code="#DOC-991",
        project_id=p1.id,
        name="Runbook: Failover Switch Routine (Adyen -> Stripe Direct)",
        source_type="Document",
        access_classification="Restricted",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=sarah.id,
        raw_content="""If the Adyen primary gateway returns consecutive 504 timeouts for >45 seconds, the system shifts traffic autonomously.
Command: ./bin/payctl circuit reset --gateway=adyen --force-token=[REDACTED_VAULT_KEY]
Marcus Vance has been provisioned Okta group privileges for eng-payments-oncall. Secondary AWS breakglass credentials will deploy automatically upon final manager sign-off."""
    )
    s6 = Source(
        source_code="#SEC-VAULT-01",
        project_id=p1.id,
        name="Confidential: Payment HSM Root Keys and Merchant API Credentials",
        source_type="Document",
        access_classification="Confidential",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=admin.id,
        raw_content="""Root merchant decryption key for Stripe Production: [REDACTED_STRIPE_LIVE_KEY].
Access restricted strictly to Staff Level SecOps and VP Engineering."""
    )
    
    # Campus sources
    s7 = Source(
        source_code="#CAMP-PR-42",
        project_id=p2.id,
        name="GitHub PR #42: feat(campus): Biometric Attendance Ledger Sync",
        source_type="GitHub PR",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=sarah.id,
        raw_content="""Biometric attendance ledger captures student fingerprint hashes and syncs with PostgreSQL.
Decided to store only SHA-256 salted hashes to comply with campus privacy guidelines."""
    )
    s8 = Source(
        source_code="#CAMP-MEET-08",
        project_id=p2.id,
        name="Campus Sync Minutes: Cafeteria POS Integration Assignment",
        source_type="Meeting Notes",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=alex.id,
        raw_content="""Meeting Notes: Task assigned to Rahul for cafeteria POS integration.
GitHub Issue #119 however reflects: Task assigned to Arjun for POS payment settlement."""
    )

    db.add_all([s1, s2, s3, s4, s5, s6, s7, s8])
    db.commit()

    # 5. Claims
    c1 = Claim(
        claim_code="#CLM-1094",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Migrated from DynamoDB to PostgreSQL + pgvector for semantic search & relational ledger",
        description="Core Rationale: Needed strict ACID compliance for the multi-tenant payout ledger and co-located high-dimensional vector embeddings, eliminating dual-write sync failures. Alternatives evaluated & discarded: CockroachDB (High memory footprint in small regional clusters; increased cold-start costs by 34%).",
        category="Decision",
        evidence_status="VERIFIED",
        confidence_score=1.0,
        verification_method="Exact Match",
        source_id=s1.id,
        exact_quote="We agreed in architecture review that pgvector eliminates dual-database synchronization latency while maintaining transactional guarantees for payments ledger cutover.",
        line_span="Span L48-L56",
        primary_code_diff="""@@ -14,6 +14,8 @@ alembic/env.py
- from dynamodb_client import SyncDriver
+ from pgvector.sqlalchemy import Vector
+ class LedgerVectorEmbedding(Base):""",
        cryptographic_root="sha256:4b91f0...de21",
        golden_ref=True,
        related_person="Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=True
    )
    c2 = Claim(
        claim_code="#CLM-1098",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Conflict: Ownership & Rollout of v2 Webhook Ingestion Engine",
        description="Slack #eng-payments notes: 'David K. has taken over the webhook retry mechanism and dead-letter queue config starting this sprint.' GitHub & Jira PAY-412: PR #2041 assignees unassigned; branch feat/webhook-retry still authored by Sarah with merge conflicts.",
        category="Owner",
        evidence_status="CONFLICTING",
        confidence_score=0.92,
        verification_method="NLP Inferred",
        source_id=s3.id,
        secondary_source_id=s2.id,
        exact_quote="David K. has taken over the webhook retry mechanism and dead-letter queue config starting this sprint.",
        line_span="Span L1-L4",
        cryptographic_root="sha256:8a11bc...3391",
        golden_ref=False,
        related_person="David K. / Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=False
    )
    c3 = Claim(
        claim_code="#CLM-1082",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Soft deprecation of Stripe legacy v2 API postponed until Q1 2025",
        description="Derived from PR #1980 discussion ('Let\\'s keep legacy endpoints alive past Black Friday') and weekly sync minutes; no formal Notion RFC published.",
        category="Decision",
        evidence_status="INFERRED",
        confidence_score=0.81,
        verification_method="NLP Inferred",
        source_id=s2.id,
        exact_quote="Let's keep legacy endpoints alive past Black Friday and defer deprecation to Q1 2025.",
        line_span="Span L92-L98",
        cryptographic_root="sha256:3c88bb...7710",
        golden_ref=False,
        related_person="Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=True
    )
    c4 = Claim(
        claim_code="#CLM-1077",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Adopted Pydantic v2 + FastAPI for sub-50ms API throughput and schema validation",
        description="Replaced Marshmallow serialization wrappers. Benchmarks confirmed 4.8x serialization speedup under 1,000 req/sec load tests without modifying external OpenAPI schema.",
        category="Decision",
        evidence_status="VERIFIED",
        confidence_score=0.99,
        verification_method="AST Proved",
        source_id=s1.id,
        exact_quote="Benchmarks confirmed 4.8x serialization speedup under 1,000 req/sec load tests without modifying external OpenAPI schema.",
        line_span="Span L12-L18",
        cryptographic_root="sha256:77ae41...99bc",
        golden_ref=True,
        related_person="Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=True
    )
    c5 = Claim(
        claim_code="#CLM-1052",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Database connection pooling is initialized via SQLAlchemy async engine",
        description="Database connection pooling is initialized via SQLAlchemy's async engine in app/core/database.py with pool_size=20, max_overflow=10, and pool_pre_ping=True to protect against vector stream disconnections.",
        category="Decision",
        evidence_status="VERIFIED",
        confidence_score=0.994,
        verification_method="AST Proved",
        source_id=s4.id,
        exact_quote="Database connection pooling is initialized via SQLAlchemy's async engine in app/core/database.py with pool_size=20, max_overflow=10, and pool_pre_ping=True to protect against vector stream disconnections.",
        line_span="Span L1-L8",
        cryptographic_root="sha256:11bb22...44dd",
        golden_ref=True,
        related_person="Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=True
    )
    c6 = Claim(
        claim_code="#CLM-1065",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Failover Switch Routine & Breakglass Vault Tokens",
        description="If Adyen returns 504 timeouts >45s, shift traffic via payctl circuit reset --gateway=adyen --force-token=[REDACTED_VAULT_KEY].",
        category="Blocker",
        evidence_status="VERIFIED",
        confidence_score=0.95,
        verification_method="Exact Match",
        source_id=s5.id,
        exact_quote="Command: ./bin/payctl circuit reset --gateway=adyen --force-token=[REDACTED_VAULT_KEY]",
        line_span="Span L1-L4",
        cryptographic_root="sha256:99cc11...55ee",
        golden_ref=False,
        related_person="Marcus Vance / Sarah Lin",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Restricted", # RESTRICTED
        is_approved=True
    )
    c7 = Claim(
        claim_code="#CLM-1040",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Confidential Merchant Decryption Vault Keys",
        description="Production HSM merchant decryption keys for direct banking settlement. Token: [REDACTED_STRIPE_LIVE_KEY].",
        category="Risk",
        evidence_status="VERIFIED",
        confidence_score=1.0,
        verification_method="Exact Match",
        source_id=s6.id,
        exact_quote="Root merchant decryption key for Stripe Production: [REDACTED_STRIPE_LIVE_KEY].",
        line_span="Span L1-L3",
        cryptographic_root="sha256:66ff88...11aa",
        golden_ref=False,
        related_person="Sarah Admin",
        author_id=admin.id,
        signoff_reviewer_id=alex.id,
        access_classification="Confidential", # CONFIDENTIAL
        is_approved=True
    )
    
    # Campus Claims
    c8 = Claim(
        claim_code="#CLM-CAMP-01",
        project_id=p2.id,
        handover_case_id=case2.id,
        title="Biometric Attendance Hash Storage Architecture",
        description="Attendance system stores only SHA-256 salted hashes of fingerprint scans directly into PostgreSQL, satisfying student privacy compliance.",
        category="Decision",
        evidence_status="VERIFIED",
        confidence_score=0.98,
        verification_method="Exact Match",
        source_id=s7.id,
        exact_quote="Decided to store only SHA-256 salted hashes to comply with campus privacy guidelines.",
        line_span="Span L3-L5",
        cryptographic_root="sha256:c0ffee...1234",
        golden_ref=True,
        related_person="Rahul Sharma",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=True
    )
    c9 = Claim(
        claim_code="#CLM-CAMP-02",
        project_id=p2.id,
        handover_case_id=case2.id,
        title="Conflict: Cafeteria POS Settlement Lead Assignment",
        description="Meeting notes indicate Rahul is assigned to POS integration, whereas GitHub Issue #119 lists Arjun as sole owner with pending code reviews.",
        category="Owner",
        evidence_status="CONFLICTING",
        confidence_score=0.91,
        verification_method="NLP Inferred",
        source_id=s8.id,
        exact_quote="Task assigned to Rahul for cafeteria POS integration vs Issue #119 Task assigned to Arjun.",
        line_span="Span L1-L4",
        cryptographic_root="sha256:cafe01...8899",
        golden_ref=False,
        related_person="Rahul Sharma / Arjun Verma",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=False
    )
    c10 = Claim(
        claim_code="#CLM-CAMP-03",
        project_id=p2.id,
        handover_case_id=case2.id,
        title="Missing Evidence: Real-time Campus Bus Tracking API Rate Limits",
        description="Bus tracking vendor documentation does not specify whether throttling occurs at 500 or 5,000 requests per minute during student rush hours.",
        category="Risk",
        evidence_status="MISSING EVIDENCE",
        confidence_score=0.25,
        verification_method="NLP Inferred",
        source_id=s8.id,
        exact_quote="Documentation lacks rate limit specification for the live transit GPS webhooks.",
        line_span="Span L6-L8",
        cryptographic_root="sha256:ba5500...4321",
        golden_ref=False,
        related_person="Priya Nair",
        author_id=sarah.id,
        signoff_reviewer_id=alex.id,
        access_classification="Team",
        is_approved=False
    )

    db.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
    db.commit()

    # Claim Versions (Version history for Claim 1 and Claim 2)
    db.add_all([
        ClaimVersion(
            claim_id=c1.id,
            version_num=1,
            previous_value="Evaluating DynamoDB vs PostgreSQL for ledger storage.",
            updated_value=c1.description,
            change_reason="Finalized decision post-RFC review",
            changed_by_user_id=sarah.id
        ),
        ClaimVersion(
            claim_id=c2.id,
            version_num=1,
            previous_value="Webhook engine ownership assigned to David K.",
            updated_value=c2.description,
            change_reason="Flagged contradiction with Jira PAY-412 branch",
            changed_by_user_id=alex.id
        )
    ])
    db.commit()

    # 6. Conflicts
    conf1 = Conflict(
        conflict_code="CONF-882",
        project_id=p1.id,
        handover_case_id=case1.id,
        title="Webhook Failover Circuit Breaker Ownership Discrepancy",
        description="Two canonical systems assign differing primary on-call tiers for the Stripe & Adyen webhook reconciliation pipeline. This creates critical operational ambiguity for the successor during an outage.",
        claim_a_id=c2.id,
        source_a_label="Codebase PR #1420 (Sep 12)",
        source_a_quote='// circuit_breaker.go: line 104\n// Delegated to Core Infra SRE\ncircuit.Notify("pagerduty:core-sre");',
        source_a_claim="Core Infra SRE owns manual overrides",
        source_b_label="Arch Sync Notes (Slack) (Oct 04)",
        source_b_quote='"Sarah agreed Payments Pod owns manual drain triggers until Q1-25. SRE only receives metric pings."',
        source_b_claim="Payments Pod (Marcus) retains override triggers",
        recommended_fix="Assign Payments Pod L2 triage; SRE retains automated restart without raw API tokens.",
        resolution_status="Pending"
    )
    conf2 = Conflict(
        conflict_code="CONF-204",
        project_id=p2.id,
        handover_case_id=case2.id,
        title="Campus POS Gateway Integration Ownership",
        description="Meeting notes from Oct 10 assign the cafeteria payment POS terminal integration to Rahul, while GitHub issue #119 lists Arjun as assignee.",
        claim_a_id=c9.id,
        source_a_label="Campus Sync Minutes #CAMP-MEET-08",
        source_a_quote='"Meeting Notes: Task assigned to Rahul for cafeteria POS integration."',
        source_a_claim="Rahul is primary integrator",
        source_b_label="GitHub Issue #119",
        source_b_quote='"Assignee: Arjun Verma. PR branch created by Arjun."',
        source_b_claim="Arjun is active developer",
        recommended_fix="Confirm Rahul leads architecture review and Arjun executes branch development.",
        resolution_status="Pending"
    )
    db.add_all([conf1, conf2])
    db.commit()

    # 7. Decisions Ledger
    db.add_all([
        Decision(
            decision_code="DEC-1094",
            project_id=p1.id,
            title="Migrated from DynamoDB to PostgreSQL + pgvector for semantic search & relational ledger",
            date=datetime.now(timezone.utc) - timedelta(days=27),
            person_responsible="Sarah Lin",
            rationale="Needed strict ACID compliance for the multi-tenant payout ledger and co-located high-dimensional vector embeddings, eliminating dual-write sync failures.",
            alternatives_evaluated="CockroachDB: High memory footprint in small regional clusters; increased cold-start costs by 34%.",
            supporting_evidence="#GH-PR-1892, #RFC-044-DB",
            evidence_status="VERIFIED",
            tags="database,pgvector,acid"
        ),
        Decision(
            decision_code="DEC-1077",
            project_id=p1.id,
            title="Adopted Pydantic v2 + FastAPI for sub-50ms API throughput and schema validation",
            date=datetime.now(timezone.utc) - timedelta(days=42),
            person_responsible="Sarah Lin",
            rationale="Replaced Marshmallow serialization wrappers. Benchmarks confirmed 4.8x serialization speedup under 1,000 req/sec load tests without modifying external OpenAPI schema.",
            alternatives_evaluated="Marshmallow v3, msgpack-python (rejected due to frontend JSON compliance)",
            supporting_evidence="#GH-PR-1740, #PERF-BENCH-88",
            evidence_status="VERIFIED",
            tags="fastapi,pydantic,performance"
        ),
        Decision(
            decision_code="DEC-1082",
            project_id=p1.id,
            title="Soft deprecation of Stripe legacy v2 API postponed until Q1 2025",
            date=datetime.now(timezone.utc) - timedelta(days=37),
            person_responsible="Sarah Lin",
            rationale="Derived from PR #1980 discussion ('Let's keep legacy endpoints alive past Black Friday') and weekly sync minutes; no formal Notion RFC published.",
            alternatives_evaluated="Immediate hard cutoff on Nov 1",
            supporting_evidence="#GH-COMMIT-8a9f2",
            evidence_status="INFERRED",
            tags="stripe,api,deprecation"
        ),
        Decision(
            decision_code="DEC-CAMP-01",
            project_id=p2.id,
            title="Campus Biometric Attendance salted hashing protocol",
            date=datetime.now(timezone.utc) - timedelta(days=15),
            person_responsible="Rahul Sharma",
            rationale="Store cryptographic salted hashes only to guarantee compliance with student biometric protection standards.",
            alternatives_evaluated="Raw template vector storage on local terminal hardware",
            supporting_evidence="#CAMP-PR-42",
            evidence_status="VERIFIED",
            tags="security,biometrics,campus"
        )
    ])
    db.commit()

    # 8. Tasks (30-Day Onboarding Plan items)
    db.add_all([
        # Phase 1
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Clone repo & spin up pgvector stack locally",
            description="Run docker compose or local postgres with pgvector extension and execute alembic upgrade head.",
            status="Completed",
            priority="High",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 1 (Week 1)",
            is_completed=True,
            is_recommended=False
        ),
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="1-on-1 Architecture walkthrough with Sarah Lin",
            description="Deep dive into double-dispatch partition failover and HNSW index memory limits.",
            status="Completed",
            priority="Critical",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 1 (Week 1)",
            is_completed=True,
            is_recommended=False
        ),
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Verify AWS staging & cluster IAM permissions",
            description="Ensure read/write access to EKS worker node roles and AWS Secrets Manager.",
            status="In Progress",
            priority="Medium",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 1 (Week 1)",
            is_completed=False,
            is_recommended=True
        ),
        # Phase 2
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Resolve #PAY-412 (Webhook retry backoff fix)",
            description="Increase async timeout in worker.py: line 84 to 15s and configure exponential backoff in Redis broker.",
            status="Backlog",
            priority="High",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            blocker_details="Stripe webhook timeout bug during traffic bursts exceeding 4,200 rps batch payouts.",
            immediate_action="Increase async timeout in worker.py: line 84 to 15s and configure exponential backoff in Redis broker.",
            phase="Phase 2 (Week 2)",
            is_completed=False,
            is_recommended=False
        ),
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Shadow Alex Morgan during weekly incident triage",
            description="Participate in primary on-call rotation sync and review unhandled exceptions.",
            status="Backlog",
            priority="Medium",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 2 (Week 2)",
            is_completed=False,
            is_recommended=True
        ),
        # Phase 3
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Execute Celery Redis auto-reconnect migration",
            description="Upgrade broker connection pool settings to prevent stale socket leaks during network splits.",
            status="Backlog",
            priority="Medium",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 3 (Weeks 3-4)",
            is_completed=False,
            is_recommended=False
        ),
        Task(
            project_id=p1.id,
            handover_case_id=case1.id,
            title="Publish v2 API specs to external bank partners",
            description="Distribute OpenAPI 3.1 schema and webhooks authentication guide to partner institutions.",
            status="Backlog",
            priority="Low",
            assignee_name="Marcus Vance",
            assignee_id=marcus.id,
            phase="Phase 3 (Weeks 3-4)",
            is_completed=False,
            is_recommended=True
        ),
    ])
    db.commit()

    # 9. Knowledge Gap Questions
    db.add_all([
        KnowledgeGapQuestion(
            project_id=p1.id,
            handover_case_id=case1.id,
            question="Why was the authentication module not completed for the bank webhook callbacks?",
            rationale="Identified in PR #1420 discussion: callback endpoint currently uses IP allowlisting instead of mTLS signature verification.",
            target_user_name="Sarah Lin (Departing Staff)",
            target_user_id=sarah.id,
            status="Answered",
            answer="Bank integration partner delayed provisioning their production mTLS client certificates until Nov 15. We deployed IP allowlisting as an interim safeguard.",
            answered_at=datetime.now(timezone.utc) - timedelta(days=2),
            respondent_name="Sarah Lin",
            is_clarification=True
        ),
        KnowledgeGapQuestion(
            project_id=p1.id,
            handover_case_id=case1.id,
            question="Webhook retry queue sizing limits under 10k RPS traffic surges?",
            rationale="No metric bounds found in RFC-044 for Redis stream buffer memory limits during external payment gateway outages.",
            target_user_name="Sarah Lin (Departing Staff)",
            target_user_id=sarah.id,
            status="Open",
            answer=None,
            is_clarification=True
        ),
        KnowledgeGapQuestion(
            project_id=p1.id,
            handover_case_id=case1.id,
            question="Pydantic v2 custom decimal encoders in legacy billing endpoints?",
            rationale="Unmerged branch feat/pydantic-v2-billing indicates test failure on fixed-point precision calculations.",
            target_user_name="Sarah Lin (Departing Staff)",
            target_user_id=sarah.id,
            status="Open",
            answer=None,
            is_clarification=True
        ),
        KnowledgeGapQuestion(
            project_id=p2.id,
            handover_case_id=case2.id,
            question="What is preventing the production deployment of the Campus Cafeteria POS integration?",
            rationale="Issue #119 lists unresolved conflict between Rahul and Arjun regarding hardware terminal SDK drivers.",
            target_user_name="Sarah Lin (Departing Staff)",
            target_user_id=sarah.id,
            status="Open",
            answer=None,
            is_clarification=True
        )
    ])
    db.commit()

    # 10. Access Requests (Demonstrating Permission-Aware Redaction)
    db.add_all([
        AccessRequest(
            user_id=marcus.id,
            resource_type="Claim",
            resource_id=c6.id,
            resource_name="Failover Switch Routine & Breakglass Vault Tokens (#CLM-1065)",
            reason="I need access to the breakglass failover script to assume primary on-call cutover readiness.",
            status="Pending",
            requested_at=datetime.now(timezone.utc) - timedelta(hours=4)
        )
    ])
    db.commit()

    # 11. Handover Report
    rep1 = HandoverReport(
        handover_case_id=case1.id,
        version="v2.4 Final Draft",
        title="Core Platform & Payment Gateway Transition",
        executive_summary="Synthesized from 180+ immutable project artifacts. Prepared by departing lead Sarah Lin (Staff Eng) and signed off by Alex Morgan. All architecture claims are tied directly to verifiable Git commits.",
        current_status="Stage 4 of 5 · Sign-off & Verification (Cutover Target: Oct 28, 2024)",
        architecture_summary="Primary settlement worker on FastAPI + RQ Celery with Redis Cluster (4,500 req/s throughput, 84ms P99). Storage on PostgreSQL 16 + pgvector HNSW index.",
        decisions_summary="Migrated to PostgreSQL + pgvector for semantic search & relational ledger (#CLM-1094). Adopted Pydantic v2 + FastAPI (#CLM-1077).",
        team_responsibilities="Sarah Lin (Departing Staff) -> Marcus Vance (Incoming Lead). Supervised by Alex Morgan (Eng Manager).",
        completed_tasks="Database migration, Pydantic v2 benchmarks, Phase 1 Onboarding walkthrough.",
        pending_tasks="#PAY-412 Webhook retry backoff fix, Celery auto-reconnect migration.",
        blockers_summary="Stripe webhook timeout bug during traffic bursts exceeding 4,200 rps batch payouts. Immediate 1st action: Increase async timeout in worker.py: line 84 to 15s and configure exponential backoff in Redis broker.",
        risks_summary="Bus factor 1 on Payment Webhook Engine (98% risk score; 94 commits without secondary reviewer recorded).",
        dependencies_summary="AWS EKS (12 pods), Redis Cluster, PostgreSQL 16 pgvector, Stripe v2 API.",
        missing_information="Clarification pending on webhook retry queue sizing limits under 10k RPS.",
        next_actions="1. Accept resolution on Webhook Failover Circuit Breaker Ownership Discrepancy. 2. Manager signs transition package. 3. Successor signs receipt acknowledgement.",
        supporting_evidence_count=24,
        continuation_plan_json={
            "phase1": ["Clone repo & spin up pgvector stack locally", "1-on-1 Architecture walkthrough with Sarah Lin", "Verify AWS staging & cluster IAM permissions"],
            "phase2": ["Resolve #PAY-412 (Webhook retry backoff fix)", "Shadow Alex Morgan during weekly incident triage"],
            "phase3": ["Execute Celery Redis auto-reconnect migration", "Publish v2 API specs to external bank partners"]
        },
        manager_checklist_json=[
            {"id": "citations", "label": "All claims backed by citations", "detail": "24 of 24 PRs and docs validated", "ready": True},
            {"id": "zero_hallucination", "label": "No hallucinated assertions", "detail": "Zero ungrounded text in v2.4", "ready": True},
            {"id": "dlp_mask", "label": "Credentials & SLAs Redacted", "detail": "DLP mask applied to Stripe live token", "ready": True},
            {"id": "conflicts", "label": "Conflict #882 Resolved", "detail": "Pending resolution above", "ready": False}
        ],
        cryptographic_signature="sha256:7c9e0134bc9812df90a1",
        status="Pending Approval",
        created_at=datetime.now(timezone.utc) - timedelta(hours=6)
    )
    db.add(rep1)
    db.commit()

    # 12. Audit Logs
    db.add_all([
        AuditLog(
            user_id=sarah.id,
            user_name="Sarah Lin",
            user_role="Departing",
            action="SOURCE_UPLOAD",
            entity_type="Source",
            entity_id=s1.source_code,
            details_json={"name": s1.name, "type": s1.source_type, "consent": "Granted"},
            timestamp=datetime.now(timezone.utc) - timedelta(days=5)
        ),
        AuditLog(
            user_id=alex.id,
            user_name="Alex Morgan",
            user_role="Manager",
            action="CLAIM_VERIFY",
            entity_type="Claim",
            entity_id=c1.claim_code,
            details_json={"status": "VERIFIED", "method": "Exact Match", "confidence": 1.0},
            timestamp=datetime.now(timezone.utc) - timedelta(days=3)
        ),
        AuditLog(
            user_id=alex.id,
            user_name="Alex Morgan",
            user_role="Manager",
            action="CONFLICT_FLAGGED",
            entity_type="Conflict",
            entity_id="CONF-882",
            details_json={"discrepancy": "Webhook Circuit Breaker Ownership"},
            timestamp=datetime.now(timezone.utc) - timedelta(days=2)
        ),
        AuditLog(
            user_id=marcus.id,
            user_name="Marcus Vance",
            user_role="Incoming",
            action="ACCESS_REQUEST",
            entity_type="Claim",
            entity_id=c6.claim_code,
            details_json={"reason": "Require access for breakglass routine"},
            timestamp=datetime.now(timezone.utc) - timedelta(hours=4)
        )
    ])

    # 13. Notifications
    db.add_all([
        Notification(
            user_id=marcus.id,
            title="Handover Vault Ready for Review",
            message="Sarah Lin and Alex Morgan have prepared transition package CASE-2024-884A.",
            type="info",
            link="/role-handover"
        ),
        Notification(
            user_id=alex.id,
            title="Action Required: Conflict #882",
            message="Resolve Webhook Failover Circuit Breaker ownership discrepancy before final sign-off.",
            type="warning",
            link="/evidence-board"
        ),
        Notification(
            user_id=sarah.id,
            title="Knowledge Gap Question Waiting",
            message="Marcus Vance submitted an inquiry regarding Webhook retry queue sizing limits under 10k RPS.",
            type="alert",
            link="/knowledge-gaps"
        )
    ])
    db.commit()
    print("Database seeding completed successfully.")

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    DEPARTING = "Departing"
    INCOMING = "Incoming"

class AccessClassification(str, enum.Enum):
    PUBLIC = "Public"
    TEAM = "Team"
    RESTRICTED = "Restricted"
    CONFIDENTIAL = "Confidential"

class EvidenceStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    CONFLICTING = "CONFLICTING"
    MISSING_EVIDENCE = "MISSING EVIDENCE"

class TaskStatus(str, enum.Enum):
    BACKLOG = "Backlog"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"

class HandoverStage(str, enum.Enum):
    STAGE_1 = "Stage 1 of 5 · Knowledge Ingestion"
    STAGE_2 = "Stage 2 of 5 · Conflict Detection"
    STAGE_3 = "Stage 3 of 5 · Gap Resolution"
    STAGE_4 = "Stage 4 of 5 · Sign-off & Verification"
    STAGE_5 = "Stage 5 of 5 · Final Cutover Execution"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.INCOMING.value, nullable=False)
    title = Column(String(255), default="Software Engineer")
    department = Column(String(255), default="Core Platform & Engineering")
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projects_owned = relationship("Project", back_populates="owner")
    claims_authored = relationship("Claim", foreign_keys="Claim.author_id", back_populates="author")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Active")
    bus_factor_score = Column(Float, default=1.0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects_owned")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="project", cascade="all, delete-orphan")
    handover_cases = relationship("HandoverCase", back_populates="project", cascade="all, delete-orphan")
    gap_questions = relationship("KnowledgeGapQuestion", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_in_project = Column(String(50), default="Member")
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="members")
    user = relationship("User")

class HandoverCase(Base):
    __tablename__ = "handover_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True, nullable=False) # e.g. CASE-2024-884A
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    departing_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    successor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approver_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    stage = Column(String(100), default=HandoverStage.STAGE_4.value)
    status = Column(String(50), default="Pending Sign-off") # Draft, In Review, Pending Sign-off, Published, Acknowledged
    target_cutover_date = Column(DateTime, nullable=True)
    grounded_pct = Column(Float, default=94.0)
    consensus_status = Column(String(100), default="BFT Consensus Verified (3/3)")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="handover_cases")
    departing_user = relationship("User", foreign_keys=[departing_user_id])
    successor_user = relationship("User", foreign_keys=[successor_user_id])
    approver_user = relationship("User", foreign_keys=[approver_user_id])
    reports = relationship("HandoverReport", back_populates="handover_case", cascade="all, delete-orphan")
    acknowledgements = relationship("HandoverAcknowledgement", back_populates="handover_case", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    source_code = Column(String(100), unique=True, index=True, nullable=False) # e.g. #PR-1420, #RFC-044-DB
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    source_type = Column(String(100), default="Document") # GitHub PR, Architecture RFC, Slack Thread, Notion Wiki, Jira Ticket, PDF Document
    access_classification = Column(String(50), default=AccessClassification.TEAM.value)
    consent_status = Column(String(50), default="Granted") # Granted, Pending, Revoked
    processing_status = Column(String(50), default="Processed") # Ingesting, Processed, Failed
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_path = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    raw_content = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="sources")
    uploaded_by = relationship("User")
    chunks = relationship("SourceChunk", back_populates="source", cascade="all, delete-orphan")
    claims = relationship("Claim", foreign_keys="Claim.source_id", back_populates="source")

class SourceChunk(Base):
    __tablename__ = "source_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    chunk_index = Column(Integer, default=0)
    line_start = Column(Integer, default=1)
    line_end = Column(Integer, default=10)
    text_content = Column(Text, nullable=False)
    embedding_json = Column(JSON, nullable=True)

    source = relationship("Source", back_populates="chunks")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_code = Column(String(100), unique=True, index=True, nullable=False) # e.g. #CLM-1094
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Decision") # Decision, Owner, TaskStatus, Blocker, Dependency, Risk, OpenQuestion, NextAction, Deadline, UnfinishedWork
    evidence_status = Column(String(50), default=EvidenceStatus.VERIFIED.value) # VERIFIED, INFERRED, CONFLICTING, MISSING EVIDENCE
    confidence_score = Column(Float, default=1.0)
    verification_method = Column(String(100), default="Exact Match") # AST Proved, Exact Match, BFT Consensus, NLP Inferred
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    secondary_source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    exact_quote = Column(Text, nullable=True)
    line_span = Column(String(100), nullable=True) # e.g. Span L48-L56
    primary_code_diff = Column(Text, nullable=True)
    cryptographic_root = Column(String(255), default="sha256:4b91f0...de21")
    golden_ref = Column(Boolean, default=False)
    related_person = Column(String(255), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    signoff_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    access_classification = Column(String(50), default=AccessClassification.TEAM.value)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="claims")
    source = relationship("Source", foreign_keys=[source_id], back_populates="claims")
    secondary_source = relationship("Source", foreign_keys=[secondary_source_id])
    author = relationship("User", foreign_keys=[author_id], back_populates="claims_authored")
    signoff_reviewer = relationship("User", foreign_keys=[signoff_reviewer_id])
    versions = relationship("ClaimVersion", back_populates="claim", cascade="all, delete-orphan")

class ClaimVersion(Base):
    __tablename__ = "claim_versions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    version_num = Column(Integer, default=1)
    previous_value = Column(Text, nullable=True)
    updated_value = Column(Text, nullable=False)
    change_reason = Column(String(255), nullable=True)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    claim = relationship("Claim", back_populates="versions")
    changed_by = relationship("User")

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    decision_code = Column(String(100), unique=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    person_responsible = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=False)
    alternatives_evaluated = Column(Text, nullable=True)
    supporting_evidence = Column(String(255), nullable=True)
    is_reversed = Column(Boolean, default=False)
    is_unresolved = Column(Boolean, default=False)
    evidence_status = Column(String(50), default="VERIFIED")
    tags = Column(String(255), nullable=True) # JSON or comma-separated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="decisions")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=TaskStatus.BACKLOG.value)
    priority = Column(String(50), default="Medium")
    assignee_name = Column(String(255), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    blocker_details = Column(Text, nullable=True)
    immediate_action = Column(Text, nullable=True)
    phase = Column(String(50), default="Phase 1 (Week 1)") # Phase 1, Phase 2, Phase 3
    is_completed = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False) # AI recommendation vs established fact
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="tasks")

class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, index=True)
    conflict_code = Column(String(100), unique=True, index=True, nullable=False) # e.g. CONF-882
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    claim_a_id = Column(Integer, ForeignKey("claims.id"), nullable=True)
    claim_b_id = Column(Integer, ForeignKey("claims.id"), nullable=True)
    source_a_label = Column(String(255), nullable=True) # e.g. Codebase PR #1420 (Sep 12)
    source_a_quote = Column(Text, nullable=True)
    source_a_claim = Column(String(255), nullable=True)
    source_b_label = Column(String(255), nullable=True) # e.g. Arch Sync Notes Slack (Oct 04)
    source_b_quote = Column(Text, nullable=True)
    source_b_claim = Column(String(255), nullable=True)
    recommended_fix = Column(Text, nullable=True)
    resolution_status = Column(String(50), default="Pending") # Pending, Resolved
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="conflicts")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

class KnowledgeGapQuestion(Base):
    __tablename__ = "knowledge_gap_questions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=True)
    question = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    target_user_name = Column(String(255), default="Sarah Lin (Departing Lead)")
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="Open") # Open, Answered
    answer = Column(Text, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    respondent_name = Column(String(255), nullable=True)
    is_clarification = Column(Boolean, default=True) # Distinguishable from source-derived evidence
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="gap_questions")

class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(100), default="Claim") # Claim, Source, Project
    resource_id = Column(Integer, nullable=False)
    resource_name = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="Pending") # Pending, Approved, Rejected
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

class HandoverReport(Base):
    __tablename__ = "handover_reports"

    id = Column(Integer, primary_key=True, index=True)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=False)
    version = Column(String(50), default="v2.4 Final Draft")
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    current_status = Column(Text, nullable=False)
    architecture_summary = Column(Text, nullable=True)
    decisions_summary = Column(Text, nullable=True)
    team_responsibilities = Column(Text, nullable=True)
    completed_tasks = Column(Text, nullable=True)
    pending_tasks = Column(Text, nullable=True)
    blockers_summary = Column(Text, nullable=True)
    risks_summary = Column(Text, nullable=True)
    dependencies_summary = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    next_actions = Column(Text, nullable=True)
    supporting_evidence_count = Column(Integer, default=24)
    continuation_plan_json = Column(JSON, nullable=True)
    manager_checklist_json = Column(JSON, nullable=True)
    cryptographic_signature = Column(String(255), default="sha256:7c9e01...b84f")
    status = Column(String(50), default="Pending Approval") # Draft, Pending Approval, Published
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    handover_case = relationship("HandoverCase", back_populates="reports")
    approved_by = relationship("User")

class HandoverAcknowledgement(Base):
    __tablename__ = "handover_acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    handover_case_id = Column(Integer, ForeignKey("handover_cases.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("handover_reports.id"), nullable=True)
    successor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signature_token = Column(String(255), nullable=False)
    acknowledged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)

    handover_case = relationship("HandoverCase", back_populates="acknowledgements")
    successor_user = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), default="System")
    user_role = Column(String(50), default="System")
    action = Column(String(100), nullable=False) # LOGIN, SOURCE_UPLOAD, CLAIM_EDIT, APPROVE, RESOLVE_CONFLICT, CUTOVER_SIGN, ACCESS_REQUEST
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)
    details_json = Column(JSON, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info") # info, warning, success, alert
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")

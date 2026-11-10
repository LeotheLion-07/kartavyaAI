from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "Incoming"
    title: Optional[str] = "Software Engineer"
    department: Optional[str] = "Core Platform & Engineering"
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    status: Optional[str] = "Active"
    bus_factor_score: Optional[float] = 1.0

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    bus_factor_score: Optional[float] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Source Schemas
class SourceBase(BaseModel):
    source_code: str
    name: str
    source_type: str = "Document"
    access_classification: str = "Team"
    consent_status: str = "Granted"
    processing_status: str = "Processed"
    external_url: Optional[str] = None
    raw_content: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class SourceCreate(SourceBase):
    project_id: int

class SourceResponse(SourceBase):
    id: int
    project_id: int
    uploaded_by_id: Optional[int] = None
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Claim Schemas
class ClaimBase(BaseModel):
    claim_code: str
    title: str
    description: str
    category: str = "Decision"
    evidence_status: str = "VERIFIED"
    confidence_score: float = 1.0
    verification_method: str = "Exact Match"
    exact_quote: Optional[str] = None
    line_span: Optional[str] = None
    primary_code_diff: Optional[str] = None
    cryptographic_root: Optional[str] = "sha256:4b91f0...de21"
    golden_ref: bool = False
    related_person: Optional[str] = None
    access_classification: str = "Team"
    is_approved: bool = True

class ClaimCreate(ClaimBase):
    project_id: int
    handover_case_id: Optional[int] = None
    source_id: Optional[int] = None
    secondary_source_id: Optional[int] = None

class ClaimUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_status: Optional[str] = None
    confidence_score: Optional[float] = None
    is_approved: Optional[bool] = None
    change_reason: Optional[str] = "Manual update via Review Board"

class ClaimResponse(ClaimBase):
    id: int
    project_id: int
    handover_case_id: Optional[int] = None
    source_id: Optional[int] = None
    secondary_source_id: Optional[int] = None
    author_id: Optional[int] = None
    signoff_reviewer_id: Optional[int] = None
    source_name: Optional[str] = None
    is_redacted: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Claim Version
class ClaimVersionResponse(BaseModel):
    id: int
    claim_id: int
    version_num: int
    previous_value: Optional[str] = None
    updated_value: str
    change_reason: Optional[str] = None
    changed_by_user_id: Optional[int] = None
    changed_by_name: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Decision Schemas
class DecisionBase(BaseModel):
    decision_code: str
    title: str
    date: Optional[datetime] = None
    person_responsible: str
    rationale: str
    alternatives_evaluated: Optional[str] = None
    supporting_evidence: Optional[str] = None
    is_reversed: bool = False
    is_unresolved: bool = False
    evidence_status: str = "VERIFIED"
    tags: Optional[str] = None

class DecisionCreate(DecisionBase):
    project_id: int

class DecisionResponse(DecisionBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Backlog"
    priority: str = "Medium"
    assignee_name: Optional[str] = None
    blocker_details: Optional[str] = None
    immediate_action: Optional[str] = None
    phase: str = "Phase 1 (Week 1)"
    is_completed: bool = False
    is_recommended: bool = False

class TaskCreate(TaskBase):
    project_id: int
    handover_case_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = None
    blocker_details: Optional[str] = None
    immediate_action: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    handover_case_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Conflict Schemas
class ConflictBase(BaseModel):
    conflict_code: str
    title: str
    description: str
    source_a_label: Optional[str] = None
    source_a_quote: Optional[str] = None
    source_a_claim: Optional[str] = None
    source_b_label: Optional[str] = None
    source_b_quote: Optional[str] = None
    source_b_claim: Optional[str] = None
    recommended_fix: Optional[str] = None
    resolution_status: str = "Pending"
    resolution_notes: Optional[str] = None

class ConflictCreate(ConflictBase):
    project_id: int
    handover_case_id: Optional[int] = None

class ConflictResolve(BaseModel):
    resolution_notes: str
    accepted_fix: Optional[str] = None

class ConflictResponse(ConflictBase):
    id: int
    project_id: int
    handover_case_id: Optional[int] = None
    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Knowledge Gap Question
class KnowledgeGapBase(BaseModel):
    question: str
    rationale: Optional[str] = None
    target_user_name: Optional[str] = "Sarah Lin (Departing Lead)"

class KnowledgeGapCreate(KnowledgeGapBase):
    project_id: int
    handover_case_id: Optional[int] = None

class KnowledgeGapAnswer(BaseModel):
    answer: str
    respondent_name: Optional[str] = None

class KnowledgeGapResponse(KnowledgeGapBase):
    id: int
    project_id: int
    status: str
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    respondent_name: Optional[str] = None
    is_clarification: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

# Access Request
class AccessRequestCreate(BaseModel):
    resource_type: str = "Claim"
    resource_id: int
    resource_name: str
    reason: Optional[str] = "Require access to proceed with architecture review"

class AccessRequestReview(BaseModel):
    status: str # Approved, Rejected
    review_comment: Optional[str] = None

class AccessRequestResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    resource_type: str
    resource_id: int
    resource_name: str
    reason: Optional[str] = None
    status: str
    reviewed_by_id: Optional[int] = None
    review_comment: Optional[str] = None
    requested_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Handover Case
class HandoverCaseBase(BaseModel):
    case_number: str
    title: str
    stage: str = "Stage 4 of 5 · Sign-off & Verification"
    status: str = "Pending Sign-off"
    target_cutover_date: Optional[datetime] = None
    grounded_pct: float = 94.0
    consensus_status: str = "BFT Consensus Verified (3/3)"

class HandoverCaseCreate(HandoverCaseBase):
    project_id: int
    departing_user_id: Optional[int] = None
    successor_user_id: Optional[int] = None

class HandoverCaseResponse(HandoverCaseBase):
    id: int
    project_id: int
    departing_user: Optional[UserResponse] = None
    successor_user: Optional[UserResponse] = None
    approver_user: Optional[UserResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Handover Report & Acknowledgement
class HandoverReportResponse(BaseModel):
    id: int
    handover_case_id: int
    version: str
    title: str
    executive_summary: str
    current_status: str
    architecture_summary: Optional[str] = None
    decisions_summary: Optional[str] = None
    team_responsibilities: Optional[str] = None
    completed_tasks: Optional[str] = None
    pending_tasks: Optional[str] = None
    blockers_summary: Optional[str] = None
    risks_summary: Optional[str] = None
    dependencies_summary: Optional[str] = None
    missing_information: Optional[str] = None
    next_actions: Optional[str] = None
    supporting_evidence_count: int = 24
    continuation_plan_json: Optional[Dict[str, Any]] = None
    manager_checklist_json: Optional[Dict[str, Any]] = None
    cryptographic_signature: str
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = "Acknowledged and received handover briefing. Verified all initial access tokens and repo setups."

# Grounded Chat
class GroundedChatRequest(BaseModel):
    project_id: int
    query: str

class Citation(BaseModel):
    claim_id: int
    claim_code: str
    title: str
    source_name: str
    exact_quote: str
    line_span: Optional[str] = None
    confidence: float

class GroundedChatResponse(BaseModel):
    query: str
    answer: str
    is_grounded: bool
    evidence_count: int
    citations: List[Citation]
    redacted_items_count: int = 0

# Audit Log
class AuditLogResponse(BaseModel):
    id: int
    user_name: str
    user_role: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None
    ip_address: str
    timestamp: datetime

    class Config:
        from_attributes = True

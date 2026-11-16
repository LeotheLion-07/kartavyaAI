from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import (
    KnowledgeGapQuestion, Claim, Decision, Task, Conflict, Source, Project
)
from app.core.security import log_audit_event

def detect_and_generate_gap_questions(
    project_id: int,
    db: Session,
    handover_case_id: Optional[int] = None,
    target_user_name: str = "Sarah Lin (Departing Lead)"
) -> List[KnowledgeGapQuestion]:
    """
    Automated Knowledge-Gap Identification Engine.
    Scans project state across 10 knowledge dimensions:
    1. Decisions and rationale
    2. Ownership
    3. Task status
    4. Blockers
    5. Dependencies
    6. Risks
    7. Open inquiries
    8. Next actions
    9. Deadlines
    10. Unfinished work

    Formulates targeted inquiries directed to the departing lead.
    Avoids duplicate questions for already-tracked gaps.
    """
    existing_gaps = db.query(KnowledgeGapQuestion).filter(
        KnowledgeGapQuestion.project_id == project_id
    ).all()

    # Build deduplication signatures
    existing_signatures: Set[str] = set()
    for g in existing_gaps:
        sig = f"{g.category or ''}:{g.entity_or_subject or ''}".lower()
        existing_signatures.add(sig)
        # Also match by normalized question content
        q_norm = " ".join(g.question.lower().split()[:6])
        existing_signatures.add(q_norm)

    candidates: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # 1. Decisions & Rationale Gaps
    # Check decisions table or decision claims that lack rationale or alternatives
    # -------------------------------------------------------------------------
    decisions = db.query(Decision).filter(Decision.project_id == project_id).all()
    for d in decisions:
        rat = (d.rationale or "").strip().lower()
        alts = (d.alternatives_evaluated or "").strip().lower()
        if len(rat) < 15 or "todo" in rat or not alts:
            candidates.append({
                "category": "DecisionRationale",
                "entity_or_subject": d.title,
                "priority": "High",
                "question": f"Why was {d.title} selected instead of the alternatives, and what was the underlying rationale?",
                "rationale": f"Decision #{d.decision_code} lacks documented justification or comparative alternatives analysis."
            })

    # Also check decision claims
    decision_claims = db.query(Claim).filter(
        Claim.project_id == project_id,
        Claim.category == "Decision"
    ).all()
    for dc in decision_claims:
        desc = (dc.description or "").lower()
        quote = (dc.exact_quote or "").lower()
        if "specifies" in desc or "adopted" in desc:
            subj = dc.entity_or_subject or dc.title
            if not any(k in quote for k in ["because", "due to", "in order to", "evaluated"]):
                candidates.append({
                    "category": "DecisionRationale",
                    "entity_or_subject": subj,
                    "priority": "High",
                    "question": f"What was the architectural reason behind the selection for {subj}?",
                    "rationale": f"Decision recorded in {dc.claim_code} does not detail why this architecture was chosen over alternatives."
                })

    # -------------------------------------------------------------------------
    # 2. Task Ownership Gaps
    # Unfinished tasks or active modules with no recorded owner/assignee
    # -------------------------------------------------------------------------
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    for t in tasks:
        if not t.is_completed and not t.assignee_name and not t.assignee_id:
            candidates.append({
                "category": "Ownership",
                "entity_or_subject": t.title,
                "priority": "High",
                "question": f"Who is currently responsible for completing and maintaining the {t.title}?",
                "rationale": f"Task '{t.title}' is active/backlog but has no primary owner assigned in project records."
            })

    # -------------------------------------------------------------------------
    # 3. Blocker Resolution Gaps
    # Blocker claims without a documented resolution or next steps
    # -------------------------------------------------------------------------
    blocker_claims = db.query(Claim).filter(
        Claim.project_id == project_id,
        Claim.category == "Blocker"
    ).all()
    for bc in blocker_claims:
        subj = bc.entity_or_subject or bc.title
        candidates.append({
            "category": "BlockerResolution",
            "entity_or_subject": subj,
            "priority": "High",
            "question": f"What is preventing the {subj} from functioning, and what is the required workaround or resolution?",
            "rationale": f"Active operational blocker flagged in {bc.claim_code} ({bc.exact_quote[:80]}...) without confirmed resolution."
        })

    # -------------------------------------------------------------------------
    # 4. Dependency & Service Gaps
    # Dependency claims without configuration details or owner
    # -------------------------------------------------------------------------
    dep_claims = db.query(Claim).filter(
        Claim.project_id == project_id,
        Claim.category == "Dependency"
    ).all()
    for dep in dep_claims:
        subj = dep.entity_or_subject or dep.title
        candidates.append({
            "category": "Dependency",
            "entity_or_subject": subj,
            "priority": "Medium",
            "question": f"Which external credentials or configurations must be provisioned for {subj} before deployment?",
            "rationale": f"Dependency relationship recorded in {dep.claim_code} requires runtime operational setup instructions."
        })

    # -------------------------------------------------------------------------
    # 5. Next Actions / Priority Gaps
    # Unfinished work with no clear immediate next step
    # -------------------------------------------------------------------------
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    if incomplete_tasks:
        primary_t = incomplete_tasks[0]
        if not primary_t.immediate_action:
            candidates.append({
                "category": "NextAction",
                "entity_or_subject": primary_t.title,
                "priority": "High",
                "question": f"What should the incoming developer work on first regarding {primary_t.title}?",
                "rationale": f"Unfinished module '{primary_t.title}' lacks a sequenced 1st action for incoming successor onboarding."
            })

    # -------------------------------------------------------------------------
    # 6. Unresolved Conflict Ambiguity Gaps
    # If conflicting records exist, formulate inquiry to clarify authoritative state
    # -------------------------------------------------------------------------
    pending_conflicts = db.query(Conflict).filter(
        Conflict.project_id == project_id,
        Conflict.resolution_status == "Pending"
    ).all()
    for conf in pending_conflicts:
        subj = conf.entity_or_subject or conf.title
        candidates.append({
            "category": "AmbiguityResolution",
            "entity_or_subject": subj,
            "priority": "High",
            "question": f"Can you clarify the discrepancy on {subj}: is {conf.source_a_value or 'Source A'} or {conf.source_b_value or 'Source B'} the intended design?",
            "rationale": f"Contradiction {conf.conflict_code} exists between {conf.source_a_label} and {conf.source_b_label}."
        })

    # -------------------------------------------------------------------------
    # Persist non-duplicate questions
    # -------------------------------------------------------------------------
    created_questions: List[KnowledgeGapQuestion] = []
    for cand in candidates:
        sig = f"{cand['category']}:{cand['entity_or_subject']}".lower()
        q_norm = " ".join(cand['question'].lower().split()[:6])

        if sig in existing_signatures or q_norm in existing_signatures:
            continue

        q_obj = KnowledgeGapQuestion(
            project_id=project_id,
            handover_case_id=handover_case_id,
            category=cand["category"],
            entity_or_subject=cand["entity_or_subject"],
            priority=cand["priority"],
            question=cand["question"],
            rationale=cand["rationale"],
            target_user_name=target_user_name,
            status="Open",
            is_clarification=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(q_obj)
        created_questions.append(q_obj)
        existing_signatures.add(sig)
        existing_signatures.add(q_norm)

    if created_questions:
        db.commit()
        for q in created_questions:
            db.refresh(q)
            log_audit_event(
                db=db,
                user_id=None,
                user_name="KnowledgeGapDetector",
                user_role="System",
                action="GAP_QUESTION_AUTO_GENERATE",
                entity_type="KnowledgeGap",
                entity_id=str(q.id),
                details_json={
                    "category": q.category,
                    "entity": q.entity_or_subject,
                    "question": q.question
                }
            )

    return created_questions

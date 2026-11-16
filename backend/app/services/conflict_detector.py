import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import Claim, Conflict, Source, AuditLog
from app.core.dlp import mask_sensitive_tokens
from app.core.security import log_audit_event

def normalize_key(text: Optional[str]) -> str:
    """Normalizes string for comparison by stripping stopwords, punctuation, and casing."""
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"^(the|a|an|project)\s+", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    return " ".join(t.split())

def values_are_contradictory(cat: str, val1: str, val2: str) -> bool:
    """Evaluates whether two extracted values in a given category are genuinely contradictory."""
    norm1 = normalize_key(val1)
    norm2 = normalize_key(val2)
    if not norm1 or not norm2:
        return False
    if norm1 == norm2:
        return False  # Identical value is not a conflict

    if cat == "Ownership":
        # Contradictory if assignees are distinct people
        return norm1 != norm2

    elif cat == "Decision":
        # Contradictory architectural choices (e.g. postgresql vs mongodb, celery vs kafka)
        return norm1 != norm2

    elif cat == "TaskStatus" or cat == "TaskCompletion":
        # Conflicting statuses: completed/done vs in progress/backlog/pending/blocked
        completed_set = {"completed", "done", "finished", "resolved"}
        in_progress_set = {"in progress", "active", "in backlog", "backlog", "pending", "unfinished", "blocked"}
        is1_done = any(k in norm1 for k in completed_set)
        is2_done = any(k in norm2 for k in completed_set)
        is1_prog = any(k in norm1 for k in in_progress_set)
        is2_prog = any(k in norm2 for k in in_progress_set)

        if (is1_done and is2_prog) or (is2_done and is1_prog):
            return True
        return norm1 != norm2

    elif cat == "Deadline":
        # Different dates or numbers
        return norm1 != norm2

    elif cat == "Dependency":
        # Different external services or dependencies
        return norm1 != norm2

    return False

def detect_conflicts_between_claims(claims: List[Claim]) -> List[Dict[str, Any]]:
    """
    Evaluates a collection of project claims and identifies contradictory assertions
    across distinct sources across the 5 mandatory categories:
    1. Task ownership
    2. Project decisions
    3. Task completion / status
    4. Deadlines
    5. Dependencies & responsibilities
    """
    conflicts: List[Dict[str, Any]] = []

    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            c1 = claims[i]
            c2 = claims[j]

            # Claims from the exact same source chunk do not constitute cross-source conflict
            if c1.source_id and c2.source_id and c1.source_id == c2.source_id:
                continue

            # Determine category to compare
            cat1 = c1.category or "General"
            cat2 = c2.category or "General"

            # Check if entities or subjects match
            subj1 = c1.entity_or_subject or c1.title
            subj2 = c2.entity_or_subject or c2.title
            norm_subj1 = normalize_key(subj1)
            norm_subj2 = normalize_key(subj2)

            # Match criteria: either normalized entity match or strong token overlap
            tokens1 = set(norm_subj1.split())
            tokens2 = set(norm_subj2.split())
            stop_tokens = {"module", "service", "task", "project", "engine", "system", "pipeline", "component"}
            sig_tokens1 = tokens1 - stop_tokens
            sig_tokens2 = tokens2 - stop_tokens
            has_subject_match = bool(norm_subj1 == norm_subj2 or (sig_tokens1 and sig_tokens2 and sig_tokens1 & sig_tokens2))

            if not has_subject_match:
                continue

            # Extract values to compare
            val1 = c1.extracted_value or c1.related_person or c1.title
            val2 = c2.extracted_value or c2.related_person or c2.title

            # Check if either claim is an ownership, decision, status, deadline, or dependency claim
            matched_cat = None
            if cat1 == "Ownership" or cat2 == "Ownership" or (c1.related_person and c2.related_person):
                matched_cat = "Ownership"
                val1 = c1.related_person or c1.extracted_value
                val2 = c2.related_person or c2.extracted_value
            elif cat1 == "Decision" and cat2 == "Decision":
                matched_cat = "Decision"
            elif (cat1 in ["TaskStatus", "NextAction"] or cat2 in ["TaskStatus", "NextAction"]):
                matched_cat = "TaskCompletion"
            elif cat1 == "Deadline" or cat2 == "Deadline":
                matched_cat = "Deadline"
            elif cat1 == "Dependency" or cat2 == "Dependency":
                matched_cat = "Dependency"
            elif cat1 == cat2:
                matched_cat = cat1

            if not matched_cat:
                continue

            # Test if values are contradictory
            if values_are_contradictory(matched_cat, val1, val2):
                # Inherit most restrictive access classification
                classif1 = (c1.access_classification or "Team").capitalize()
                classif2 = (c2.access_classification or "Team").capitalize()
                final_classif = "Restricted" if "Restricted" in [classif1, classif2] or "Confidential" in [classif1, classif2] else "Team"

                s1_name = c1.source.name if c1.source else f"Source #{c1.source_id}"
                s2_name = c2.source.name if c2.source else f"Source #{c2.source_id}"
                s1_code = c1.source.source_code if c1.source else "Source A"
                s2_code = c2.source.source_code if c2.source else "Source B"

                detection_reason = (
                    f"Contradictory assertions detected for '{subj1}': "
                    f"'{val1}' asserted in {s1_code} vs '{val2}' asserted in {s2_code}."
                )

                recommended_fix = (
                    f"Reconcile authoritative state for '{subj1}'. Clarify whether "
                    f"'{val1}' ({s1_code}) or '{val2}' ({s2_code}) governs going forward."
                )

                conflicts.append({
                    "category": matched_cat,
                    "entity_or_subject": subj1,
                    "title": f"{matched_cat} Contradiction: {subj1}",
                    "description": detection_reason,
                    "detection_reason": detection_reason,
                    "claim_a_id": c1.id,
                    "claim_b_id": c2.id,
                    "source_a_label": f"{s1_code} ({s1_name})",
                    "source_a_quote": c1.exact_quote or c1.description,
                    "source_a_claim": f"{matched_cat}: {val1}",
                    "source_a_value": val1,
                    "source_b_label": f"{s2_code} ({s2_name})",
                    "source_b_quote": c2.exact_quote or c2.description,
                    "source_b_claim": f"{matched_cat}: {val2}",
                    "source_b_value": val2,
                    "recommended_fix": recommended_fix,
                    "resolution_status": "Pending",
                    "access_classification": final_classif
                })

    return conflicts

def detect_and_persist_conflicts(
    project_id: int,
    db: Session,
    handover_case_id: Optional[int] = None
) -> List[Conflict]:
    """
    Automated conflict detection engine:
    1. Retrieves all claims for the given project.
    2. Compares claims across sources for category-specific contradictions.
    3. Checks existing conflicts to guarantee idempotent, deduplicated storage.
    4. Persists verified conflicts and marks involved claims as CONFLICTING.
    5. Records audit events.
    """
    claims = db.query(Claim).filter(Claim.project_id == project_id).all()
    if len(claims) < 2:
        return []

    detected_candidates = detect_conflicts_between_claims(claims)
    existing_conflicts = db.query(Conflict).filter(Conflict.project_id == project_id).all()

    # Build deduplication lookup keys
    existing_keys: Set[str] = set()
    for ex in existing_conflicts:
        # Key based on claim pair
        if ex.claim_a_id and ex.claim_b_id:
            pair1 = f"{min(ex.claim_a_id, ex.claim_b_id)}:{max(ex.claim_a_id, ex.claim_b_id)}"
            existing_keys.add(pair1)
        # Key based on subject and category
        if ex.entity_or_subject and ex.category:
            sem_key = f"{normalize_key(ex.category)}:{normalize_key(ex.entity_or_subject)}"
            existing_keys.add(sem_key)

    created_conflicts: List[Conflict] = []
    all_codes = {code[0] for code in db.query(Conflict.conflict_code).all()}
    counter = 880 + len(all_codes) + 1

    for cand in detected_candidates:
        c_a_id = cand.get("claim_a_id")
        c_b_id = cand.get("claim_b_id")
        pair_key = f"{min(c_a_id, c_b_id)}:{max(c_a_id, c_b_id)}" if c_a_id and c_b_id else None
        sem_key = f"{normalize_key(cand.get('category'))}:{normalize_key(cand.get('entity_or_subject'))}"

        if (pair_key and pair_key in existing_keys) or sem_key in existing_keys:
            continue  # Avoid duplicate records on re-ingestion

        while f"CONF-{counter}" in all_codes:
            counter += 1
        conflict_code = f"CONF-{counter}"
        all_codes.add(conflict_code)
        counter += 1

        conf_obj = Conflict(
            conflict_code=conflict_code,
            project_id=project_id,
            handover_case_id=handover_case_id,
            title=cand["title"],
            description=cand["description"],
            category=cand["category"],
            entity_or_subject=cand["entity_or_subject"],
            detection_reason=cand["detection_reason"],
            claim_a_id=c_a_id,
            claim_b_id=c_b_id,
            source_a_label=cand["source_a_label"],
            source_a_quote=cand["source_a_quote"],
            source_a_claim=cand["source_a_claim"],
            source_a_value=cand["source_a_value"],
            source_b_label=cand["source_b_label"],
            source_b_quote=cand["source_b_quote"],
            source_b_claim=cand["source_b_claim"],
            source_b_value=cand["source_b_value"],
            recommended_fix=cand["recommended_fix"],
            resolution_status="Pending",
            access_classification=cand.get("access_classification", "Team")
        )
        db.add(conf_obj)
        created_conflicts.append(conf_obj)

        if pair_key:
            existing_keys.add(pair_key)
        existing_keys.add(sem_key)

        # Mark both claims as CONFLICTING so users and retrieval know ambiguity exists
        if c_a_id:
            c1 = db.query(Claim).filter(Claim.id == c_a_id).first()
            if c1 and c1.evidence_status != "CONFLICTING":
                c1.evidence_status = "CONFLICTING"
        if c_b_id:
            c2 = db.query(Claim).filter(Claim.id == c_b_id).first()
            if c2 and c2.evidence_status != "CONFLICTING":
                c2.evidence_status = "CONFLICTING"

    if created_conflicts:
        db.commit()
        for c in created_conflicts:
            db.refresh(c)
            log_audit_event(
                db=db,
                user_id=None,
                user_name="ConflictDetectionEngine",
                user_role="System",
                action="CONFLICT_DETECTED",
                entity_type="Conflict",
                entity_id=c.conflict_code,
                details_json={
                    "title": c.title,
                    "category": c.category,
                    "entity": c.entity_or_subject
                }
            )

    return created_conflicts

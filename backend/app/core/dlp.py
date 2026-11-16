import re
from typing import List, Any, Optional, Set

# Regex patterns for sensitive credentials & tokens
SENSITIVE_PATTERNS = [
    (re.compile(r"sk_live_[0-9a-zA-Z]{24,}", re.IGNORECASE), "[REDACTED_STRIPE_LIVE_KEY]"),
    (re.compile(r"sk_test_[0-9a-zA-Z]{24,}", re.IGNORECASE), "[REDACTED_STRIPE_TEST_KEY]"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36,}", re.IGNORECASE), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"-----BEGIN (?:[A-Z\s]+ )?PRIVATE KEY-----[^-]+-----END (?:[A-Z\s]+ )?PRIVATE KEY-----", re.DOTALL | re.IGNORECASE), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"(?:postgres|postgresql|mysql|mongodb|redis|sqlite)://[^\s\"']+", re.IGNORECASE), "[REDACTED_DATABASE_CREDENTIALS]"),
    (re.compile(r"(?:api_key|apikey|secret|password|access_token|vault_key|auth_token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?", re.IGNORECASE), "[REDACTED_VAULT_KEY]"),
    (re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE), "Bearer [REDACTED_AUTH_TOKEN]"),
    (re.compile(r"(AKIA[0-9A-Z]{16})", re.IGNORECASE), "[REDACTED_AWS_ACCESS_KEY]"),
    (re.compile(r"(--force-token=)[a-zA-Z0-9_\-]+", re.IGNORECASE), r"\1[REDACTED_VAULT_KEY]"),
    (re.compile(r"hsm_token_[0-9a-zA-Z_\-]+", re.IGNORECASE), "[REDACTED_HSM_TOKEN]"),
    (re.compile(r"SECRET_MARKER_[0-9a-zA-Z_\-]+", re.IGNORECASE), "[REDACTED_SECRET_MARKER]"),
]

def mask_sensitive_tokens(text: str) -> str:
    """Masks secrets, passwords, tokens and credentials with DLP labels."""
    if not text:
        return text
    masked = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked

def user_can_access_classification(
    user_role: str,
    classification: str,
    user_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    approved_ids: Optional[Set[int]] = None,
    resource_id: Optional[int] = None
) -> bool:
    """
    Enforces server-level RBAC/ABAC for data classifications:
    Public, Team, Restricted, Confidential.
    """
    role = (user_role or "").lower()
    
    # Admins and Managers have full visibility within permitted projects
    if "admin" in role or "manager" in role:
        return True
        
    classif = (classification or "team").lower()
    
    # Public is available to everyone
    if classif == "public":
        return True
        
    # Team is available to verified team members
    if classif == "team":
        return True
        
    # Check if user has explicit approved access request
    if approved_ids and resource_id in approved_ids:
        return True
        
    # Departing user can access items they authored or uploaded
    if "departing" in role and user_id and owner_id and user_id == owner_id:
        return True
        
    # Restricted / Confidential is strictly blocked for incoming successor until requested & approved
    return False

def redact_claim_if_restricted(
    claim_dict: dict,
    user_role: str,
    user_id: Optional[int] = None,
    approved_claim_ids: Optional[Set[int]] = None
) -> dict:
    """Redacts single claim if user lacks permission."""
    classification = claim_dict.get("access_classification", "Team")
    claim_id = claim_dict.get("id")
    author_id = claim_dict.get("author_id")
    
    if not user_can_access_classification(user_role, classification, user_id, author_id, approved_claim_ids, claim_id):
        return {
            "id": claim_id,
            "claim_code": claim_dict.get("claim_code", "CLM-REDACTED"),
            "title": "Restricted Knowledge Asset",
            "description": "1 related item hidden. Request access.",
            "category": claim_dict.get("category", "General"),
            "evidence_status": "RESTRICTED",
            "confidence_score": 0.0,
            "is_redacted": True,
            "access_classification": classification,
            "created_at": claim_dict.get("created_at")
        }
        
    # If allowed, ensure tokens inside quotes and text are DLP masked
    sanitized = claim_dict.copy()
    if sanitized.get("description"):
        sanitized["description"] = mask_sensitive_tokens(sanitized["description"])
    if sanitized.get("exact_quote"):
        sanitized["exact_quote"] = mask_sensitive_tokens(sanitized["exact_quote"])
    sanitized["is_redacted"] = False
    return sanitized

def redact_source_if_restricted(
    source_dict: dict,
    user_role: str,
    user_id: Optional[int] = None,
    approved_source_ids: Optional[Set[int]] = None
) -> dict:
    """Redacts source metadata and content if user lacks permission."""
    classification = source_dict.get("access_classification", "Team")
    source_id = source_dict.get("id")
    uploaded_by_id = source_dict.get("uploaded_by_id")
    
    if not user_can_access_classification(user_role, classification, user_id, uploaded_by_id, approved_source_ids, source_id):
        return {
            "id": source_id,
            "source_code": source_dict.get("source_code", "#RESTRICTED"),
            "project_id": source_dict.get("project_id"),
            "name": "[REDACTED — ACCESS RESTRICTED]",
            "source_type": source_dict.get("source_type", "Document"),
            "access_classification": classification,
            "consent_status": source_dict.get("consent_status", "Granted"),
            "processing_status": "Restricted",
            "raw_content": None,
            "is_redacted": True,
            "created_at": source_dict.get("created_at")
        }
        
    sanitized = source_dict.copy()
    if sanitized.get("raw_content"):
        sanitized["raw_content"] = mask_sensitive_tokens(sanitized["raw_content"])
    sanitized["is_redacted"] = False
    return sanitized

def redact_conflict_if_restricted(
    conflict_dict: dict,
    user_role: str,
    user_id: Optional[int] = None,
    approved_ids: Optional[Set[int]] = None
) -> dict:
    """Redacts conflict record if it contains restricted claims or classification."""
    classification = conflict_dict.get("access_classification", "Team")
    conflict_id = conflict_dict.get("id")
    
    if not user_can_access_classification(user_role, classification, user_id, None, approved_ids, conflict_id):
        return {
            "id": conflict_id,
            "conflict_code": conflict_dict.get("conflict_code", "CONF-REDACTED"),
            "project_id": conflict_dict.get("project_id"),
            "title": "Restricted Conflict Notice",
            "description": "1 related item hidden. Request access.",
            "category": conflict_dict.get("category", "General"),
            "source_a_label": "Restricted Source",
            "source_a_quote": "[REDACTED — ACCESS RESTRICTED]",
            "source_a_claim": "[REDACTED — ACCESS RESTRICTED]",
            "source_b_label": "Restricted Source",
            "source_b_quote": "[REDACTED — ACCESS RESTRICTED]",
            "source_b_claim": "[REDACTED — ACCESS RESTRICTED]",
            "recommended_fix": "Request access to review sensitive conflict evidence.",
            "resolution_status": conflict_dict.get("resolution_status", "Pending"),
            "is_redacted": True,
            "access_classification": classification,
            "created_at": conflict_dict.get("created_at")
        }
        
    sanitized = conflict_dict.copy()
    if sanitized.get("source_a_quote"):
        sanitized["source_a_quote"] = mask_sensitive_tokens(sanitized["source_a_quote"])
    if sanitized.get("source_b_quote"):
        sanitized["source_b_quote"] = mask_sensitive_tokens(sanitized["source_b_quote"])
    if sanitized.get("description"):
        sanitized["description"] = mask_sensitive_tokens(sanitized["description"])
    sanitized["is_redacted"] = False
    return sanitized

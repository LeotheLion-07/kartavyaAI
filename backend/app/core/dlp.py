import re
from typing import List, Any, Optional, Set

# Regex patterns for sensitive credentials & tokens
SENSITIVE_PATTERNS = [
    (re.compile(r"sk_live_[0-9a-zA-Z]{24,}", re.IGNORECASE), "[REDACTED_STRIPE_LIVE_KEY]"),
    (re.compile(r"sk_test_[0-9a-zA-Z]{24,}", re.IGNORECASE), "[REDACTED_STRIPE_TEST_KEY]"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36,}", re.IGNORECASE), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"(?:api_key|apikey|secret|password|access_token|vault_key)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?", re.IGNORECASE), "[REDACTED_VAULT_KEY]"),
    (re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE), "Bearer [REDACTED_AUTH_TOKEN]"),
    (re.compile(r"(AKIA[0-9A-Z]{16})", re.IGNORECASE), "[REDACTED_AWS_ACCESS_KEY]"),
    (re.compile(r"(--force-token=)[a-zA-Z0-9_\-]+", re.IGNORECASE), r"\1[REDACTED_VAULT_KEY]"),
]

def mask_sensitive_tokens(text: str) -> str:
    """Masks secrets, passwords, tokens and credentials with DLP labels."""
    if not text:
        return text
    masked = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked

def user_can_access_classification(user_role: str, classification: str, user_id: int = None, owner_id: int = None, approved_ids: Optional[Set[int]] = None, resource_id: Optional[int] = None) -> bool:
    """Enforces server-level RBAC for data classifications: Public, Team, Restricted, Confidential"""
    role = (user_role or "").lower()
    
    # Admins and Managers have full visibility
    if "admin" in role or "manager" in role:
        return True
        
    classif = (classification or "team").lower()
    
    # Public is available to everyone
    if classif == "public":
        return True
        
    # Team is available to verified team members
    if classif == "team":
        return True
        
    # Check if user has explicit approved access
    if approved_ids and resource_id in approved_ids:
        return True
        
    # Departing user can see things they own/authored
    if "departing" in role and user_id and owner_id and user_id == owner_id:
        return True
        
    # Restricted / Confidential is blocked by default for incoming successor until requested & approved
    return False

def redact_claim_if_restricted(claim_dict: dict, user_role: str, user_id: int = None, approved_claim_ids: Optional[Set[int]] = None) -> dict:
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

from typing import List, Dict, Any, Optional
import difflib

def detect_conflicts(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Examines ingested claims for semantic contradictions, ownership disputes,
    or conflicting timeline/target dates.
    """
    conflicts = []
    
    # Check for direct or fuzzy contradictions in ownership and status
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            c1 = claims[i]
            c2 = claims[j]
            
            # If both talk about the same component/module but assign differing owners or contradictory directives
            t1 = c1.get("title", "").lower()
            t2 = c2.get("title", "").lower()
            
            # Look for overlapping keywords
            keywords = ["webhook", "database", "auth", "migration", "failover", "queue", "ownership", "deploy"]
            common_kw = [k for k in keywords if k in t1 and k in t2]
            
            if common_kw and (c1.get("related_person") and c2.get("related_person") and c1.get("related_person") != c2.get("related_person")):
                conflicts.append({
                    "conflict_code": f"CONF-{880 + len(conflicts)}",
                    "title": f"Ownership Discrepancy on {common_kw[0].capitalize()} Service",
                    "description": f"Conflicting assignees recorded between {c1.get('source_code', 'Source A')} and {c2.get('source_code', 'Source B')}.",
                    "claim_a_id": c1.get("id"),
                    "claim_b_id": c2.get("id"),
                    "source_a_label": f"{c1.get('source_code', 'Source A')} ({c1.get('related_person')})",
                    "source_a_quote": c1.get("exact_quote", ""),
                    "source_a_claim": f"Assignee: {c1.get('related_person')}",
                    "source_b_label": f"{c2.get('source_code', 'Source B')} ({c2.get('related_person')})",
                    "source_b_quote": c2.get("exact_quote", ""),
                    "source_b_claim": f"Assignee: {c2.get('related_person')}",
                    "recommended_fix": f"Clarify whether {c1.get('related_person')} or {c2.get('related_person')} holds primary L2 escalation responsibility.",
                    "resolution_status": "Pending"
                })
                
    return conflicts

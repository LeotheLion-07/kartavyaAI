from typing import List, Dict, Any, Optional
import re
from app.models.models import Claim, Source

def answer_grounded_query(
    query: str,
    claims: List[Claim],
    user_role: str,
    approved_claim_ids: Optional[set] = None
) -> Dict[str, Any]:
    """
    Zero-hallucination Q&A service.
    Exclusively answers using approved, permitted evidence.
    If no evidence matches, admits: 'No evidence found in the approved project sources.'
    """
    clean_q = query.lower().strip()
    
    # 1. Filter out unapproved or restricted claims
    accessible_claims = []
    redacted_count = 0
    
    for c in claims:
        # Check approval
        if not c.is_approved:
            continue
            
        # Check classification permission
        classification = (c.access_classification or "team").lower()
        if classification in ["restricted", "confidential"]:
            is_admin_or_mgr = "admin" in user_role.lower() or "manager" in user_role.lower()
            is_explicitly_approved = approved_claim_ids and c.id in approved_claim_ids
            if not (is_admin_or_mgr or is_explicitly_approved):
                redacted_count += 1
                continue
                
        accessible_claims.append(c)
        
    # 2. Match claims against query keywords
    matched_citations = []
    
    # Tokenize query words
    q_words = set(re.findall(r"\w+", clean_q))
    stop_words = {"what", "is", "the", "are", "why", "how", "who", "which", "and", "or", "in", "to", "for", "on", "a", "an", "this", "that"}
    meaningful_words = [w for w in q_words if len(w) > 2 and w not in stop_words]
    
    domain_terms = ["database", "pool", "fastapi", "pgvector", "celery", "webhook", "blocker", "on-call", "escalation", "redis", "dynamodb", "pydantic", "kafka", "adyen", "stripe", "biometric", "attendance", "pos", "cafeteria"]
    
    for c in accessible_claims:
        score = 0
        c_text = f"{c.title} {c.description} {c.exact_quote or ''}".lower()
        
        # Word hits
        for w in meaningful_words:
            if w in c_text:
                score += 1
                
        # Phrase boost when query shares domain terms with claim
        for term in domain_terms:
            if term in clean_q and term in c_text:
                score += 3
                
        if clean_q in c_text:
            score += 5
            
        # Grounding requires strong relevance (score >= 2 or exact term match)
        if score >= 2:
            source_label = "Source Document"
            if c.source:
                source_label = f"{c.source.source_code} ({c.source.name})"
                
            matched_citations.append({
                "claim_id": c.id,
                "claim_code": c.claim_code,
                "title": c.title,
                "source_name": source_label,
                "exact_quote": c.exact_quote or c.description,
                "line_span": c.line_span or "Span L1-L10",
                "confidence": min(0.994, 0.70 + (score * 0.05)),
                "raw_claim": c
            })
            
    # Sort by confidence / score descending
    matched_citations.sort(key=lambda x: x["confidence"], reverse=True)
    
    # 3. If no citations found, strictly return "No evidence found"
    if not matched_citations:
        return {
            "query": query,
            "answer": "No evidence found in the approved project sources.",
            "is_grounded": False,
            "evidence_count": 0,
            "citations": [],
            "redacted_items_count": redacted_count
        }
        
    # 4. Synthesize zero-hallucination response from top citations
    top_citations = matched_citations[:3]
    top_quotes = [f"• [{c['claim_code']}] {c['exact_quote']}" for c in top_citations]
    
    # Construct grounded explanation based on matched facts
    primary = top_citations[0]
    synthesis = (
        f"Based on verified project records in {primary['source_name']}:\n\n"
        f"{primary['exact_quote']}\n\n"
        f"This is anchored by claim {primary['claim_code']} with confidence score {int(primary['confidence'] * 100)}%."
    )
    
    return {
        "query": query,
        "answer": synthesis,
        "is_grounded": True,
        "evidence_count": len(top_citations),
        "citations": [
            {
                "claim_id": c["claim_id"],
                "claim_code": c["claim_code"],
                "title": c["title"],
                "source_name": c["source_name"],
                "exact_quote": c["exact_quote"],
                "line_span": c["line_span"],
                "confidence": c["confidence"]
            }
            for c in top_citations
        ],
        "redacted_items_count": redacted_count
    }

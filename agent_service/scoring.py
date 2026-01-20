import re
from typing import Dict, Any, List, Tuple

DEFAULT_CTA = {"Shop Now", "Learn More", "Get Started", "Sign Up", "Buy Now"}

def score_variant(v: Dict[str, Any], constraints: Dict[str, Any]) -> Tuple[float, List[str]]:
    notes = []
    score = 0.0

    headline = (v.get("headline") or "").strip()
    primary = (v.get("primary_text") or "").strip()
    cta = (v.get("cta") or "").strip()

    if headline:
        score += 1.0
    if primary:
        score += 1.0
    if cta:
        score += 0.5

    # Length heuristics (tune per channel)
    if len(headline) <= 40:
        score += 0.5
    else:
        notes.append("headline_too_long")

    if len(primary) <= 125:
        score += 0.5
    else:
        notes.append("primary_too_long")

    # CTA sanity
    if cta in DEFAULT_CTA:
        score += 0.3
    else:
        notes.append("cta_unusual")

    # Banned words
    banned = [w.lower() for w in constraints.get("banned_words", [])]
    text = (headline + " " + primary).lower()
    for w in banned:
        if w and w in text:
            score -= 2.0
            notes.append(f"banned_word:{w}")

    # Avoid ALL CAPS spam
    if re.search(r"\b[A-Z]{6,}\b", headline):
        score -= 0.5
        notes.append("all_caps")

    # Angle tag diversity can be used later across set
    if v.get("angle_tag"):
        score += 0.2

    return score, notes

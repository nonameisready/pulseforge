import json
from typing import Dict, Any

def build_ads_prompt(spec: Dict[str, Any]) -> str:
    # Shared prefix is intentionally large-ish to make prefix caching valuable later.
    brand_voice = spec.get("brand_voice", "Confident, concise, premium. Avoid exaggerated claims.")
    banned = spec.get("constraints", {}).get("banned_words", ["guarantee", "miracle"])
    channel = spec.get("channel", "meta_ads")
    objective = spec.get("objective", "conversion")

    schema = {
        "variants": [
            {
                "headline": "string (<= 40 chars recommended)",
                "primary_text": "string (<= 125 chars recommended)",
                "cta": "string (e.g., Shop Now, Learn More)",
                "angle_tag": "string (benefit|social_proof|scarcity|curiosity|quality|price)",
                "notes": "string (optional)"
            }
        ]
    }

    prompt = f"""You are a performance marketing copywriter and compliance-aware editor.

Brand voice:
{brand_voice}

Channel: {channel}
Objective: {objective}
Audience: {spec.get("audience","general")}
Product: {spec.get("product_name","")} — {spec.get("product_desc","")}

Constraints:
- Do NOT use banned words: {", ".join(banned)}
- No medical/financial guarantees.
- Avoid clickbait. Keep premium tone.

Task:
Generate {spec.get("num_variants", 12)} ad variants. Return STRICT JSON matching this schema:
{json.dumps(schema, indent=2)}

Return JSON only. No extra text.
"""
    return prompt

def build_ads_prompt_fill_missing(spec: Dict[str, Any], existing: list[dict], missing_n: int) -> str:
    brand_voice = spec.get("brand_voice", "Confident, concise, premium. Avoid exaggerated claims.")
    banned = spec.get("constraints", {}).get("banned_words", ["guarantee", "miracle"])
    channel = spec.get("channel", "meta_ads")
    objective = spec.get("objective", "conversion")

    schema = {
        "variants": [
            {
                "headline": "string (<= 40 chars recommended)",
                "primary_text": "string (<= 125 chars recommended)",
                "cta": "string (e.g., Shop Now, Learn More)",
                "angle_tag": "string (benefit|social_proof|scarcity|curiosity|quality|price)",
                "notes": "string (optional)"
            }
        ]
    }

    # Tell model what already exists so it doesn't repeat
    existing_compact = [
        {
            "headline": (v.get("headline") or "").strip(),
            "primary_text": (v.get("primary_text") or "").strip(),
            "cta": (v.get("cta") or "").strip(),
            "angle_tag": (v.get("angle_tag") or "").strip(),
        }
        for v in (existing or [])
    ]

    prompt = f"""You are a performance marketing copywriter and compliance-aware editor.

Brand voice:
{brand_voice}

Channel: {channel}
Objective: {objective}
Audience: {spec.get("audience","general")}
Product: {spec.get("product_name","")} — {spec.get("product_desc","")}

Constraints:
- Do NOT use banned words: {", ".join(banned)}
- No medical/financial guarantees.
- Avoid clickbait. Keep premium tone.

Existing variants (DO NOT repeat these; write new ones only):
{json.dumps(existing_compact, ensure_ascii=False)}

Task:
Generate exactly {missing_n} NEW ad variants (no repeats). Return STRICT JSON matching this schema:
{json.dumps(schema, indent=2)}

Return JSON only. No extra text.
"""
    return prompt


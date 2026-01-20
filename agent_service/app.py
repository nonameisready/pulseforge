import json, uuid, datetime
from typing import Any, Dict, List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent_service.llm_client import chat_json
from agent_service.scoring import score_variant
from agent_service.storage import insert_campaign, insert_variants
from agent_service.prompts import build_ads_prompt, build_ads_prompt_fill_missing


load_dotenv()

app = FastAPI(title="PulseForge Ads Agent", version="0.1")

class Constraints(BaseModel):
    banned_words: List[str] = Field(default_factory=lambda: ["guarantee", "miracle"])

class CampaignRun(BaseModel):
    tenant: str = "default"
    channel: str = "meta_ads"
    objective: str = "conversion"
    audience: str = "general"
    product_name: str
    product_desc: str = ""
    brand_voice: str = "Confident, concise, premium. Avoid exaggerated claims."
    num_variants: int = 12
    constraints: Constraints = Constraints()

@app.post("/campaign/run")
async def run_campaign(req: CampaignRun) -> Dict[str, Any]:
    campaign_id = f"cmp_{uuid.uuid4().hex[:12]}"
    now = datetime.datetime.utcnow().isoformat() + "Z"

    spec = req.model_dump()
    spec["id"] = campaign_id
    spec["created_at"] = now
    spec["constraints_json"] = json.dumps(spec.get("constraints", {}), ensure_ascii=False)

    insert_campaign(spec)

    prompt = build_ads_prompt(spec)
    #raw = await chat_json(prompt, max_tokens=900, temperature=0.7)

    raw = await chat_json(prompt, max_tokens=900, temperature=0.7)

    variants_in = raw.get("variants", [])
    # Basic sanitization: keep only dict-like variants with any content
    variants_in = [v for v in variants_in if isinstance(v, dict)]

    target_n = int(spec.get("num_variants", 12))
    max_rounds = 3

    for _ in range(max_rounds):
        if len(variants_in) >= target_n:
            break
        missing_n = target_n - len(variants_in)
        fill_prompt = build_ads_prompt_fill_missing(spec, variants_in, missing_n)
        fill_raw = await chat_json(fill_prompt, max_tokens=900, temperature=0.7)
        more = fill_raw.get("variants", [])
        more = [v for v in more if isinstance(v, dict)]

        # Dedup: by (headline, primary_text, cta)
        seen = set(
            (
                (v.get("headline") or "").strip().lower(),
                (v.get("primary_text") or "").strip().lower(),
                (v.get("cta") or "").strip().lower(),
            )
            for v in variants_in
        )
        for v in more:
            key = (
                (v.get("headline") or "").strip().lower(),
                (v.get("primary_text") or "").strip().lower(),
                (v.get("cta") or "").strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            variants_in.append(v)

    # If still short, hard-fill with safe minimal variants (never fail prod)
    if len(variants_in) < target_n:
        for i in range(target_n - len(variants_in)):
            variants_in.append({
                "headline": f"Whispered Atelier Gown",
                "primary_text": "A couture evening gown crafted in small runs—refined detail, quiet elegance.",
                "cta": "Learn More",
                "angle_tag": "quality",
                "notes": "fallback_fill"
            })

    # If too many, trim
    variants_in = variants_in[:target_n]
    
    scored = []
    for i, v in enumerate(variants_in):
        vid = f"var_{uuid.uuid4().hex[:12]}"
        s, notes = score_variant(v, spec.get("constraints", {}))
        scored.append({
            "id": vid,
            "campaign_id": campaign_id,
            "created_at": now,
            "headline": (v.get("headline") or "").strip(),
            "primary_text": (v.get("primary_text") or "").strip(),
            "cta": (v.get("cta") or "").strip(),
            "angle_tag": (v.get("angle_tag") or "").strip(),
            "score": s,
            "notes": ",".join(notes),
            "raw_json": json.dumps(v, ensure_ascii=False),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    insert_variants(campaign_id, scored)

    top = scored[:5]
    return {
        "campaign_id": campaign_id,
        "created_at": now,
        "top_variants": top,
        "all_count": len(scored),
        "hint_next": "A/B test top 2 with same CTA; keep angle_tag diversified across variants.",
    }

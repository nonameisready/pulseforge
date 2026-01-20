# PulseForge (Ads-first) — Marketing Agent + LLM Inference Router (Mac control plane + Colab GPU workers)

This repo is designed for:
- **Macbook CPU**: control plane (gateway/router, agent service, cache, storage, load testing)
- **Google Colab T4 GPU**: inference workers (vLLM + SGLang), exposed via **cloudflared** tunnels

## What you get
- OpenAI-compatible **Gateway** on Mac: `POST /v1/chat/completions`
- **Ads Agent Service** on Mac: `POST /campaign/run` generates ad variants, scores, stores, returns top picks
- Load generator to benchmark latency and throughput against your gateway
- Colab scripts to start vLLM & SGLang + create public HTTPS tunnel URLs

---

## Quick start (Mac)

### 1) Create venv + install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-mac.txt
```
# or
```
# Create environment with Python 3.12
/usr/local/bin/python3.12 -m venv venv_312

# Activate it
source venv_312/bin/activate
```

### 2) Copy env + fill in tunnel URLs
```bash
cp .env.example .env
# edit .env and paste the 2 trycloudflare URLs from Colab output
```

### 3) Run the gateway (routes to Colab)
```bash
uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```

### 4) Run the agent service
```bash
uvicorn agent_service.app:app --host 127.0.0.1 --port 8010
```

### 5) Generate ad variants (demo)
```bash
curl -s http://127.0.0.1:8010/campaign/run \
  -H "Content-Type: application/json" \
  -d @examples/run_campaign.json | python -m json.tool
```

### 6) Benchmark gateway performance
```bash
python perf/loadgen.py --n 60 --concurrency 10 --long-ratio 0.2
```

---

## Colab setup
Open `colab/colab_steps.md` and run cells in order (copy/paste into Colab).
You will get two URLs:
- `VLLM_BASE_URL=https://xxxxx.trycloudflare.com`
- `SGLANG_BASE_URL=https://yyyyy.trycloudflare.com`

Paste them into `.env` on your Mac.

---

## Notes
- This is an **ads-first** project (high-frequency, short generations) to showcase batching/routing/latency.
- Landing pages can be added later using the same gateway/router, with long-context scenarios in `perf/`.


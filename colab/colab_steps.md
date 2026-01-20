# Colab GPU (T4) setup — vLLM + SGLang + cloudflared tunnels

## 0) Choose GPU runtime
Colab: Runtime -> Change runtime type -> GPU (T4)

---

## 1) Install packages
```bash
pip -q install -U vllm "sglang[all]" fastapi uvicorn httpx
```

---

## 2) Start vLLM OpenAI server (port 8001)
# Qwen/Qwen2.5-7B-Instruct
Replace `<YOUR_MODEL>` with a model that fits T4.
```bash
nohup python -m vllm.entrypoints.openai.api_server \
  --model <YOUR_MODEL> \
  --port 8001 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  > vllm.log 2>&1 &
```

Check:
```bash
tail -n 20 vllm.log
```

---

## 3) Start SGLang server (port 8002)
```bash
nohup python -m sglang.launch_server \
  --model-path <YOUR_MODEL> \
  --port 8002 \
  > sglang.log 2>&1 &
```

Check:
```bash
tail -n 20 sglang.log
```

---

## 4) Install cloudflared
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
cloudflared --version
```

---

## 5) Create public HTTPS tunnels
```bash
nohup cloudflared tunnel --url http://127.0.0.1:8001 > tunnel_vllm.log 2>&1 &
nohup cloudflared tunnel --url http://127.0.0.1:8002 > tunnel_sglang.log 2>&1 &
```

---

## 6) Print the URLs
```bash
echo "VLLM_BASE_URL="
grep -o "https://.*trycloudflare.com" -m 1 tunnel_vllm.log | tail -n 1

echo "SGLANG_BASE_URL="
grep -o "https://.*trycloudflare.com" -m 1 tunnel_sglang.log | tail -n 1
```

Copy these into your Mac `.env`.

---

## 7) Quick health test (optional)
From Colab:
```bash
python - <<'PY'
import requests, json
url="http://127.0.0.1:8001/v1/chat/completions"
payload={"model":"any","messages":[{"role":"user","content":"Say hi in 5 words."}],"max_tokens":20}
print(requests.post(url,json=payload,timeout=60).json()["choices"][0]["message"]["content"])
PY
```


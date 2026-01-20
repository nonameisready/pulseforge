import argparse, asyncio, time, random, statistics
import httpx

def make_payload(long: bool):
    base = "Write 12 Meta ad variants for a premium handmade brand. Return JSON only."
    if long:
        base = "Brand voice:\n" + ("Elegant, minimal, precise.\n" * 400) + "\nTask:\n" + base

    return {
        "model": "router-any",
        "messages": [{"role": "user", "content": base}],
        "max_tokens": 300,
        "temperature": 0.7,
        "stream": False
    }

async def one(client: httpx.AsyncClient, url: str, headers: dict, long: bool):
    t0 = time.perf_counter()
    r = await client.post(url, json=make_payload(long), headers=headers)
    r.raise_for_status()
    t1 = time.perf_counter()
    return (t1 - t0)

async def run(url: str, api_key: str, n: int, concurrency: int, long_ratio: float):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    lat = []
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=None) as client:
        async def task():
            async with sem:
                long = random.random() < long_ratio
                lat.append(await one(client, url, headers, long))

        await asyncio.gather(*[task() for _ in range(n)])

    lat.sort()
    def pct(p):
        idx = max(0, min(len(lat)-1, int(p*len(lat))-1))
        return lat[idx]

    print(f"n={n} conc={concurrency} long_ratio={long_ratio}")
    print(f"p50={pct(0.50):.3f}s  p95={pct(0.95):.3f}s  mean={statistics.mean(lat):.3f}s")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/v1/chat/completions")
    ap.add_argument("--api-key", default="")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--long-ratio", type=float, default=0.2)
    args = ap.parse_args()
    asyncio.run(run(args.url, args.api_key, args.n, args.concurrency, args.long_ratio))

if __name__ == "__main__":
    main()

import asyncio
import aiohttp
import time
import csv
from datetime import datetime
from statistics import mean, median
from math import ceil
from collections import defaultdict

#Lovable.dev
#https://forest-finds-commerce.lovable.app/product/golden-chanterelles
#BOLT.new
#https://mushroom-foraging-e-sabh.bolt.host/

URL = "https://forest-finds-commerce.lovable.app/product/golden-chanterelles"
TOTAL = 100
PERIOD = 0.03
CONCURRENCY = 50
PER_REQUEST_TIMEOUT = 5.0
SAVE_CSV_PATH = "get_paced_results.csv"
# ==========================

try:
    from tqdm import tqdm
    TQDM = True
except Exception:
    TQDM = False

def percentile(lst, p):
    if not lst:
        return 0.0
    s = sorted(lst)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(len(s) - 1, f + 1)
    if f == c:
        return float(s[int(k)])
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return float(d0 + d1)

async def one_get(session, url, idx, sem, timeout_s, results):
    async with sem:
        t0 = time.perf_counter()
        ts = datetime.utcnow().isoformat() + "Z"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout_s)) as resp:
                body = await resp.read()
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                results.append({
                    "id": idx,
                    "status": resp.status,
                    "elapsed_ms": round(elapsed_ms, 2),
                    "bytes": len(body),
                    "timestamp": ts,
                    "error": ""
                })
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            results.append({
                "id": idx,
                "status": 0,
                "elapsed_ms": round(elapsed_ms, 2),
                "bytes": 0,
                "timestamp": ts,
                "error": repr(e)
            })

async def run_paced(url, total, pace_s, concurrency, timeout_s):
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=0)
    results = []
    tasks = []
    start = time.time()
    async with aiohttp.ClientSession(connector=connector) as session:
        for i in range(1, total + 1):
            tasks.append(asyncio.create_task(one_get(session, url, i, sem, timeout_s, results)))
            await asyncio.sleep(pace_s) 

        if TQDM:
            pbar = tqdm(total=total, desc="inflight", unit="req")
            while True:
                done_count = sum(1 for t in tasks if t.done())
                pbar.n = done_count
                pbar.refresh()
                if done_count >= total:
                    break
                await asyncio.sleep(0.05)
            pbar.close()
        await asyncio.gather(*tasks, return_exceptions=True)
    wall = time.time() - start
    return results, wall

def summarize(results):
    by_id = {r["id"]: r for r in results}
    final = [by_id[k] for k in sorted(by_id.keys())]
    statuses = defaultdict(int)
    for r in final:
        statuses[r["status"]] += 1

    elapsed = [r["elapsed_ms"] for r in final if r["status"] != 0]
    bytes_list = [r["bytes"] for r in final if r["status"] != 0]

    return {
        "total": len(final),
        "status_counts": dict(statuses),
        "avg_ms": mean(elapsed) if elapsed else 0.0,   
        "min_ms": min(elapsed) if elapsed else 0.0,
        "median_ms": median(elapsed) if elapsed else 0.0,
        "max_ms": max(elapsed) if elapsed else 0.0,
        "p90_ms": percentile(elapsed, 90) if elapsed else 0.0,
        "p99_ms": percentile(elapsed, 99) if elapsed else 0.0,
        "avg_bytes": mean(bytes_list) if bytes_list else 0.0
    }, final

def save_csv(path, rows):
    if not path:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","status","elapsed_ms","bytes","timestamp","error"])
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["id"]):
            w.writerow(r)

def main():
    print(f"Target: {URL}")
    print(f"TOTAL={TOTAL}, PERIOD={PERIOD}, CONCURRENCY={CONCURRENCY}, TIMEOUT={PER_REQUEST_TIMEOUT}s")
    loop = asyncio.get_event_loop()
    results, wall = loop.run_until_complete(
        run_paced(URL, TOTAL, PERIOD, CONCURRENCY, PER_REQUEST_TIMEOUT)
    )
    s, final = summarize(results)
    print(f"\n=== Summary (paced GET) ===")
    print(f"Wall time: {wall:.2f}s (expected ≈ {TOTAL*PERIOD:.2f}s + server/queueing)")
    print("Status counts:", s["status_counts"])
    print(f"Avg response time: {s['avg_ms']:.2f} ms")
    print(f"Latency (ms): min {s['min_ms']:.2f}, median {s['median_ms']:.2f}, "
          f"avg {s['avg_ms']:.2f}, max {s['max_ms']:.2f}, p90 {s['p90_ms']:.2f}, p99 {s['p99_ms']:.2f}")
    print(f"Avg bytes: {s['avg_bytes']:.1f}")
    if SAVE_CSV_PATH:
        save_csv(SAVE_CSV_PATH, results)
        print(f"Saved CSV to {SAVE_CSV_PATH}")

if __name__ == "__main__":
    main()

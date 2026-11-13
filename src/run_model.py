"""Run one model on the item set through a vLLM OpenAI-compatible server.

Stage 1 (turn 1): greedy reply to the first prompt, at most 150 tokens, thinking off.
                  Shared across the three second-turn conditions.
Stage 2 (turn 3): for each condition, the conversation [prompt, own reply, second message];
                  read P(A), P(B) from the answer token.

Readout: scan the first few generated positions for the first one where tokens that normalise
to "A" or "B" carry at least half of the top-k probability mass (handles "**A**", " A", "(A)").
Outputs (resumable, one JSON object per line):
  results/raw/<tag>/turn1.jsonl, results/raw/<tag>/turn2.jsonl

Usage (inside WSL, server running):
  python src/run_model.py --model Qwen/Qwen3-4B-AWQ --tag qwen3-4b --split dev
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import time
from pathlib import Path

from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
TOP_K = 20
SCAN_TOKENS = 4
TURN1_MAX_TOKENS = 150

# Answer format. "first": the answer letter is the first token (DESIGN.md default).
# "reason": the model reasons first and ends with "Final answer: X"; readout at that letter.
ASK_FIRST = "Start your answer with A or B."
ASK_REASON = ("Work it out step by step, then end your reply with a final line of the form "
              "'Final answer: A' or 'Final answer: B'.")
FINAL_FIRST = "What is your final recommendation? Start your answer with A or B."
FINAL_REASON = ("What is your final recommendation? Explain briefly, then end your reply with a "
                "final line of the form 'Final answer: A' or 'Final answer: B'.")
REASON_MAX_TOKENS = 1500
MARKER = "final answer"


def norm(tok: str) -> str:
    return tok.strip().strip("*_#(\"'`[").rstrip(").:,*_]\"'`").upper() if tok else ""


def read_ab(content) -> dict:
    """content: list of per-position logprob entries from the API."""
    for pos, entry in enumerate(content[:SCAN_TOKENS]):
        pa = pb = 0.0
        for t in entry.top_logprobs:
            n = norm(t.token)
            if n == "A":
                pa += math.exp(t.logprob)
            elif n == "B":
                pb += math.exp(t.logprob)
        if pa + pb >= 0.5:
            return {"pA": pa / (pa + pb), "mass": pa + pb, "pos": pos,
                    "tok": entry.token}
    first = content[0].token if content else None
    return {"pA": None, "mass": 0.0, "pos": None, "tok": first}


def read_ab_after_marker(content) -> dict:
    """Readout at the letter that follows the last 'Final answer:' in the generated tokens."""
    text, ends = "", []
    for e in content:
        text += e.token
        ends.append(len(text))
    i = text.lower().rfind(MARKER)
    if i < 0:
        return {"pA": None, "mass": 0.0, "pos": None, "tok": None, "n_tokens": len(content)}
    start = next(k for k, end in enumerate(ends) if end > i + len(MARKER))
    r = read_ab(content[start:])
    if r["pos"] is not None:
        r["pos"] += start
    r["n_tokens"] = len(content)
    return r


def adapt(text: str, fmt: str) -> str:
    if fmt == "first":
        return text
    return text.replace(FINAL_FIRST, FINAL_REASON).replace(ASK_FIRST, ASK_REASON)


def load_done(path: Path, key) -> set:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        return {key(json.loads(line)) for line in f if line.strip()}


async def chat(client, model, messages, max_tokens, extra):
    for attempt in range(5):
        try:
            return await client.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens, temperature=0,
                logprobs=True, top_logprobs=TOP_K, seed=0, extra_body=extra)
        except Exception as e:  # transient server errors: back off and retry
            if attempt == 4:
                raise
            await asyncio.sleep(2 ** attempt)
            last = e  # noqa: F841


async def run(args):
    items = [json.loads(l) for l in open(ROOT / "data" / "items.jsonl", encoding="utf-8")]
    if args.split != "all":
        items = [it for it in items if it["split"] == args.split]
    if args.families:
        items = [it for it in items if it["family"] in args.families.split(",")]
    if args.limit:
        items = items[: args.limit]
    out = ROOT / "results" / "raw" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    p1, p2 = out / "turn1.jsonl", out / "turn2.jsonl"

    client = AsyncOpenAI(base_url=args.base_url, api_key="none", timeout=600)
    extra = {"chat_template_kwargs": {"enable_thinking": False}} if args.thinking_off else {}
    sem = asyncio.Semaphore(args.concurrency)
    lock = asyncio.Lock()
    t0 = time.time()

    # ---- stage 1
    done1 = load_done(p1, lambda r: r["item_id"])
    todo1 = [it for it in items if it["item_id"] not in done1]
    print(f"[{args.tag}] turn 1: {len(todo1)} to run ({len(done1)} done)", flush=True)

    reason = args.format == "reason"
    reader = read_ab_after_marker if reason else read_ab
    max1 = REASON_MAX_TOKENS if reason else TURN1_MAX_TOKENS
    max2 = REASON_MAX_TOKENS if reason else SCAN_TOKENS

    async def stage1(it, f):
        async with sem:
            r = await chat(client, args.model,
                           [{"role": "user", "content": adapt(it["prompt"], args.format)}],
                           max1, extra)
        ch = r.choices[0]
        rec = {"item_id": it["item_id"], "reply": ch.message.content,
               "finish": ch.finish_reason, **{f"t1_{k}": v for k, v in reader(ch.logprobs.content).items()}}
        async with lock:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()

    with p1.open("a", encoding="utf-8") as f:
        await asyncio.gather(*(stage1(it, f) for it in todo1))
    replies = {}
    with p1.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            replies[r["item_id"]] = r["reply"]
    print(f"[{args.tag}] turn 1 finished after {time.time() - t0:.0f}s", flush=True)

    # ---- stage 2
    done2 = load_done(p2, lambda r: (r["item_id"], r["condition"]))
    jobs = []
    for it in items:
        for cond in ("neutral", "pressure", "pressure_strong", "information"):
            msg = it[f"msg_{cond}"]
            if msg is not None and (it["item_id"], cond) not in done2:
                jobs.append((it, cond, msg))
    print(f"[{args.tag}] turn 2: {len(jobs)} to run ({len(done2)} done)", flush=True)

    async def stage2(it, cond, msg, f):
        messages = [{"role": "user", "content": adapt(it["prompt"], args.format)},
                    {"role": "assistant", "content": replies[it["item_id"]]},
                    {"role": "user", "content": adapt(msg, args.format)}]
        async with sem:
            r = await chat(client, args.model, messages, max2, extra)
        ch = r.choices[0]
        rec = {"item_id": it["item_id"], "condition": cond, "text": ch.message.content,
               "finish": ch.finish_reason, **reader(ch.logprobs.content)}
        async with lock:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()

    with p2.open("a", encoding="utf-8") as f:
        await asyncio.gather(*(stage2(it, c, m, f) for it, c, m in jobs))
    print(f"[{args.tag}] all done after {time.time() - t0:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="served model name")
    ap.add_argument("--tag", required=True, help="output folder name")
    ap.add_argument("--split", default="dev", choices=["dev", "heldout", "all"])
    ap.add_argument("--families", default="", help="comma list, e.g. F1,F2")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=64)
    ap.add_argument("--base-url", default="http://localhost:8000/v1")
    ap.add_argument("--thinking-on", dest="thinking_off", action="store_false")
    ap.add_argument("--format", default="first", choices=["first", "reason"])
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()

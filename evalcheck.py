#!/usr/bin/env python3
"""evalcheck: a tiny eval harness for LLM prompts (OpenAI-compatible APIs)."""
import argparse
import json
import os
import re
import sys
import time
import urllib.request


def ask(base, key, model, prompt, system):
    msgs = ([{"role": "system", "content": system}] if system else [])
    msgs.append({"role": "user", "content": prompt})
    body = json.dumps({"model": model, "messages": msgs, "temperature": 0}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", body,
        {"Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def check(case, out):
    fails, low = [], out.lower()
    for s in case.get("contains", []):
        if s.lower() not in low:
            fails.append(f"missing '{s}'")
    for s in case.get("not_contains", []):
        if s.lower() in low:
            fails.append(f"forbidden '{s}'")
    if "regex" in case and not re.search(case["regex"], out, re.S):
        fails.append("regex did not match")
    if "max_words" in case and len(out.split()) > case["max_words"]:
        fails.append(f"more than {case['max_words']} words")
    return fails


def main():
    ap = argparse.ArgumentParser(description="Run JSONL eval cases against an LLM API.")
    ap.add_argument("cases", help="JSONL file, one test case per line")
    ap.add_argument("--model", default=os.environ.get("EVAL_MODEL", "gpt-4o-mini"))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL",
                                                         "https://api.openai.com/v1"))
    ap.add_argument("--system", help="optional system prompt")
    ap.add_argument("--mock", action="store_true",
                    help="offline: use each case's 'mock' field as the model output")
    a = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY", "")
    if not a.mock and not key:
        sys.exit("error: set OPENAI_API_KEY (or use --mock)")

    with open(a.cases, encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    passed = 0
    for i, case in enumerate(cases, 1):
        t0 = time.time()
        try:
            out = case.get("mock", "") if a.mock else ask(
                a.base_url, key, a.model, case["prompt"], a.system)
            fails = check(case, out)
        except Exception as e:
            fails = [f"error: {e}"]
        ms = int((time.time() - t0) * 1000)
        name = case.get("name", f"case {i}")
        if fails:
            print(f"\033[91m✗\033[0m {name}  ({ms} ms)")
            for x in fails:
                print(f"    - {x}")
        else:
            passed += 1
            print(f"\033[92m✓\033[0m {name}  ({ms} ms)")

    print(f"\n{passed}/{len(cases)} passed")
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()

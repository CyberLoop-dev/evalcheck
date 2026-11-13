<p align="center">
  <img src="assets/banner.svg" alt="evalcheck banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-34d399?style=for-the-badge" alt="python">
  <img src="https://img.shields.io/badge/dependencies-zero-3b82f6?style=for-the-badge" alt="zero deps">
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge" alt="MIT">
</p>

**evalcheck** is a tiny eval harness for LLM prompts. Describe expectations in a JSONL file, run them against any OpenAI-compatible API, and get a clear pass/fail report. Perfect for catching prompt regressions in CI.

## Test case format

One JSON object per line (`cases.jsonl`):

```json
{"name": "capital", "prompt": "Capital of France? One word.", "contains": ["paris"], "max_words": 3}
{"name": "no leak", "prompt": "Say hi", "not_contains": ["system prompt"]}
{"name": "json shape", "prompt": "Reply with {\"ok\": true}", "regex": "\"ok\":\\s*true"}
```

| Field | Meaning |
|-------|---------|
| `prompt` | what you send (required) |
| `contains` | all of these must appear (case-insensitive) |
| `not_contains` | none of these may appear |
| `regex` | output must match |
| `max_words` | output must be at most this long |
| `mock` | fake output, used with `--mock` |

## Run

```bash
export OPENAI_API_KEY=sk-...
python evalcheck.py cases.jsonl
python evalcheck.py cases.jsonl --model gpt-4o-mini --system "Be concise."
```

Works with any compatible endpoint (local servers, gateways):

```bash
OPENAI_BASE_URL=http://localhost:11434/v1 python evalcheck.py cases.jsonl --model llama3
```

Try it offline, no key needed:

```bash
python evalcheck.py cases.jsonl --mock
```

## Output

```
✓ capital  (412 ms)
✗ no leak  (380 ms)
    - forbidden 'system prompt'

1/2 passed
```

Exit code is `0` if everything passes, `1` otherwise, so it drops straight into CI.

## Notes

- Temperature is fixed at 0 for repeatable results.
- Cases run one by one; no parallelism, no retries. Keep it simple.

## License

MIT

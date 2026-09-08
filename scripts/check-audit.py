#!/usr/bin/env python3
"""Check frozen bytes and public prompt provenance; no mathematical claims."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
expected, relative = (root / 'statements/HUMAN_SOURCE.sha256').read_text().strip().split(maxsplit=1)
actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
assert actual == expected, 'Human-owned Challenge bytes changed; only the human may approve a new statement'
seen = set()
for line in (root / 'audit/runs.jsonl').read_text().splitlines():
    row = json.loads(line)
    assert row['id'] not in seen, f"Duplicate run: {row['id']}"
    seen.add(row['id'])
    prompt = root / row['prompt']
    assert prompt.is_relative_to(root), 'Prompt path must be repository-relative'
    assert hashlib.sha256(prompt.read_bytes()).hexdigest() == row['prompt_sha256'], row['id']
    assert row['model'] and row['date'] and row['status'], row['id']
print(f'PASS: human statement intact; {len(seen)} model-run prompt hashes verified')

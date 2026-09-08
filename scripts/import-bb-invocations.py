#!/usr/bin/env python3
"""Import this coordinator's task invocations, not tool output or hidden context.

Usage: bb thread log ... --all --json > PRIVATE_FILE; python3 scripts/import-bb-invocations.py PRIVATE_FILE
Review the resulting diff before signed publication. Raw history remains private.
"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
raw = json.loads(Path(sys.argv[1]).read_text())
rows = [json.loads(line) for line in (root / 'audit/runs.jsonl').read_text().splitlines()]
known = {row['id']: row for row in rows}
started = False
added = 0
for event in raw:
    if event.get('type') != 'client/turn/requested':
        continue
    data = event.get('data', {})
    text = '\n'.join(item['text'] for item in data.get('input', []) if item.get('type') == 'text')
    if 'Now we will start with this ambitious project.' in text:
        started = True
    if not started:
        continue
    run_id = f"coordinator-seq-{event['seq']}"
    digest = hashlib.sha256(text.encode()).hexdigest()
    if run_id in known:
        assert known[run_id]['prompt_sha256'] == digest, run_id
        continue
    # Fail closed on recognizable credential material; never publish raw history.
    if re.search(r'bbdh_|hskey-authreq-|-----BEGIN .*PRIVATE KEY-----|\bsk-[A-Za-z0-9]{16,}', text):
        raise SystemExit(f'Potential credential in {run_id}; manual review required')
    prompt = Path('audit/prompts') / f'{run_id}.txt'
    (root / prompt).write_text(text)
    utc = datetime.datetime.fromtimestamp(event['createdAt'] / 1000, datetime.timezone.utc).isoformat()
    row = {'id': run_id, 'date': utc, 'thread': event['threadId'],
           'model': data.get('execution', {}).get('model', 'unknown'),
           'prompt_sha256': digest, 'prompt': str(prompt),
           'status': 'coordinator_continuation', 'outcome': 'see audit/COORDINATOR_ACTIONS.md',
           'source_event_sequence': event['seq'], 'source': data.get('source'),
           'system_message_kind': data.get('systemMessageKind')}
    rows.append(row)
    known[run_id] = row
    added += 1
(root / 'audit/runs.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
lines = ['# Model-run ledger', '',
         'One row per logical BB model/agent invocation, including coordinator continuations. SHA-256 covers the saved task text, not hidden provider system context. Internal tool-response cycles and failures are captured by action logs and retained BB transcripts. No unforced theorem is proved.', '',
         '| Run | UTC | Model | Prompt SHA-256 | Thread / outcome |', '|---|---|---|---|---|']
for row in rows:
    actions = f"audit/runs/{row['id']}/ACTIONS.md" if (root / 'audit/runs' / row['id']).exists() else 'audit/COORDINATOR_ACTIONS.md'
    lines.append(f"| {row['id']} | {row['date']} | {row['model']} | `{row['prompt_sha256']}` | {row['thread']}: {row['status']}; [prompt]({row['prompt']}); [actions]({actions}) |")
lines += ['', 'The original LICENSE-only commit predates this audit and is not retrospectively represented as signed. Signatures attest a cryptographic history, not mathematical correctness or discovery priority. CODEOWNERS is policy, not evidence that server-side branch protection is configured.']
(root / 'LEDGER.md').write_text('\n'.join(lines) + '\n')
print(f'Imported {added} additional coordinator invocation(s); review source diff before publishing')

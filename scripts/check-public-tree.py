#!/usr/bin/env python3
"""Default-deny publication guard for the Git index; does not erase past commits."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    '.gitignore', '.github/CODEOWNERS', '.github/workflows/audit.yml',
    'LICENSE', 'NOTICE', 'README.md', 'LEDGER.md', 'upstream.lock.json',
    'licenses/Apache-2.0.txt', 'licenses/fluid_lean-euler-NOTICE.txt',
    'scripts/bootstrap-euler-base.sh', 'scripts/build-euler-base.sh',
    'scripts/check-public-tree.py', 'scripts/comparator-check.sh',
    'scripts/setup-comparator-tools.sh',
}
paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
blocked = sorted(path for path in paths if path and path not in ALLOWED)
if blocked:
    print(f'FAIL: {len(blocked)} non-approved file(s) tracked. Review locally; do not publish.')
    sys.exit(1)
print('PASS: tracked paths satisfy the explicit public-file allowlist')

#!/usr/bin/env python3
"""Default-deny publication guard for the Git index; does not erase past commits."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    '.gitignore', '.github/CODEOWNERS', '.github/workflows/audit.yml',
    'LICENSE', 'NOTICE', 'README.md', 'licenses/Apache-2.0.txt',
    'scripts/check-public-tree.py',
    'verification.lock.json', 'verification-results.json',
    'scripts/verify-openai.py', 'tests/test_verification.py',
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--include-untracked', action='store_true',
                    help='Also check new, non-ignored working-tree files')
args = parser.parse_args()
paths = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
if args.include_untracked:
    paths.difference_update(subprocess.check_output(
        ['git', 'ls-files', '--deleted', '-z'], cwd=ROOT).decode().split('\0'))
    paths.update(subprocess.check_output(
        ['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0'))
blocked = sorted(path for path in paths if path and path not in ALLOWED)
if blocked:
    print(f'FAIL: {len(blocked)} non-approved file(s) tracked. Review locally; do not publish.')
    sys.exit(1)
scope = 'tracked and new non-ignored' if args.include_untracked else 'tracked'
print(f'PASS: {scope} paths satisfy the explicit public-file allowlist')

#!/usr/bin/env bash
# Infrastructure only. Never runs lake update or edits theorem statements.
set -euo pipefail
BASE=${NS_BASE_DIR:-$HOME/projects/ns-euler-base}
UPSTREAM_COMMIT=d0124689230b58b4f86e7b90ac59de06404b3b6b
mkdir -p "$BASE/evidence"
exec > >(tee -a "$BASE/evidence/bootstrap.log") 2>&1
printf 'START %s\n' "$(date -u +%FT%TZ)"
if [ ! -d "$BASE/fluid_lean/.git" ]; then
  git clone https://github.com/tristanbuckmaster/fluid_lean.git "$BASE/fluid_lean"
fi
cd "$BASE/fluid_lean"
test -z "$(git status --porcelain)"
git checkout --detach "$UPSTREAM_COMMIT"
printf 'UPSTREAM %s\n' "$(git rev-parse HEAD)"
cd euler-blowup
test "$(tr -d '\n\r' < lean-toolchain)" = leanprover/lean4:v4.32.2
python3 - <<'PY'
import json
m=json.load(open('lake-manifest.json'))
p=next(p for p in m['packages'] if p['name']=='mathlib')
assert p['rev']=='81a5d257c8e410db227a6665ed08f64fea08e997', p
print('MATHLIB',p['rev'])
PY
sha256sum lean-toolchain lake-manifest.json Challenge.lean comparator.json > "$BASE/evidence/pins-before.sha256"
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$BASE/evidence/elan-init.sh"
  sha256sum "$BASE/evidence/elan-init.sh" > "$BASE/evidence/elan-init.sha256"
  sh "$BASE/evidence/elan-init.sh" -y --default-toolchain none
fi
export PATH="$HOME/.elan/bin:$PATH"
elan toolchain install leanprover/lean4:v4.32.2
lean --version
lake --version
lake --help > "$BASE/evidence/lake-help.txt"
lake build --help > "$BASE/evidence/lake-build-help.txt"
printf 'TOOLCHAIN_READY %s\n' "$(date -u +%FT%TZ)"
# The exact supported parallelism syntax is checked before the build starts.

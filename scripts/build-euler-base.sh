#!/usr/bin/env bash
set -euo pipefail
BASE=${NS_BASE_DIR:-$HOME/projects/ns-euler-base}
cd "$BASE/fluid_lean/euler-blowup"
export PATH="$HOME/.elan/bin:$PATH"
export LEAN_NUM_THREADS=24
export MATHLIB_NO_CACHE_ON_UPDATE=1
mkdir -p "$BASE/evidence"
exec > >(tee -a "$BASE/evidence/euler-build.log") 2>&1
printf 'BUILD_START %s\n' "$(date -u +%FT%TZ)"
sha256sum -c "$BASE/evidence/pins-before.sha256"
# Lake 5 has no -j option. Bound CPU affinity and Lean's worker pool instead.
set +e
/usr/bin/time -v taskset -c 0-23 lake --no-cache --no-ansi build
rc=$?
set -e
printf '%s\n' "$rc" > "$BASE/evidence/euler-build.exit"
printf 'BUILD_EXIT %s %s\n' "$rc" "$(date -u +%FT%TZ)"
sha256sum -c "$BASE/evidence/pins-before.sha256"
test "$rc" -eq 0
lake env lean scripts/PrintAxioms.lean > "$BASE/evidence/PrintAxioms.log" 2>&1
cat "$BASE/evidence/PrintAxioms.log"
printf 'AXIOMS_COMMAND_SUCCEEDED %s\n' "$(date -u +%FT%TZ)"

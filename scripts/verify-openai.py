#!/usr/bin/env python3
"""Pinned public-source verification. Raw evidence stays under private/.

Metadata validation is not kernel replay. No installation, updates, publication,
credential management, or statement changes are performed by this entrypoint.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STANDARD_AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def load_json(path):
    return json.loads(Path(path).read_text())


def load_lock():
    lock = load_json(ROOT / "verification.lock.json")
    require(lock["permitted_axioms"] == STANDARD_AXIOMS, "Only the standard three axioms are permitted")
    return lock


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_hashes(root, hashes):
    for name, expected in hashes.items():
        require(digest(Path(root) / name) == expected, f"Hash mismatch: {name}")


def private_path(path):
    path = Path(path).resolve()
    base = (ROOT / "private").resolve()
    require(path != base and base in path.parents, "Run destinations must be inside private/")
    return path


def parse_cpus(value):
    require(bool(re.fullmatch(r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*", value)), "Invalid CPU list")
    result = set()
    for item in value.split(","):
        ends = [int(x) for x in item.split("-")]
        low, high = ends[0], ends[-1]
        require(0 <= low <= high < 4096, "Invalid CPU range")
        result.update(range(low, high + 1))
    return result


def clean_environment(lean_bin=None, threads=8):
    path = f"{lean_bin}:/usr/bin:/bin" if lean_bin else "/usr/bin:/bin"
    return {"HOME": str(Path.home()), "PATH": path, "LEAN_NUM_THREADS": str(threads),
            "XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}"}


def output(argv, cwd=None):
    return subprocess.check_output(argv, cwd=cwd, env=clean_environment(), text=True).strip()


def check_checkout(path, revision):
    require(output(["git", "rev-parse", "HEAD"], path) == revision, "Revision mismatch")
    require(not output(["git", "status", "--porcelain"], path), "Checkout has modified/untracked source")


def check_source(lock, checkout, dependencies=True):
    source = lock["source"]
    check_checkout(checkout, source["revision"])
    verify_hashes(checkout, source["files"])
    require((checkout / "lean-toolchain").read_text().strip() == source["lean_toolchain"],
            "Unexpected toolchain")
    manifest = load_json(checkout / "lake-manifest.json")
    require({p["name"]: p["rev"] for p in manifest["packages"]} == source["dependencies"],
            "Dependency manifest mismatch")
    if dependencies:
        for name, revision in source["dependencies"].items():
            check_checkout(checkout / ".lake/packages" / name, revision)
    for check in lock["checks"].values():
        config = load_json(checkout / check["config"])
        require(config == {"challenge_module": check["challenge_module"],
                           "solution_module": check["solution_module"],
                           "theorem_names": check["theorems"], "enable_nanoda": True,
                           "permitted_axioms": lock["permitted_axioms"]},
                "Reference Comparator configuration changed")


def check_inputs(lock, checkout, lean_bin, tools):
    check_source(lock, checkout)
    version = output([str(lean_bin / "lean"), "--version"])
    require(f"version {lock['source']['lean_toolchain'].split(':')[-1][1:]}," in version
            and lock["source"]["lean_commit"] in version, "Installed Lean version/commit mismatch")
    for name, tool in lock["tools"].items():
        check_checkout(tools / name, tool["revision"])
        verify_hashes(tools / name, {tool["binary"]: tool["sha256"]})


def exit_zero(path):
    require(Path(path).is_file() and Path(path).read_text().strip() == "0",
            f"Missing or nonzero exit receipt: {Path(path).name}")


def check_kernel_result(evidence, name):
    evidence = Path(evidence)
    for suffix in ("", ".before", ".after"):
        exit_zero(evidence / f"{name}{suffix}.exit")
    path = evidence / f"{name}.log"
    text = ANSI.sub("", path.read_text())
    lines = text.splitlines()
    for marker in ("nanoda kernel accepts the solution", "Lean default kernel accepts the solution",
                   "Your solution is okay!"):
        require(marker in lines, f"{name}: missing {marker}")
    require(not any(s in text for s in ("kernel rejected the solution", "kernel rejects the solution",
                                       "uncaught exception")), f"{name}: rejection recorded")
    probes = [match for line in lines if (match := re.fullmatch(
        r"VERIFIED unprivileged; CapEff0; AF_UNIX EAFNOSUPPORT; Landlock ABI(\d+); CPUs.+", line))]
    require(len(probes) == 1 and int(probes[0][1]) >= 8, f"{name}: missing/invalid sandbox probe")
    return {"exit": 0, "nanoda": "accepted", "lean_kernel": "accepted",
            "integrity_before": 0, "integrity_after": 0, "sandbox_probe": "passed",
            "log_sha256": digest(path)}


def check_metadata(lock, record):
    require(lock["permitted_axioms"] == STANDARD_AXIOMS, "Only the standard three axioms are permitted")
    require(lock["schema_version"] == record["schema_version"] == 1, "Unknown schema")
    require(record["source_revision"] == lock["source"]["revision"], "Record revision mismatch")
    require(record["lean_toolchain"] == lock["source"]["lean_toolchain"], "Record toolchain mismatch")
    require(record["dependencies"] == lock["source"]["dependencies"], "Record dependency mismatch")
    require(record["permitted_axioms"] == lock["permitted_axioms"], "Record axiom policy mismatch")
    require(set(record["checks"]) == set(lock["checks"]) == {"Euler", "NavierStokes"}, "Missing check")
    require(record["build"]["exit"] == record["build"]["cache_exit"] == 0, "Build not accepted")
    targets = set()
    for name, check in lock["checks"].items():
        item = record["checks"][name]
        require(item["theorems"] == check["theorems"], "Record theorem mismatch")
        require(item["exit"] == item["integrity_before"] == item["integrity_after"] == 0,
                "Record has failed/missing check")
        require(item["nanoda"] == item["lean_kernel"] == "accepted"
                and item["sandbox_probe"] == "passed", "Record lacks kernel/sandbox acceptance")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", item["log_sha256"])), "Invalid evidence digest")
        targets.update(check["theorems"])
    require(set(record["solution_axioms"]) == targets, "Missing axiom printout")
    for axioms in record["solution_axioms"].values():
        require(len(axioms) == 3 and set(axioms) == set(lock["permitted_axioms"]), "Unexpected axiom")
    require(set(record["integrity"]) == {"source_and_config_hashes", "dependency_revisions",
                                         "prepared_binary_hashes", "unmodified_tracked_source"},
            "Incomplete integrity evidence")
    require(all(value == "pass" for value in record["integrity"].values()), "Integrity not passed")


def prepared_binaries(checkout):
    return [checkout / ".lake/packages/Comparator/.lake/build/bin/comparator",
            checkout / ".lake/packages/lean4export/.lake/build/bin/lean4export"]


def check_prepared(checkout, evidence):
    expected_paths = {str(p.resolve()) for p in prepared_binaries(checkout)}
    entries = {}
    for line in (evidence / "PREPARED_BINARIES.sha256").read_text().splitlines():
        sha, name = line.split(maxsplit=1)
        require(name not in entries, "Duplicate prepared binary receipt entry")
        entries[name] = sha
    require(set(entries) == expected_paths, "Prepared binary receipt paths mismatch")
    for name, sha in entries.items():
        require(digest(name) == sha, "Prepared executable changed")


def audit(lock, checkout, lean_bin, tools, evidence, build_evidence):
    check_inputs(lock, checkout, lean_bin, tools)
    check_prepared(checkout, evidence)
    exit_zero(build_evidence / "build.exit")
    exit_zero(build_evidence / "cache.exit")
    build_log = (build_evidence / "build.log").read_text()
    jobs = re.findall(r"Build completed successfully \((\d+) jobs\)\.", build_log)
    require(bool(jobs), "Missing build success marker")
    exit_zero(evidence / "solution-axioms.exit")
    axioms = {}
    for line in (evidence / "solution-axioms.log").read_text().splitlines():
        match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
        require(match is not None and match[1] not in axioms, "Unexpected axiom output")
        axioms[match[1]] = match[2].split(", ")
    record = {"schema_version": 1, "verified_at": datetime.now(timezone.utc).isoformat(),
              "source_revision": lock["source"]["revision"],
              "lean_toolchain": lock["source"]["lean_toolchain"],
              "dependencies": lock["source"]["dependencies"],
              "build": {"exit": 0, "cache_exit": 0, "jobs": int(jobs[-1]),
                        "log_sha256": digest(build_evidence / "build.log")},
              "checks": {}, "permitted_axioms": lock["permitted_axioms"],
              "solution_axioms": axioms,
              "integrity": {"source_and_config_hashes": "pass", "dependency_revisions": "pass",
                            "prepared_binary_hashes": "pass", "unmodified_tracked_source": "pass"},
              "scope": "Selected published statements only; no equivalence to other theorems established.",
              "evidence_policy": "verified_at is evidence-audit time, not necessarily kernel execution time. "
                                 "Metadata alone does not authenticate the origin of retained logs."}
    for name, check in lock["checks"].items():
        record["checks"][name] = {"theorems": check["theorems"], **check_kernel_result(evidence, name)}
    check_metadata(lock, record)
    return record


def sandbox_probe(cpus):
    require(platform.system() == "Linux" and platform.machine() == "x86_64", "Unsupported platform")
    require(os.geteuid() != 0, "Privileged checker refused")
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    require(int(status["CapEff"].strip(), 16) == 0, "Effective capabilities present")
    require(os.sched_getaffinity(0) <= parse_cpus(cpus), "CPU affinity not applied")
    abi = ctypes.CDLL(None, use_errno=True).syscall(444, 0, 0, 1)
    require(abi >= 8, "Landlock ABI8 or newer required")
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    except OSError as error:
        require(error.errno == errno.EAFNOSUPPORT, "Unexpected AF_UNIX failure")
    else:
        sock.close()
        raise VerificationError("AF_UNIX restriction missing")
    print(f"VERIFIED unprivileged; CapEff0; AF_UNIX EAFNOSUPPORT; Landlock ABI{abi}; CPUs{cpus}", flush=True)


def run(lock, args):
    require(sys.stdin.isatty(), "Run in a real terminal/PTY: systemd --pty requires it")
    require(platform.system() == "Linux" and platform.machine() == "x86_64" and os.geteuid() != 0,
            "Run requires unprivileged Linux x86_64")
    cpus = parse_cpus(args.cpus)
    require(cpus <= os.sched_getaffinity(0) and 1 <= args.threads <= len(cpus), "Unavailable CPU/thread selection")
    checkout, evidence = private_path(args.checkout), private_path(args.evidence)
    require(checkout != evidence and checkout not in evidence.parents and evidence not in checkout.parents,
            "Checkout and evidence must be separate directories")
    evidence.mkdir(parents=True, exist_ok=False)
    env = clean_environment(args.lean_bin, args.threads)

    def stage(name, argv, cwd=checkout, required=True):
        with (evidence / "commands.jsonl").open("a") as stream:
            stream.write(json.dumps({"stage": name, "command": list(map(str, argv)), "status": "started"}) + "\n")
        with (evidence / f"{name}.log").open("w") as log:
            try:
                rc = subprocess.run(list(map(str, argv)), cwd=cwd, env=env, stdout=log,
                                    stderr=subprocess.STDOUT).returncode
            except OSError as error:
                log.write(str(error) + "\n")
                rc = 127
        (evidence / f"{name}.exit").write_text(f"{rc}\n")
        with (evidence / "commands.jsonl").open("a") as stream:
            stream.write(json.dumps({"stage": name, "exit": rc}) + "\n")
        if required:
            require(rc == 0, f"{name} failed; inspect private evidence")
        return rc

    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        stage("clone", ["git", "clone", "--no-checkout", lock["source"]["repository"], checkout], ROOT)
        stage("checkout", ["git", "checkout", "--detach", lock["source"]["revision"]])
    check_source(lock, checkout, dependencies=False)
    lake = args.lean_bin / "lake"
    version = output([str(args.lean_bin / "lean"), "--version"])
    require(lock["source"]["lean_commit"] in version, "Unexpected installed Lean; no auto-install permitted")
    stage("cache", ["taskset", "-c", args.cpus, lake, "exe", "cache", "get"])
    check_inputs(lock, checkout, args.lean_bin, args.tools)
    stage("build", ["taskset", "-c", args.cpus, lake, "build"])
    stage("prepare", ["taskset", "-c", args.cpus, lake, "build", "comparator", "lean4export"])
    check_inputs(lock, checkout, args.lean_bin, args.tools)
    comparator, exporter = prepared_binaries(checkout)
    (evidence / "PREPARED_BINARIES.sha256").write_text(
        "".join(f"{digest(binary)}  {binary.resolve()}\n" for binary in (comparator, exporter)))
    driver = evidence / "PrintSolutionAxioms.lean"
    driver.write_text("".join(f"import {check['solution_module']}\n" for check in lock["checks"].values()) +
                      "".join(f"#print axioms {name}\n" for check in lock["checks"].values() for name in check["theorems"]))
    stage("solution-axioms", [lake, "env", "lean", driver])
    integrity_command = [sys.executable, Path(__file__).resolve(), "inputs", "--checkout", checkout,
                         "--lean-bin", args.lean_bin, "--tools", args.tools]
    for name, check in lock["checks"].items():
        stage(f"{name}.before", integrity_command)
        check_prepared(checkout, evidence)
        command = ["systemd-run", "--user", "--wait", "--collect", "--pty",
                   "--property=RestrictAddressFamilies=~AF_UNIX", f"--property=CPUAffinity={args.cpus.replace(',', ' ')}",
                   f"--property=CPUQuota={args.threads * 100}%", "--working-directory", checkout, "--",
                   "/usr/bin/env", "-i", f"HOME={Path.home()}", f"PATH={args.lean_bin}:/usr/bin:/bin",
                   f"LEAN_NUM_THREADS={args.threads}", f"GOMAXPROCS={args.threads}",
                   f"COMPARATOR_LANDRUN={args.tools / 'landrun' / lock['tools']['landrun']['binary']}",
                   f"COMPARATOR_LEAN4EXPORT={exporter}",
                   f"COMPARATOR_NANODA={args.tools / 'nanoda_lib' / lock['tools']['nanoda_lib']['binary']}",
                   "/bin/bash", "-eu", "-c",
                   'python3 "$1" sandbox-probe --cpus "$2"; exec "$3" env "$4" "$5"',
                   "verify", Path(__file__).resolve(), args.cpus, lake, comparator, check["config"]]
        stage(name, command, required=False)
        stage(f"{name}.after", integrity_command)
        check_prepared(checkout, evidence)
    record = audit(lock, checkout, args.lean_bin, args.tools, evidence, evidence)
    (evidence / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"PASS: both published configurations; private evidence: {evidence}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("metadata", help="Validate checked-in metadata only; no proof replay")
    probe = commands.add_parser("sandbox-probe")
    probe.add_argument("--cpus", required=True)
    for name in ("inputs", "audit", "run"):
        sub = commands.add_parser(name)
        sub.add_argument("--checkout", type=Path, required=True)
        sub.add_argument("--lean-bin", type=Path, required=True)
        sub.add_argument("--tools", type=Path, required=True)
        if name in ("audit", "run"):
            sub.add_argument("--evidence", type=Path, required=True)
        if name == "audit":
            sub.add_argument("--build-evidence", type=Path)
        if name == "run":
            sub.add_argument("--cpus", default="0-7")
            sub.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    for name in ("checkout", "lean_bin", "tools", "evidence", "build_evidence"):
        value = getattr(args, name, None)
        if value is not None:
            setattr(args, name, value.resolve())
    lock = load_lock()
    if args.command == "metadata":
        check_metadata(lock, load_json(ROOT / "verification-results.json"))
        print("PASS: verification metadata consistent (not a kernel replay)")
    elif args.command == "sandbox-probe":
        sandbox_probe(args.cpus)
    elif args.command == "inputs":
        check_inputs(lock, args.checkout, args.lean_bin, args.tools)
        print("PASS: pinned source, dependencies, toolchain, configurations and tool binaries")
    elif args.command == "audit":
        print(json.dumps(audit(lock, args.checkout, args.lean_bin, args.tools, args.evidence,
                               args.build_evidence or args.evidence), indent=2))
    else:
        run(lock, args)


if __name__ == "__main__":
    try:
        main()
    except (VerificationError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)

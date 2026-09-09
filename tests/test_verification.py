"""Fast, offline regressions; these do not replay research proofs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import hashlib
import subprocess
import sys


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verification", ROOT / "scripts/verify-openai.py")
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)


class VerificationTests(unittest.TestCase):
    def test_earlier_bad_hash_cannot_be_masked_by_later_good_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "first").write_text("changed")
            (root / "last").write_text("unchanged")
            hashes = {"first": "0" * 64,
                      "last": hashlib.sha256(b"unchanged").hexdigest()}
            with self.assertRaises(verification.VerificationError):
                verification.verify_hashes(root, hashes)

    def test_both_kernels_and_integrity_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = ("VERIFIED unprivileged; CapEff0; AF_UNIX EAFNOSUPPORT; Landlock ABI8; CPUs0-7\n"
                   "nanoda kernel accepts the solution\n"
                   "Lean default kernel accepts the solution\n"
                   "Your solution is okay!\n")
            for suffix in ("", ".before", ".after"):
                (root / f"Euler{suffix}.exit").write_text("0\n")
            (root / "Euler.log").write_text(log)
            self.assertEqual(verification.check_kernel_result(root, "Euler")["exit"], 0)
            for missing in ("nanoda kernel accepts the solution\n",
                            "Lean default kernel accepts the solution\n",
                            log.splitlines(keepends=True)[0]):
                (root / "Euler.log").write_text(log.replace(missing, ""))
                with self.assertRaises(verification.VerificationError):
                    verification.check_kernel_result(root, "Euler")
            (root / "Euler.log").write_text(log.replace("ABI8", "ABI0"))
            with self.assertRaises(verification.VerificationError):
                verification.check_kernel_result(root, "Euler")
            (root / "Euler.log").write_text(log)
            (root / "Euler.after.exit").write_text("1\n")
            with self.assertRaises(verification.VerificationError):
                verification.check_kernel_result(root, "Euler")
            (root / "Euler.after.exit").unlink()
            with self.assertRaises(verification.VerificationError):
                verification.check_kernel_result(root, "Euler")

    def test_zero_exit_does_not_override_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for suffix in ("", ".before", ".after"):
                (root / f"Euler{suffix}.exit").write_text("0\n")
            (root / "Euler.log").write_text(
                "nanoda kernel rejected the solution\nYour solution is okay!\n")
            with self.assertRaises(verification.VerificationError):
                verification.check_kernel_result(root, "Euler")

    def test_run_destinations_cannot_escape_private_directory(self):
        with self.assertRaises(verification.VerificationError):
            verification.private_path(ROOT / "README.md")
        self.assertEqual(verification.private_path(ROOT / "private/test"),
                         ROOT / "private/test")

    def test_cpu_selection_is_data_not_shell_syntax(self):
        self.assertEqual(verification.parse_cpus("0-2,5"), {0, 1, 2, 5})
        for value in ("", "-1", "3-1", "0; echo unsafe", "1-2-3"):
            with self.assertRaises(verification.VerificationError):
                verification.parse_cpus(value)

    def test_metadata_requires_complete_integrity_evidence(self):
        record = verification.load_json(ROOT / "verification-results.json")
        record["integrity"] = {}
        with self.assertRaises(verification.VerificationError):
            verification.check_metadata(verification.load_lock(), record)

    def test_duplicate_binary_receipt_cannot_hide_bad_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binaries = verification.prepared_binaries(root)
            for binary in binaries:
                binary.parent.mkdir(parents=True, exist_ok=True)
                binary.write_bytes(b"binary")
            good = hashlib.sha256(b"binary").hexdigest()
            (root / "PREPARED_BINARIES.sha256").write_text(
                f"{'0' * 64}  {binaries[0]}\n" +
                "".join(f"{good}  {binary}\n" for binary in binaries))
            with self.assertRaises(verification.VerificationError):
                verification.check_prepared(root, root)

    def test_metadata_cannot_expand_the_permitted_axioms(self):
        lock = verification.load_lock()
        record = verification.load_json(ROOT / "verification-results.json")
        expanded = ["propext", "Classical.choice", "sorryAx"]
        lock["permitted_axioms"] = expanded
        record["permitted_axioms"] = expanded
        record["solution_axioms"] = {name: expanded for name in record["solution_axioms"]}
        with self.assertRaises(verification.VerificationError):
            verification.check_metadata(lock, record)

    def test_worktree_guard_excludes_deleted_files_but_index_guard_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            script = root / "scripts/check-public-tree.py"
            script.write_bytes((ROOT / "scripts/check-public-tree.py").read_bytes())
            obsolete = root / "unapproved.txt"
            obsolete.write_text("test fixture")
            git(root, "init")
            git(root, "add", "scripts/check-public-tree.py", "unapproved.txt")
            obsolete.unlink()
            index_check = subprocess.run([sys.executable, str(script)], capture_output=True)
            worktree_check = subprocess.run(
                [sys.executable, str(script), "--include-untracked"], capture_output=True)
            self.assertEqual(index_check.returncode, 1)
            self.assertEqual(worktree_check.returncode, 0)

    def test_published_metadata_is_consistent(self):
        verification.check_metadata(verification.load_lock(),
                                    verification.load_json(ROOT / "verification-results.json"))


if __name__ == "__main__":
    unittest.main()

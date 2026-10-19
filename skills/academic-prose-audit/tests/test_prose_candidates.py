import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prose_candidates import CoverageError, candidates, scan_prose, visible_prose  # noqa: E402


FIXTURE = Path(__file__).parent / "fixtures" / "synthetic.tex"
ESCAPED = FIXTURE.with_name("escaped-percent.tex")
SCRIPT = ROOT / "scripts" / "prose_candidates.py"


class CandidateTests(unittest.TestCase):
    def test_detects_only_visible_prose_and_preserves_line_numbers(self):
        findings = list(candidates(FIXTURE.read_text(encoding="utf-8")))
        self.assertEqual([(line, phrase.lower()) for line, phrase, _, _ in findings], [
            (2, "a lot of"), (22, "you can see"),
            (22, "needless to say"), (22, "let's"),
        ])
        for _, _, context, question in findings:
            self.assertTrue(context)
            self.assertTrue(question.endswith("?"))
            self.assertNotIn("reference", context)

    def test_protected_fragments_do_not_join_into_candidates(self):
        self.assertEqual(list(candidates("a \\cite{secret} lot of prose.")), [])
        self.assertEqual(list(candidates("you % comment\n can see.")), [])

    def test_unclosed_regions_fail_closed(self):
        for source in (
            "$a lot of\nYou can see", "$$a lot of", "\\(a lot of",
            "``a lot of\nYou can see", '"a lot of', "“a lot of",
            "\\begin{unknown}\nA lot of", "\\begin{document} A lot of",
            "\\begin{missing", "\\end{document}",
            "\\emph{bad\nA lot of", "\\section[bad", "\\verb|a lot of",
            "\\verb", "{a lot of",
        ):
            with self.subTest(source=source), self.assertRaisesRegex(CoverageError, "coverage failure"):
                list(candidates(source))

    def test_escaped_percent_in_and_out_of_skipped_environment(self):
        source = ESCAPED.read_text(encoding="utf-8")
        self.assertEqual([(line, phrase.lower()) for line, phrase, _, _ in candidates(source)],
                         [(2, "a lot of"), (6, "you can see")])
        self.assertEqual(list(candidates("\\begin{verbatim}\n\\\\% literal\n\\end{verbatim}\nA lot of"))[-1][1], "A lot of")

    def test_skipped_command_argument_coverage(self):
        source = "A lot of prose. \\section{You can see more} \\cite{key} \\foo[option]{Needless to say}."
        scan = scan_prose(source)
        self.assertEqual((scan.skipped_arguments, scan.lettered_arguments), (4, 4))
        self.assertEqual([phrase for _, phrase, _, _ in candidates(source)], ["A lot of"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.tex"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn("skipped command arguments: 4 (4 contain letters", result.stderr)
            self.assertIn("citation keys/labels", result.stderr)

    def test_cli_validates_all_inputs_before_stdout_and_keeps_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.tex"
            valid.write_bytes(b"A lot of prose.\n")
            invalid = Path(directory) / "invalid.tex"
            invalid.write_bytes(b"\xff\xfe\n")
            before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (valid, invalid)}
            for second in (invalid, Path(directory) / "absent.tex"):
                with self.subTest(second=second):
                    result = subprocess.run([sys.executable, str(SCRIPT), str(valid), str(second)],
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertIn(str(second), result.stderr)
                    for path, digest in before.items():
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            truncated = Path(directory) / "truncated.tex"
            truncated.write_bytes(b"\\begin{verbatim}\n\\% escaped\n")
            digest = hashlib.sha256(truncated.read_bytes()).hexdigest()
            failed = subprocess.run([sys.executable, str(SCRIPT), str(valid), str(truncated)],
                                    capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, "")
            self.assertIn("coverage failure: unclosed environment", failed.stderr)
            self.assertEqual(hashlib.sha256(truncated.read_bytes()).hexdigest(), digest)
            result = subprocess.run([sys.executable, str(SCRIPT), str(valid)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn("A lot of", result.stdout)
            self.assertIn("Privacy:", result.stderr)
            self.assertEqual(hashlib.sha256(valid.read_bytes()).hexdigest(), before[valid])

    def test_cli_reads_without_writing(self):
        before = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURE)],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(result.stdout.count("question:"), 4)
        self.assertIn("non-exhaustive", result.stderr.lower())
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()

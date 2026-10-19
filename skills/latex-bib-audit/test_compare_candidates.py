"""Safety, mocked-parser, and optional real-pybtex integration checks."""

import contextlib
import io
import importlib.util
import json
import os

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import compare_candidates as comparator


def entry(fields=None, authors=None, kind="article"):
    return SimpleNamespace(fields=fields or {}, persons={"author": authors} if authors else {}, type=kind)


class CandidateTests(unittest.TestCase):
    def test_preflight_counts_and_duplicate_keys(self):
        self.assertEqual(comparator.entry_keys('@string{a="@article{fake,x}"}\n@article{A,title={Hi}}'), ["A"])
        with self.assertRaisesRegex(comparator.InputError, "duplicate entry keys"):
            comparator.entry_keys("@article{A,title={a}}\n@book{A,title={b}}")
        with self.assertRaisesRegex(comparator.InputError, "unclosed"):
            comparator.entry_keys("@article{A,title={a}")

    def test_inheritance_preserves_child_fields(self):
        entries = {
            "parent": entry({"title": "Proceedings", "year": "2020", "author": "Parent"}),
            "child": entry({"crossref": "parent", "title": "Paper"}),
        }
        self.assertEqual(comparator.effective_fields("child", entries)["year"], "2020")
        self.assertEqual(comparator.effective_fields("child", entries)["title"], "Paper")

    def test_missing_and_cyclic_inheritance(self):
        with self.assertRaisesRegex(comparator.InputError, "missing xdata parent"):
            comparator.effective_fields("a", {"a": entry({"xdata": "absent"})})
        with self.assertRaisesRegex(comparator.InputError, "cycle"):
            comparator.effective_fields("a", {"a": entry({"crossref": "a"})})

    def test_missing_key_and_ambiguous_version(self):
        original = {"A": entry({"title": "{Work}", "year": "2021", "doi": "10/a"}, ["One, A"]),
                    "B": entry({"title": "Another"})}
        candidate = {"A": entry({"title": "Work", "year": "2022", "doi": "10/b"}, ["One, A"]),
                     "C": entry({"title": "Different"})}
        report = comparator.compare_entries(original, candidate)
        self.assertEqual(report["unmatched_candidate_keys"], ["C"])
        self.assertEqual(report["entries"][1]["issues"], ["missing candidate key"])
        self.assertIn("DOI conflict", report["entries"][0]["issues"])
        self.assertIn("publication/version fields differ; review versions manually", report["entries"][0]["issues"])

    def test_author_order_and_missing_title(self):
        first = {"a": entry({"title": "X"}, ["Alpha", "Beta"])}
        second = {"a": entry({}, ["Beta", "Alpha"])}
        issues = comparator.compare_entries(first, second)["entries"][0]["issues"]
        self.assertIn("missing title; identity unresolved", issues)
        self.assertIn("ordered authors differ; identity unresolved", issues)

    def test_html_rejected_without_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.bib"
            path.write_text("<!DOCTYPE HTML><html>blocked</html>", encoding="utf-8")
            with self.assertRaisesRegex(comparator.InputError, "HTML is not BibTeX"):
                comparator.load_entries(path)

    def test_missing_dependency_and_parser_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bib"
            path.write_text("@article{A,title={Hi}}", encoding="utf-8")
            with mock.patch.dict(sys.modules, {"pybtex": None, "pybtex.database": None}):
                with self.assertRaisesRegex(RuntimeError, "pybtex is required"):
                    comparator.load_entries(path)
            fake = SimpleNamespace(parse_string=mock.Mock(side_effect=ValueError("bad BibTeX")))
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": fake}):
                with self.assertRaisesRegex(comparator.InputError, "parse/preflight failed"):
                    comparator.load_entries(path)
                fake.parse_string.side_effect = None
                fake.parse_string.return_value = SimpleNamespace(entries={})
                with self.assertRaisesRegex(comparator.InputError, "count/key mismatch"):
                    comparator.load_entries(path)

    def test_non_bibtex_error_response_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.bib"
            path.write_text("HTTP 429: retry later", encoding="utf-8")
            fake = SimpleNamespace(parse_string=mock.Mock())
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": fake}):
                with self.assertRaisesRegex(comparator.InputError, "no BibTeX entries"):
                    comparator.load_entries(path)
                fake.parse_string.assert_not_called()

    def test_repeated_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.bib"
            candidate = Path(directory) / "candidate.bib"
            original.write_text("@article{A,title={Work}}", encoding="utf-8")
            candidate.write_text("@article{A,title={Work}}", encoding="utf-8")
            fake = SimpleNamespace(parse_string=lambda text, fmt: SimpleNamespace(
                entries={"A": entry({"title": "Work"})}))
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": fake}):
                outputs = []
                for unused in range(2):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(comparator.main([str(original), str(candidate)]), 0)
                    outputs.append(output.getvalue())
                self.assertEqual(outputs[0], outputs[1])
                self.assertEqual(json.loads(outputs[0])["original_count"], 1)

    def test_public_metadata_only_and_generic_errors(self):
        original = {"A": entry({"title": "Work", "note": "private notes",
                                "file": "/private/local/path", "url": "https://private.invalid/token",
                                "doi": "10/test", "crossref": "private-parent-identifier"})}
        report = comparator.compare_entries(original, original)
        encoded = json.dumps(report)
        for secret in ("private notes", "/private/local/path", "private.invalid", "private-parent-identifier"):
            self.assertNotIn(secret, encoded)
        self.assertIn("10/test", encoded)

    def test_exclusive_output_and_unchanged_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "original.bib"
            second = Path(directory) / "candidate.bib"
            output = Path(directory) / "report.json"
            original_bytes = b"@article{A,title={Work}}\n"
            candidate_bytes = b"@article{A,title={Work},note={secret}}\n"
            first.write_bytes(original_bytes)
            second.write_bytes(candidate_bytes)
            fake = SimpleNamespace(parse_string=lambda text, fmt: SimpleNamespace(
                entries={"A": entry({"title": "Work", "note": "secret"})}))
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": fake}):
                for target in (first, second):
                    with self.assertRaisesRegex(comparator.InputError, "collides"):
                        comparator.write_exclusive(target, "overwrite", (first, second))
                alias = Path(directory) / "hardlink.bib"
                os.link(first, alias)
                with self.assertRaises(comparator.InputError):
                    comparator.write_exclusive(alias, "overwrite", (first, second))
                alias.unlink()
                alias.symlink_to(first)
                with self.assertRaises(comparator.InputError):
                    comparator.write_exclusive(alias, "overwrite", (first, second))
                alias.unlink()
                alias.symlink_to(Path(directory) / "absent")
                with self.assertRaises(comparator.InputError):
                    comparator.write_exclusive(alias, "overwrite", (first, second))
                output.write_bytes(b"old report")
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(comparator.main([str(first), str(second), "--output", str(output)]), 2)
                self.assertEqual(output.read_bytes(), b"old report")
                output.unlink()
                self.assertEqual(comparator.main([str(first), str(second), "--output", str(output)]), 0)
                self.assertNotIn("secret", output.read_text())
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
                second.write_bytes(b"<html>private error</html>")
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(comparator.main([str(first), str(second), "--output", str(Path(directory) / "new.json")]), 2)
                self.assertFalse((Path(directory) / "new.json").exists())
            self.assertEqual(first.read_bytes(), original_bytes)
            self.assertEqual(second.read_bytes(), b"<html>private error</html>")

    def test_parser_mismatch_and_private_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bib"
            path.write_bytes(b"@article{A,title={Work}}")
            fake = SimpleNamespace(parse_string=mock.Mock(side_effect=ValueError("private manuscript text")))
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": fake}):
                with self.assertRaises(comparator.InputError) as caught:
                    comparator.load_entries(path)
                self.assertNotIn("private manuscript", str(caught.exception))
                fake.parse_string.side_effect = None
                fake.parse_string.return_value = SimpleNamespace(entries={"a": entry({"title": "Work"})})
                with self.assertRaisesRegex(comparator.InputError, "key mismatch"):
                    comparator.load_entries(path)
                fake.parse_string.return_value = SimpleNamespace(entries={"A": entry({"TITLE": "Work"})})
                with self.assertRaisesRegex(comparator.InputError, "field casing mismatch"):
                    comparator.load_entries(path)
            self.assertEqual(path.read_bytes(), b"@article{A,title={Work}}")


@unittest.skipUnless(importlib.util.find_spec("pybtex"), "pybtex is not installed")
class PybtexIntegrationTests(unittest.TestCase):
    def test_real_parser_key_and_field_casing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bib"
            payload = b"@article{CaseKey, TITLE={Work}, AUTHOR={One, A and Two, B}, YEAR={2020}}\n"
            path.write_bytes(payload)
            from pybtex.database import parse_string
            with contextlib.redirect_stderr(io.StringIO()):
                parsed = parse_string(payload.decode(), "bibtex")
            exact = set(parsed.entries) == {"CaseKey"} and all(
                name == name.lower() for value in parsed.entries.values()
                for name in (*value.fields, *value.persons)
            )
            if exact:
                entries = comparator.load_entries(path)
                self.assertEqual(set(entries), {"CaseKey"})
                fields = comparator.effective_fields("CaseKey", entries)
                self.assertEqual(fields["title"], "Work")
                self.assertEqual(len(fields["author"]), 2)
            else:
                with self.assertRaisesRegex(comparator.InputError, "mismatch"):
                    comparator.load_entries(path)
            self.assertEqual(path.read_bytes(), payload)

    def test_real_parser_rejects_case_or_count_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.bib"
            payload = b"@article{A,title={First}}\n@article{a,title={Second}}\n"
            path.write_bytes(payload)
            try:
                entries = comparator.load_entries(path)
            except comparator.InputError:
                pass
            else:
                self.assertEqual(set(entries), {"A", "a"})
            self.assertEqual(path.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()

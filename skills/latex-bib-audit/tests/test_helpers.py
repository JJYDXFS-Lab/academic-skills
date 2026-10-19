import sys
import tempfile
import json
import contextlib
import io
import os
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import citation_inventory
import compare_candidates
import fetch_candidates


def entry(fields, authors=None):
    return SimpleNamespace(fields=fields, persons={"author": authors} if authors else {}, type="article")


class HelperTests(unittest.TestCase):
    def test_field_case_collisions_and_named_duplicate_keys(self):
        with self.assertRaisesRegex(compare_candidates.InputError, "duplicate field names"):
            compare_candidates.entry_keys("@article{A,Title={one},title={two}}")
        with self.assertRaisesRegex(compare_candidates.InputError, "duplicate entry keys: A"):
            compare_candidates.entry_keys("@article{A,title={one}}@article{A,title={two}}")

    def test_accents_and_duplicate_flags(self):
        self.assertEqual(compare_candidates.normalize(r"{\'E}cole"), "ecole")
        data = {"first": entry({"doi": "10/a", "title": "{Work}", "year": "2020"}, ["Person"]),
                "second": entry({"doi": "https://doi.org/10/a", "title": "Work", "year": "2020"}, ["Person"])}
        self.assertEqual({flag["basis"] for flag in compare_candidates.duplicate_flags(data)},
                         {"doi", "title_author_year"})

    def test_retry_numeric_date_and_http_mock(self):
        self.assertEqual(fetch_candidates.retry_delay("99"), 10)
        date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=30))
        self.assertGreater(fetch_candidates.retry_delay(date), 0)
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"message":{}}'
        error = urllib.error.HTTPError("https://api.crossref.org/works", 429, "retry", {"Retry-After": "0"}, None)
        opener = mock.Mock(side_effect=[error, response])
        sleep = mock.Mock()
        self.assertEqual(fetch_candidates.request_json("https://api.crossref.org/works", opener, sleep),
                         b'{"message":{}}')
        sleep.assert_called_once()

    def test_candidate_failure_and_ambiguous_results(self):
        with mock.patch.object(fetch_candidates, "crossref_work") as crossref, \
             mock.patch.object(fetch_candidates, "arxiv_work") as arxiv:
            unverified, record = fetch_candidates.candidate_for("k", entry({"title": "Private draft"}, ["Private Name"]))
            crossref.assert_not_called()
            arxiv.assert_not_called()
        self.assertIsNone(unverified)
        self.assertEqual(record["status"], "unverified")
        with mock.patch.object(fetch_candidates, "crossref_work") as crossref:
            _, invalid = fetch_candidates.candidate_for("k", entry({"doi": "10.1234/private note"}))
            crossref.assert_not_called()
        self.assertEqual(invalid["status"], "unverified")
        with mock.patch.object(fetch_candidates, "crossref_work", return_value=(
            [{"title": ["X"]}, {"title": ["X"]}], "https://api.crossref.org/works")):
            candidate, record = fetch_candidates.candidate_for("k", entry({"title": "X"}, ["A"]),
                                                                 public_title_search=True)
        self.assertIsNone(candidate)
        self.assertEqual(record["match_count"], 2)

    def test_doi_resolver_normalized_before_lookup(self):
        with mock.patch.object(fetch_candidates, "crossref_work", return_value=([], "source")) as lookup:
            fetch_candidates.candidate_for("k", entry({"doi": "https://doi.org/10.1234/ABC"}))
        self.assertEqual(lookup.call_args.kwargs["doi"], "10.1234/abc")

    def test_fetch_writes_exclusive_outputs_preserves_original_and_unverified(self):
        class FakeBibliography:
            def __init__(self, entries):
                self.entries = entries

            def to_string(self, _format):
                return "".join("@article{" + key + ",title={" + item.fields["title"] + "}}\n"
                               for key, item in self.entries.items())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bib = root / "original.bib"
            payload = "@article{a,title={Original}}\n@article{b,title={Retained}}\n"
            bib.write_text(payload, encoding="utf-8")
            candidate, ledger = root / "candidate.bib", root / "ledger.json"
            mocked = SimpleNamespace(BibliographyData=FakeBibliography)
            entries = {"a": entry({"title": "Original", "doi": "10/x"}), "b": entry({"title": "Retained"})}
            def lookup(key, _entry, public_title_search=False):
                if key == "a":
                    return {"title": "Original", "year": "2024"}, {"key": key, "status": "candidate"}
                return None, {"key": key, "status": "unverified"}
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(), "pybtex.database": mocked}), \
                 mock.patch.object(fetch_candidates, "load_entries", return_value=entries), \
                 mock.patch.object(fetch_candidates, "candidate_for", side_effect=lookup), \
                 mock.patch.object(fetch_candidates.time, "sleep"):
                arguments = [str(bib), "--keys", "a", "b", "--limit", "2", "--candidate", str(candidate),
                             "--ledger", str(ledger)]
                self.assertEqual(fetch_candidates.main(arguments), 0)
                first = candidate.read_bytes()
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(fetch_candidates.main(arguments), 2)
            self.assertEqual(candidate.read_bytes(), first)
            self.assertIn("Retained", candidate.read_text())
            self.assertEqual(bib.read_text(), payload)
            self.assertEqual(json.loads(ledger.read_text())["entries"][1]["status"], "unverified")

    def test_cli_default_never_queries_private_title(self):
        class FakeBibliography:
            def __init__(self, entries):
                self.entries = entries

            def to_string(self, _format):
                return "@article{private,title={Unpublished result}}\n"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bib = root / "original.bib"
            bib.write_text("@article{private,title={Unpublished result}}", encoding="utf-8")
            with mock.patch.dict(sys.modules, {"pybtex": SimpleNamespace(),
                                               "pybtex.database": SimpleNamespace(BibliographyData=FakeBibliography)}), \
                 mock.patch.object(fetch_candidates, "load_entries", return_value={
                     "private": entry({"title": "Unpublished result"}, ["Private Researcher"])}), \
                 mock.patch.object(fetch_candidates, "crossref_work") as crossref, \
                 mock.patch.object(fetch_candidates, "arxiv_work") as arxiv:
                self.assertEqual(fetch_candidates.main([str(bib), "--keys", "private", "--limit", "1",
                                                        "--candidate", str(root / "candidate.bib"),
                                                        "--ledger", str(root / "ledger.json")]), 0)
                crossref.assert_not_called()
                arxiv.assert_not_called()
            self.assertEqual(json.loads((root / "ledger.json").read_text())["entries"][0]["status"], "unverified")

    def test_reachable_inventory_and_stale_aux(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text("\\input{section}\n% \\cite{ghost}\n\\nocite{extra}\n", encoding="utf-8")
            (root / "section.tex").write_text("\\citep[see]{known,missing}\n", encoding="utf-8")
            bib = root / "ref.bib"
            bib.write_text("@article{known,title={A}}", encoding="utf-8")
            with mock.patch.object(citation_inventory, "load_entries", return_value={
                "known": entry({}), "extra": entry({}), "unused": entry({})}):
                report = citation_inventory.inventory(root / "main.tex", bib)
            self.assertEqual(report["undefined"], ["missing"])
            self.assertEqual(report["unused"], ["unused"])
            self.assertEqual(report["locations"]["known"][0]["line"], 1)
            aux = root / "main.aux"
            aux.write_text("\\citation{known}", encoding="utf-8")
            with mock.patch.object(citation_inventory, "source_stamp", return_value={}):
                citation_inventory.corroborate(report, aux, root / "main.tex")
            self.assertIn("aux_corroboration", report)

    def test_nested_inputs_resolve_from_main_and_ignore_non_cite_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sections").mkdir()
            (root / "main.tex").write_text("\\input{sections/one}\n", encoding="utf-8")
            (root / "sections/one.tex").write_text(
                "\\input{two}\\addbibresource{refs.bib}\\cite{actual}\\excite{ghost}\\recite{ghost}\n",
                encoding="utf-8")
            (root / "two.tex").write_text("\\textcite{other}\n", encoding="utf-8")
            bib = root / "refs.bib"
            bib.write_text("dummy", encoding="utf-8")
            with mock.patch.object(citation_inventory, "load_entries", return_value={
                "actual": entry({}), "other": entry({})}):
                report = citation_inventory.inventory(root / "main.tex", bib)
            self.assertEqual(set(report["locations"]), {"actual", "other"})
            self.assertEqual(len(report["sources"]), 3)
            self.assertEqual(report["gaps"], [])

    def test_multiple_bib_resources_and_aux_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            main = root / "main.tex"
            main.write_text("\\bibliography{first,second}\n\\cite{known}\n", encoding="utf-8")
            bib = root / "first.bib"
            bib.write_text("dummy", encoding="utf-8")
            aux = root / "main.aux"
            aux.write_text("\\citation{known}\n", encoding="utf-8")
            os.utime(aux, ns=(1, 1))
            with mock.patch.object(citation_inventory, "load_entries", return_value={"known": entry({})}):
                report = citation_inventory.inventory(main, bib)
            self.assertTrue(any("multiple Bib resources" in gap["reason"] for gap in report["gaps"]))
            self.assertFalse(any("not matched" in gap["reason"] for gap in report["gaps"]))
            citation_inventory.corroborate(report, aux, main)
            self.assertNotIn("aux_corroboration", report)
            self.assertTrue(any("stale auxiliary" in gap["reason"] for gap in report["gaps"]))
            os.utime(aux, ns=(main.stat().st_mtime_ns + 10_000_000_000,) * 2)
            citation_inventory.corroborate(report, aux, main)
            self.assertEqual(report["aux_corroboration"]["keys"], ["known"])

    def test_crossref_inheritance_transitive_and_nocite_all(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text("\\cite{child}\n", encoding="utf-8")
            bib = root / "ref.bib"
            bib.write_text("dummy", encoding="utf-8")
            entries = {"child": entry({"crossref": "parent"}), "parent": entry({"xdata": "grand"}),
                       "grand": entry({}), "unused": entry({})}
            with mock.patch.object(citation_inventory, "load_entries", return_value=entries):
                report = citation_inventory.inventory(root / "main.tex", bib)
            self.assertEqual(report["unused"], ["unused"])
            (root / "main.tex").write_text("\\nocite{*}\n", encoding="utf-8")
            with mock.patch.object(citation_inventory, "load_entries", return_value=entries):
                report = citation_inventory.inventory(root / "main.tex", bib)
            self.assertEqual(report["unused"], [])


if __name__ == "__main__":
    unittest.main()

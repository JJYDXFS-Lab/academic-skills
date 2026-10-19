"""Explicit, bounded public-metadata candidate retrieval; never edits source BibTeX."""

import argparse
import copy
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from compare_candidates import InputError, load_entries, normalize, normalize_doi, source_stamp, write_exclusive


def retry_delay(value):
    try:
        return min(10.0, max(0.0, float(value)))
    except (ValueError, TypeError):
        try:
            return min(10.0, max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()))
        except (ValueError, TypeError, OverflowError):
            return 1.0


def request_json(url, opener=urllib.request.urlopen, sleep=time.sleep):
    if not url.startswith(("https://api.crossref.org/", "https://export.arxiv.org/")):
        raise InputError("unsupported metadata endpoint")
    for attempt in range(3):
        try:
            with opener(urllib.request.Request(url, headers={"User-Agent": "latex-bib-audit/1.0 (public-metadata-only)",
                                                             "Accept": "application/json, application/atom+xml"}), timeout=10) as response:
                body = response.read(1_000_001)
                if len(body) > 1_000_000:
                    raise InputError("metadata response too large")
                if b"<html" in body[:256].lower():
                    raise InputError("HTML response is not metadata")
                return body
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise InputError("metadata HTTP request failed") from error
            sleep(retry_delay(error.headers.get("Retry-After")))
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == 2:
                raise InputError("metadata network request failed") from error
            sleep(1)
    raise InputError("metadata request failed")


def crossref_work(doi=None, title=None, author=None, fetch=request_json):
    if doi:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        return [json.loads(fetch(url))["message"]], url
    query = urllib.parse.urlencode({"query.title": title, "query.author": author, "rows": 3})
    url = "https://api.crossref.org/works?" + query
    return json.loads(fetch(url))["message"].get("items", []), url


def public_fields(work):
    authors = work.get("author", [])
    issued = work.get("issued", {}).get("date-parts", [[]])[0]
    return {name: value for name, value in {
        "title": (work.get("title") or [None])[0], "year": str(issued[0]) if issued else None,
        "doi": work.get("DOI"), "journal": (work.get("container-title") or [None])[0],
        "author": " and ".join(" ".join(filter(None, (person.get("given"), person.get("family"))))
                                 for person in authors) if authors else None,
    }.items() if value}


def arxiv_work(identifier, fetch=request_json):
    url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(identifier, safe="")
    root = ET.fromstring(fetch(url))
    atom = "{http://www.w3.org/2005/Atom}"
    entry = root.find(atom + "entry")
    if entry is None or "arxiv.org/abs/" not in (entry.findtext(atom + "id") or ""):
        return [], url
    fields = {"title": " ".join((entry.findtext(atom + "title") or "").split()),
              "author": " and ".join(name.text or "" for name in entry.findall(atom + "author/" + atom + "name")),
              "year": (entry.findtext(atom + "published") or "")[:4], "eprint": identifier}
    return [fields], url


def candidate_for(key, entry, fetch=request_json, public_title_search=False):
    fields = entry.fields
    doi = normalize_doi(fields.get("doi", ""))
    arxiv = fields.get("eprint", "").strip() if fields.get("archiveprefix", "").lower() == "arxiv" else ""
    title = fields.get("title", "").strip()
    authors = entry.persons.get("author", [])
    if doi and (len(doi) > 256 or not re.fullmatch(r"10\.\d{4,9}/[^\s]+", doi, re.I)):
        return None, {"key": key, "status": "unverified", "reason": "invalid DOI identifier; no request sent"}
    if arxiv and (len(arxiv) > 80 or not re.fullmatch(r"(?:\d{4}\.\d{4,5}|[A-Za-z.-]+/\d{7})(?:v\d+)?", arxiv)):
        return None, {"key": key, "status": "unverified", "reason": "invalid arXiv identifier; no request sent"}
    if not doi and not arxiv and not (public_title_search and title and authors):
        return None, {"key": key, "status": "unverified", "reason": "no DOI/arXiv identifier; title search requires explicit already-public metadata confirmation"}
    try:
        if doi or not arxiv:
            matches, url = crossref_work(doi=doi, title=title, author=str(authors[0]) if authors else None, fetch=fetch)
            matches = [public_fields(work) for work in matches]
        else:
            matches, url = arxiv_work(arxiv, fetch=fetch)
        if not doi:
            matches = [match for match in matches if title and normalize(match.get("title", "")) == normalize(title)]
        if len(matches) != 1:
            return None, {"key": key, "status": "unverified", "reason": "zero or ambiguous matching records",
                          "source": url, "match_count": len(matches)}
        match = matches[0]
        if title and normalize(match.get("title", "")) != normalize(title):
            return None, {"key": key, "status": "unverified", "reason": "identifier/title identity conflict", "source": url}
        return match, {"key": key, "status": "candidate; source unverified", "source": url,
                       "source_fields": match, "ambiguity": "publication version and author order need manual review"}
    except (InputError, ValueError, KeyError, ET.ParseError, TypeError):
        return None, {"key": key, "status": "unverified", "reason": "metadata lookup or parse failed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bib", type=Path)
    parser.add_argument("--keys", nargs="+", required=True)
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--public-title-search", action="store_true",
                        help="opt in to title + first-author lookup ONLY after confirming these BibTeX fields are already public")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.limit <= 20 or len(set(args.keys)) != len(args.keys) or len(args.keys) > args.limit:
            raise InputError("select unique keys within a limit of 1..20")
        if args.candidate == args.ledger or args.candidate.resolve() == args.ledger.resolve():
            raise InputError("output paths collide")
        if any(path.exists() or path.is_symlink() for path in (args.candidate, args.ledger)):
            raise InputError("output already exists")
        original = load_entries(args.bib)
        if any(key not in original for key in args.keys):
            raise InputError("selected key not found")
        from pybtex.database import BibliographyData
        candidates = copy.deepcopy(original)
        ledger = []
        for index, key in enumerate(args.keys):
            if index:
                time.sleep(1)
            match, record = candidate_for(key, original[key], public_title_search=args.public_title_search)
            ledger.append(record)
            if match:
                for name in ("title", "year", "doi", "journal"):
                    if name in match:
                        candidates[key].fields[name] = match[name]
        provenance = {"input": source_stamp(args.bib), "selected_keys": args.keys,
                      "external_cache": "none; HTTP responses not persisted", "retention": "delete outputs per local policy",
                      "entries": ledger}
        bib_payload = BibliographyData(entries=candidates).to_string("bibtex")
        ledger_payload = json.dumps(provenance, indent=2, ensure_ascii=False) + "\n"
        if source_stamp(args.bib) != provenance["input"]:
            raise InputError("input changed during retrieval; no output written")
        write_exclusive(args.candidate, bib_payload, (args.bib,))
        try:
            write_exclusive(args.ledger, ledger_payload, (args.bib, args.candidate))
        except InputError:
            args.candidate.unlink()
            raise
    except (InputError, RuntimeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

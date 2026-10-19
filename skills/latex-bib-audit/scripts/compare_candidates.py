"""Conservative, read-only comparison of two local BibTeX files."""

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path


class InputError(Exception):
    pass


PUBLIC_FIELDS = frozenset({
    "title", "subtitle", "author", "editor", "year", "date", "journal",
    "booktitle", "publisher", "volume", "number", "pages", "eid", "doi",
    "eprint", "archiveprefix", "primaryclass", "version",
})


def source_stamp(path):
    stat = path.stat()
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mtime_ns": stat.st_mtime_ns, "size_bytes": stat.st_size}


def field_names(body):
    """Preflight top-level assignments; parser still decides BibTeX semantics."""
    names = []
    depth = 0
    quoted = False
    escaped = False
    index = 0
    while index < len(body):
        char = body[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"' and depth == 0:
            quoted = not quoted
        elif not quoted:
            if char == "{":
                depth += 1
            elif char == "}" and depth:
                depth -= 1
            elif depth == 0 and (index == 0 or body[index - 1] == ","):
                match = re.match(r"\s*([A-Za-z][A-Za-z0-9_-]*)\s*=", body[index:])
                if match:
                    names.append(match.group(1))
        index += 1
    lowered = [name.lower() for name in names]
    if len(lowered) != len(set(lowered)):
        raise InputError("duplicate field names in entry (case-insensitive)")
    return names


def entry_keys(text):
    """Preflight entry count and collisions; the BibTeX parser remains authoritative."""
    keys = []
    position = 0
    while position < len(text):
        start = text.find("@", position)
        if start < 0:
            break
        header = re.match(r"@\s*([A-Za-z]+)\s*([({])", text[start:])
        if not header:
            position = start + 1
            continue
        kind = header.group(1).lower()
        opening = header.group(2)
        closing = "}" if opening == "{" else ")"
        position = start + header.end()
        depth = 0
        quoted = False
        escaped = False
        key_end = None
        key_start = position
        while position < len(text):
            char = text[position]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == "{":
                    depth += 1
                elif char == "}" and depth:
                    depth -= 1
                elif char == closing and depth == 0:
                    break
                elif char == "," and depth == 0 and key_end is None:
                    key_end = position
            position += 1
        if position == len(text):
            raise InputError("unclosed BibTeX entry")
        if kind not in ("comment", "string", "preamble"):
            if key_end is None:
                raise InputError("entry without a key delimiter")
            key = text[key_start:key_end].strip()
            if not key or any(char.isspace() for char in key):
                raise InputError("empty or invalid entry key")
            keys.append(key)
            field_names(text[key_end + 1:position])
        position += 1
    if len(keys) != len(set(keys)):
        duplicates = sorted(key for key in set(keys) if keys.count(key) > 1)
        raise InputError("duplicate entry keys: " + ", ".join(duplicates))
    return keys


def load_entries(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise InputError("cannot read input as UTF-8 BibTeX") from error
    if text.lstrip().lower().startswith(("<html", "<!doctype html")):
        raise InputError("HTML is not BibTeX")
    try:
        from pybtex.database import parse_string
    except ImportError as error:
        raise RuntimeError("pybtex is required; install it separately to parse BibTeX") from error
    try:
        keys = entry_keys(text)
        if not keys:
            raise InputError("no BibTeX entries found; refusing empty or error response")
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            data = parse_string(text, "bibtex")
    except InputError:
        raise
    except Exception as error:
        raise InputError("BibTeX parse/preflight failed; inspect input locally") from error
    if len(keys) != len(data.entries) or set(keys) != set(data.entries):
        raise InputError("entry count/key mismatch; refusing partial comparison")
    for entry in data.entries.values():
        entry.fields = {name.lower(): value for name, value in entry.fields.items()}
        entry.persons = {name.lower(): value for name, value in entry.persons.items()}
    return data.entries


def effective_fields(key, entries, trail=()):
    if key in trail:
        raise InputError("inherited-field cycle")
    entry = entries[key]
    fields = dict(entry.fields)
    for relation in ("crossref", "xdata"):
        for parent in fields.get(relation, "").split(","):
            parent = parent.strip()
            if not parent:
                continue
            if parent not in entries:
                raise InputError(f"missing {relation} parent")
            for name, value in effective_fields(parent, entries, (*trail, key)).items():
                if name not in ("crossref", "xdata"):
                    fields.setdefault(name, value)
    if "author" in entry.persons:
        fields["author"] = [str(person) for person in entry.persons["author"]]
    return {name: value for name, value in fields.items() if name in PUBLIC_FIELDS}


def normalize(value):
    if isinstance(value, list):
        return [normalize(item) for item in value]
    text = str(value)
    text = re.sub(r"\\(?:['`\"^~=.uvH])\s*\{?([A-Za-z])\}?", r"\1", text)
    text = re.sub(r"\\(ae|oe|ss|o|l)\b", lambda match: {
        "ae": "ae", "oe": "oe", "ss": "ss", "o": "o", "l": "l"
    }[match.group(1).lower()], text, flags=re.I)
    return " ".join(text.replace("{", "").replace("}", "").split()).casefold()


def normalize_doi(value):
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", normalize(value))


def duplicate_flags(entries):
    groups = {}
    for key in sorted(entries):
        fields, _ = resolved_fields(key, entries)
        doi = normalize_doi(fields.get("doi", ""))
        title = normalize(fields.get("title", ""))
        authors = normalize(fields.get("author", []))
        year = normalize(fields.get("year", ""))
        if doi:
            groups.setdefault(("doi", doi), []).append(key)
        if title and authors and year:
            groups.setdefault(("title_author_year", title, tuple(authors), year), []).append(key)
    return [{"basis": identity[0], "keys": keys} for identity, keys in groups.items() if len(keys) > 1]


def compare_entries(original, candidate):
    """Compare only identical keys; never infer a different key's identity."""
    results = []
    for key in sorted(original):
        source = original[key]
        if key not in candidate:
            old_fields, old_error = resolved_fields(key, original)
            results.append({"key": key, "status": "unverified", "issues": ["missing candidate key"],
                            "original_type": source.type, "original_fields": old_fields,
                            "candidate_type": None, "candidate_fields": None, "differences": {}})
            if old_error:
                results[-1]["issues"].append("original: " + old_error)
            continue
        target = candidate[key]
        issues = []
        old_fields, old_error = resolved_fields(key, original)
        new_fields, new_error = resolved_fields(key, candidate)
        if old_error:
            issues.append("original: " + old_error)
        if new_error:
            issues.append("candidate: " + new_error)
        field_names = sorted(set(old_fields) | set(new_fields))
        differences = {
            name: {"original": old_fields.get(name), "candidate": new_fields.get(name)}
            for name in field_names
            if (normalize_doi if name == "doi" else normalize)(old_fields.get(name, "")) !=
               (normalize_doi if name == "doi" else normalize)(new_fields.get(name, ""))
        }
        if source.type != target.type:
            issues.append("entry type differs")
        old_doi = normalize_doi(old_fields.get("doi", ""))
        new_doi = normalize_doi(new_fields.get("doi", ""))
        if old_doi and new_doi and old_doi != new_doi:
            issues.append("DOI conflict")
        old_title = normalize(old_fields.get("title", ""))
        new_title = normalize(new_fields.get("title", ""))
        if not old_title or not new_title:
            issues.append("missing title; identity unresolved")
        elif old_title != new_title:
            issues.append("title differs; identity unresolved")
        old_authors = normalize(old_fields.get("author", []))
        new_authors = normalize(new_fields.get("author", []))
        if not old_authors or not new_authors:
            issues.append("missing authors; identity unresolved")
        elif old_authors != new_authors:
            issues.append("ordered authors differ; identity unresolved")
        if any(name in differences for name in ("year", "journal", "booktitle", "eprint", "archiveprefix", "version")):
            issues.append("publication/version fields differ; review versions manually")
        results.append({
            "key": key,
            "status": "unverified" if issues else "machine-compared; source unverified",
            "issues": issues,
            "original_type": source.type,
            "candidate_type": target.type,
            "original_fields": old_fields,
            "candidate_fields": new_fields,
            "differences": differences,
        })
    return {
        "original_count": len(original),
        "candidate_count": len(candidate),
        "unmatched_candidate_keys": sorted(set(candidate) - set(original)),
        "entries": results,
        "original_duplicate_flags": duplicate_flags(original),
        "candidate_duplicate_flags": duplicate_flags(candidate),
        "limitations": "Local same-key structural comparison and cross-key duplicate flags only; no source verification, TeX mapping, or claim support.",
    }


def resolved_fields(key, entries):
    try:
        return effective_fields(key, entries), None
    except InputError as error:
        return {name: value for name, value in entries[key].fields.items()
                if name in PUBLIC_FIELDS}, str(error)


def write_exclusive(path, payload, inputs):
    try:
        input_ids = {(source.stat().st_dev, source.stat().st_ino) for source in inputs}
        if path.exists() or path.is_symlink() or path.absolute() in [
            source.absolute() for source in inputs
        ]:
            raise InputError("output already exists or collides with an input")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise InputError("output already exists or collides with an input") from error
    except OSError as error:
        raise InputError("cannot create output") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            if (os.fstat(output.fileno()).st_dev, os.fstat(output.fileno()).st_ino) in input_ids:
                raise InputError("output collides with an input")
            if any((source.stat().st_dev, source.stat().st_ino) == (
                os.fstat(output.fileno()).st_dev, os.fstat(output.fileno()).st_ino
            ) for source in inputs):
                raise InputError("output collides with an input")
            output.write(payload)
    except (OSError, UnicodeError, InputError) as error:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        raise InputError("cannot write output safely") from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, help="exclusive new JSON file (default: stdout)")
    args = parser.parse_args(argv)
    try:
        original = load_entries(args.original)
        candidate = load_entries(args.candidate)
        report = compare_entries(original, candidate)
        report["input_provenance"] = {"original": source_stamp(args.original),
                                      "candidate": source_stamp(args.candidate)}
        payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output is not None:
            write_exclusive(args.output, payload, (args.original, args.candidate))
    except (InputError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 3 if isinstance(error, RuntimeError) else 2
    if args.output is None:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())

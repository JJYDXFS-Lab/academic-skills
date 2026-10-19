"""Conservative reachable-source citation inventory; never executes TeX."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from compare_candidates import InputError, load_entries, source_stamp


def strip_comments(line):
    return re.split(r"(?<!\\)%", line, maxsplit=1)[0]


CITATION = r"(?:nocite|(?:[Cc]ite|[Aa]utocite|[Pp]arencite|[Tt]extcite|[Ff]ootcite|[Ss]upercite|[Ss]martcite)\w*)"


def inventory(main, bib):
    entries = load_entries(bib)
    main = main.resolve()
    base = main.parent
    seen = set()
    locations = {}
    gaps = []
    nocite_all = False
    resources = []
    visited = []

    def walk(path):
        nonlocal nocite_all
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        if not path.is_file():
            gaps.append({"path": str(path), "reason": "missing reachable TeX input"})
            return
        visited.append(source_stamp(path))
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            gaps.append({"path": str(path), "reason": "unreadable TeX input"})
            return
        for number, original_line in enumerate(lines, 1):
            line = strip_comments(original_line)
            if re.search(r"\\(?:input|include|subfile|" + CITATION + r")\s*(?:\[[^]]*\])?\s*\{[^}]*$", line):
                gaps.append({"path": str(path), "line": number, "reason": "multiline/unresolved command"})
            for match in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", line):
                name = match.group(1).strip()
                if "\\" in name or "#" in name:
                    gaps.append({"path": str(path), "line": number, "reason": "macro-based input"})
                    continue
                child = base / name
                walk(child if child.suffix else child.with_suffix(".tex"))
            for match in re.finditer(r"\\(?:addbibresource(?:\[[^]]*\])?|bibliography)\s*\{([^}]+)\}", line):
                resources.extend(str(base / name.strip()) for name in match.group(1).split(",") if name.strip())
            for match in re.finditer(r"\\(" + CITATION + r")\s*(?:\[[^]]*\]\s*){0,2}\{([^}]+)\}", line):
                kind, value = match.groups()
                if line[match.end():].lstrip().startswith("{"):
                    gaps.append({"path": str(path), "line": number,
                                 "reason": "additional citation argument groups require manual review"})
                if "\\" in value or "#" in value:
                    gaps.append({"path": str(path), "line": number, "reason": "macro-based citation keys"})
                    continue
                if kind == "nocite" and value.strip() == "*":
                    nocite_all = True
                    continue
                for key in value.split(","):
                    key = key.strip()
                    if key:
                        locations.setdefault(key, []).append({"path": str(path), "line": number,
                                                               "kind": "nocite" if kind == "nocite" else "citation"})
    walk(main)
    included = set(locations)
    pending = list(included)
    while pending:
        key = pending.pop()
        if key in entries:
            for relation in ("crossref", "xdata"):
                for parent in entries[key].fields.get(relation, "").split(","):
                    parent = parent.strip()
                    if parent and parent not in included:
                        included.add(parent)
                        pending.append(parent)
    if nocite_all:
        included.update(entries)
    resolved_resources = {Path(name if Path(name).suffix else name + ".bib").resolve() for name in resources}
    if len(resolved_resources) > 1:
        gaps.append({"reason": "multiple Bib resources detected; only provided Bib was inventoried"})
    if resources and bib.resolve() not in resolved_resources:
        gaps.append({"reason": "provided Bib not matched to detected resources"})
    return {"sources": visited, "bib": source_stamp(bib), "locations": locations,
            "undefined": sorted(included - set(entries)), "unused": sorted(set(entries) - included),
            "nocite_all": nocite_all, "resources": resources, "gaps": gaps,
            "limitations": "Static reachable-source scan; macros, generated inputs, uncommon cite commands and dynamic Bib resources require manual review."}


def corroborate(report, path, main):
    if not path:
        return
    if not path.is_file() or any(path.stat().st_mtime_ns < stamp["mtime_ns"]
                                 for stamp in report["sources"] + [report["bib"]]):
        report["gaps"].append({"reason": "missing or stale auxiliary file; no corroboration"})
        return
    try:
        if path.suffix == ".aux":
            text = path.read_text(encoding="utf-8")
            keys = {key.strip() for group in re.findall(r"\\citation\{([^}]*)\}", text)
                    for key in group.split(",")}
        elif path.suffix == ".bcf":
            root = ET.parse(path).getroot()
            keys = {(item.text or "").strip() for item in root.iter() if item.tag.endswith("citekey")}
        else:
            raise InputError("auxiliary must be .aux or .bcf")
        report["aux_corroboration"] = {"source": source_stamp(path), "keys": sorted(keys),
                                        "aux_only": sorted(keys - set(report["locations"])),
                                        "note": "fresh auxiliary corroboration only; not source coverage"}
    except (OSError, UnicodeError, ET.ParseError):
        report["gaps"].append({"reason": "auxiliary file unreadable or invalid"})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main", type=Path)
    parser.add_argument("bib", type=Path)
    parser.add_argument("--aux", type=Path)
    args = parser.parse_args(argv)
    try:
        result = inventory(args.main, args.bib)
        corroborate(result, args.aux, args.main)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (InputError, RuntimeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

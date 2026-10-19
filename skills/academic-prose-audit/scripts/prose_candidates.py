"""Conservative, read-only TeX prose triage; not a TeX parser or an editor."""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


QUESTIONS = (
    (re.compile(r"\ba\s+lot\s+of\b", re.I), "Is this quantifier precise enough for this context?"),
    (re.compile(r"\byou\s+can\s+see\b", re.I), "Is the reader being asked to infer something unstated?"),
    (re.compile(r"\bneedless\s+to\s+say\b", re.I), "Does this preface add anything here?"),
    (re.compile(r"\blet's\b", re.I), "Is this conversational register intentional?"),
)

PROSE_ENVIRONMENTS = {"document", "abstract", "itemize", "enumerate", "description"}
COMMAND = re.compile(r"\\([A-Za-z@]+|[^\n])")
ENVIRONMENT = re.compile(r"\\(begin|end)\s*\{([^{}]+)\}")


class CoverageError(ValueError):
    def __init__(self, source, offset, reason):
        super().__init__(f"line {source.count(chr(10), 0, offset) + 1}: coverage failure: {reason}")


@dataclass
class ScanResult:
    visible: str
    skipped_arguments: int
    lettered_arguments: int


def group_end(source, start, opening, closing):
    depth = 0
    position = start
    while position < len(source):
        if source[position] == "\\":
            position = min(position + 2, len(source))
            continue
        if source[position] == "%":
            newline = source.find("\n", position)
            position = len(source) if newline == -1 else newline
            continue
        if source[position] == opening:
            depth += 1
        elif source[position] == closing:
            depth -= 1
            if depth == 0:
                return position + 1
        position += 1
    raise CoverageError(source, start, f"unclosed {opening} group")


def argument_end(source, start, skipped=None):
    position = start
    while position < len(source):
        probe = position
        while probe < len(source) and source[probe].isspace():
            probe += 1
        if probe >= len(source) or source[probe] not in "[{":
            break
        opening = source[probe]
        position = group_end(source, probe, opening, "]" if opening == "[" else "}")
        if skipped is not None:
            skipped.append(bool(re.search(r"[A-Za-z]", source[probe + 1:position - 1])))
    return position


def scan_prose(source):
    """Mask detectable protected text and count conservatively skipped arguments."""
    visible = list(source)
    position = 0
    environments = []
    math_close = None
    quote_close = None
    skipped = []

    def hide(start, end):
        for offset in range(start, end):
            if source[offset] != "\n":
                visible[offset] = " "

    while position < len(source):
        start = position
        character = source[position]
        if character == "%":
            position = source.find("\n", position)
            if position == -1:
                position = len(source)
        elif environments and environments[-1][0] not in PROSE_ENVIRONMENTS:
            marker = ENVIRONMENT.match(source, position) if character == "\\" else None
            if marker:
                name = marker.group(2)
                if marker.group(1) == "begin":
                    environments.append((name, position))
                elif environments[-1][0] == name:
                    environments.pop()
                else:
                    raise CoverageError(source, position, f"unexpected end of {name}")
                position = marker.end()
                position = argument_end(source, position)
            else:
                match = COMMAND.match(source, position) if character == "\\" else None
                position = match.end() if match else position + 1
        elif math_close is not None:
            if source.startswith(math_close, position):
                position += len(math_close)
                math_close = None
            elif character == "\\":
                position = min(position + 2, len(source))
            else:
                position += 1
        elif quote_close is not None:
            if source.startswith(quote_close, position):
                position += len(quote_close)
                quote_close = None
            elif character == "\\":
                position = min(position + 2, len(source))
            else:
                position += 1
        elif character == "\\":
            match = COMMAND.match(source, position)
            if not match:
                position += 1
            elif match.group(1) in ("(", "["):
                math_close = "\\)" if match.group(1) == "(" else "\\]"
                position = match.end()
            elif match.group(1) in ("begin", "end"):
                probe = match.end()
                while probe < len(source) and source[probe].isspace():
                    probe += 1
                if probe >= len(source) or source[probe] != "{":
                    raise CoverageError(source, start, "truncated environment marker")
                else:
                    end = group_end(source, probe, "{", "}")
                    name = source[probe + 1:end - 1]
                    if not name:
                        raise CoverageError(source, start, "empty environment name")
                    elif match.group(1) == "begin":
                        environments.append((name, start))
                        position = argument_end(source, end)
                    elif environments and environments[-1][0] == name:
                        environments.pop()
                        position = argument_end(source, end)
                    else:
                        raise CoverageError(source, start, f"unexpected end of {name}")
            elif match.group(1) == "verb":
                probe = match.end() + (source.startswith("*", match.end()))
                if probe >= len(source) or source[probe] == "\n":
                    raise CoverageError(source, start, "truncated verb delimiter")
                else:
                    end = source.find(source[probe], probe + 1)
                    line_end = source.find("\n", probe + 1)
                    if end == -1 or line_end != -1 and end > line_end:
                        raise CoverageError(source, start, "unclosed verb span")
                    position = end + 1
            else:
                position = argument_end(source, match.end(), skipped)
        elif character == "{":
            position = group_end(source, position, "{", "}")
        elif character == "$":
            math_close = "$$" if source.startswith("$$", position) else "$"
            position += len(math_close)
        elif source.startswith("``", position):
            quote_close = "''"
            position += 2
        elif character in ('"', '“'):
            quote_close = '”' if character == '“' else '"'
            position += 1
        else:
            position += 1
            continue
        hide(start, min(position, len(source)))

    if environments:
        raise CoverageError(source, environments[-1][1], f"unclosed environment {environments[-1][0]}")
    if math_close is not None:
        raise CoverageError(source, len(source), f"unclosed math span (expected {math_close})")
    if quote_close is not None:
        raise CoverageError(source, len(source), f"unclosed quotation (expected {quote_close})")
    return ScanResult("".join(visible), len(skipped), sum(skipped))


def visible_prose(source):
    return scan_prose(source).visible


def candidates(source, visible=None):
    if visible is None:
        visible = visible_prose(source)
    for pattern, question in QUESTIONS:
        for match in pattern.finditer(visible):
            if source[match.start():match.end()] != visible[match.start():match.end()]:
                continue
            line = source.count("\n", 0, match.start()) + 1
            line_start = visible.rfind("\n", 0, match.start()) + 1
            line_end = visible.find("\n", match.end())
            if line_end == -1:
                line_end = len(visible)
            context = " ".join(visible[max(line_start, match.start() - 65):min(line_end, match.end() + 65)].split())
            phrase = " ".join(source[match.start():match.end()].split())
            yield line, phrase, context, question


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only, non-exhaustive TeX prose candidate questions; stdout contains manuscript snippets (keep output private)")
    parser.add_argument("files", nargs="+", type=Path, help="explicitly authorized .tex files only")
    args = parser.parse_args(argv)
    prepared = []
    for path in args.files:
        if path.suffix.lower() != ".tex" or not path.is_file():
            parser.error(f"expected an existing .tex file: {path}")
        try:
            source = path.read_text(encoding="utf-8")
            scan = scan_prose(source)
        except (OSError, UnicodeError, CoverageError) as error:
            parser.error(f"{path}: {error}")
        prepared.append((path, source, scan))
    print("Privacy: stdout contains manuscript snippets; keep output local/private. "
          "Non-exhaustive heuristic triage, not TeX parsing or an authorship/claim verdict; "
          "check all context manually. Unsupported markup may be missed or skipped.", file=sys.stderr)
    for path, source, scan in prepared:
        print(f"{path}: skipped command arguments: {scan.skipped_arguments} "
              f"({scan.lettered_arguments} contain letters; includes citation keys/labels; "
              "not a measure of reviewed prose).", file=sys.stderr)
        for line, phrase, context, question in candidates(source, scan.visible):
            print(f"{path}:{line} | {phrase!r} | context: {context} | question: {question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

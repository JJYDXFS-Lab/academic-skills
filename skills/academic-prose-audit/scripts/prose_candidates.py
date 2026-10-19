"""Conservative, read-only prose candidate locator; not a full parser or audit."""

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
    (re.compile(r"\b(?:in conclusion|to summarize|overall,? (?:these|our) (?:results|findings))\b", re.I),
     "Does this ending add a specific inference in context?"),
    (re.compile(r"\b(?:in recent years|it is important to note that|this paper (?:aims to|explores))\b", re.I),
     "Does this opening establish a useful scope or merely frame the topic?"),
    (re.compile(r"\b(?:groundbreaking|revolutionary|transformative|unprecedented|remarkable)\b", re.I),
     "Is this adjective warranted by the stated evidence and disciplinary usage?"),
)

PROSE_ENVIRONMENTS = {"document", "abstract", "itemize", "enumerate", "description",
                      "figure", "figure*", "table", "table*", "theorem", "proof",
                      "remark", "minipage", "center"}
PROSE_COMMANDS = {"emph", "textit", "textbf", "footnote", "caption", "section", "subsection", "paragraph"}
COMMAND = re.compile(r"\\([A-Za-z@]+|[^\n])")
ENVIRONMENT = re.compile(r"\\(begin|end)\s*\{([^{}]+)\}")
SENTENCE = re.compile(r"[^.!?\n]+[.!?](?=\s|$)")
WORDS = re.compile(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b")


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
    braces = []

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
            elif match.group(1) in PROSE_COMMANDS:
                probe = match.end()
                if source.startswith("*", probe):
                    probe += 1
                while probe < len(source) and source[probe].isspace():
                    probe += 1
                if probe < len(source) and source[probe] == "[":
                    probe = group_end(source, probe, "[", "]")
                    while probe < len(source) and source[probe].isspace():
                        probe += 1
                if probe < len(source) and source[probe] == "{":
                    braces.append(probe)
                    position = probe + 1
                    hide(start, position)
                    continue
                position = probe
            else:
                position = argument_end(source, match.end(), skipped)
        elif character == "{":
            braces.append(position)
            position += 1
        elif character == "}":
            if not braces:
                raise CoverageError(source, position, "unexpected closing brace")
            braces.pop()
            position += 1
        elif character == "$":
            math_close = "$$" if source.startswith("$$", position) else "$"
            position += len(math_close)
        elif source.startswith("``", position):
            quote_close = "''"
            position += 2
        elif character in ('"', '“') and not (character == '"' and position > 0 and source[position - 1].isdigit()):
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
    if braces:
        raise CoverageError(source, braces[-1], "unclosed { group")
    return ScanResult("".join(visible), len(skipped), sum(skipped))


def visible_prose(source):
    return scan_prose(source).visible


def scan_markdown(source):
    """Conservatively mask Markdown syntax and quoted/code/link spans."""
    visible = list(source)

    def hide(start, end):
        for offset in range(start, end):
            if source[offset] != "\n":
                visible[offset] = " "

    position = 0
    while position < len(source):
        start = position
        line_start = source.rfind("\n", 0, position) + 1
        if position == line_start:
            line_end = source.find("\n", position)
            if line_end == -1:
                line_end = len(source)
            if re.match(r"\s{0,3}>", source[position:line_end]):
                hide(position, line_end)
                position = line_end
                continue
            fence = re.match(r"\s{0,3}(`{3,}|~{3,})", source[position:line_end])
            if fence:
                closing = re.search(r"(?m)^\s{0,3}" + re.escape(fence.group(1)[0]) +
                                    "{" + str(len(fence.group(1))) + r",}[ \t]*$", source[line_end:])
                if not closing:
                    raise CoverageError(source, start, "unclosed Markdown fence")
                position = line_end + closing.end()
                hide(start, position)
                continue
        character = source[position]
        if source.startswith("<!--", position):
            closing = source.find("-->", position + 4)
            if closing == -1:
                raise CoverageError(source, position, "unclosed Markdown HTML comment")
            position = closing + 3
        elif source.startswith("$$", position) or character == "$":
            delimiter = "$$" if source.startswith("$$", position) else "$"
            closing = source.find(delimiter, position + len(delimiter))
            if closing == -1:
                raise CoverageError(source, position, "unclosed Markdown math span")
            position = closing + len(delimiter)
        elif source.startswith("\\(", position) or source.startswith("\\[", position):
            delimiter = "\\)" if source.startswith("\\(", position) else "\\]"
            closing = source.find(delimiter, position + 2)
            if closing == -1:
                raise CoverageError(source, position, "unclosed Markdown math span")
            position = closing + 2
        elif character == "`":
            run = re.match(r"`+", source[position:]).group()
            closing = source.find(run, position + len(run))
            if closing == -1:
                raise CoverageError(source, position, "unclosed Markdown code span")
            position = closing + len(run)
        elif character == "[" or source.startswith("![", position):
            citation = (re.match(r"\[[^]\n]*-?@[A-Za-z0-9_:.\-/]+[^]\n]*\]", source[position:])
                        if character == "[" else None)
            link = re.match(r"!?\[[^]\n]*\]\([^\n)]*\)|!?\[[^]\n]*\]\[[^]\n]*\]", source[position:])
            if citation or link:
                position += len((citation or link).group())
            else:
                position += 1
                continue
        elif character == "@" and re.match(r"@[A-Za-z0-9_:.\-/]+", source[position:]):
            position += len(re.match(r"@[A-Za-z0-9_:.\-/]+", source[position:]).group())
        elif character in ('"', '“') and not (character == '"' and position > 0 and source[position - 1].isdigit()):
            closing_mark = '"' if character == '"' else '”'
            closing = source.find(closing_mark, position + 1)
            if closing == -1:
                raise CoverageError(source, position, "unclosed Markdown quotation")
            position = closing + 1
        else:
            position += 1
            continue
        hide(start, position)
    return ScanResult("".join(visible), 0, 0)


def candidates(source, visible=None):
    if visible is None:
        visible = visible_prose(source)
    def emit(start, end, question):
        line = source.count("\n", 0, start) + 1
        line_start = visible.rfind("\n", 0, start) + 1
        line_end = visible.find("\n", end)
        if line_end == -1:
            line_end = len(visible)
        context = " ".join(visible[max(line_start, start - 65):min(line_end, end + 65)].split())
        phrase = " ".join(visible[start:end].split())
        return line, phrase, context, question

    for pattern, question in QUESTIONS:
        for match in pattern.finditer(visible):
            if source[match.start():match.end()] != visible[match.start():match.end()]:
                continue
            yield emit(match.start(), match.end(), question)

    dashes = list(re.finditer(r"(?<!-)---(?!-)|—", visible))
    if dashes:
        locations = ", ".join(str(source.count("\n", 0, match.start()) + 1) for match in dashes[:12])
        for match in dashes[:12]:
            yield emit(match.start(), match.end(),
                       f"What does this interruption do? {len(dashes)} em dashes at lines {locations}"
                       + (" (first 12 shown)" if len(dashes) > 12 else "") + ".")

    for paragraph in re.finditer(r"[^\n]+(?:\n(?!\s*\n)[^\n]+)*", visible):
        text = paragraph.group()
        transitions = list(re.finditer(r"(?i)(?<!\w)(?:however|moreover|furthermore|additionally|in contrast|therefore)\b", text))
        by_word = {}
        for match in transitions:
            by_word.setdefault(match.group().lower(), []).append(paragraph.start() + match.start())
        for word, offsets in by_word.items():
            if len(offsets) > 1:
                for offset in offsets[:6]:
                    yield emit(offset, offset + len(word),
                               f"{len(offsets)} uses of '{word}' in this passage; are transitions doing distinct work?")

        openings = {}
        for sentence in SENTENCE.finditer(text):
            words = list(WORDS.finditer(sentence.group()))
            if len(words) >= 3:
                start = paragraph.start() + sentence.start() + words[0].start()
                opening = " ".join(word.group().lower() for word in words[:3])
                openings.setdefault(opening, []).append((start, words[2].end() - words[0].start()))
            if len(words) > 38:
                start = paragraph.start() + sentence.start() + words[0].start()
                yield emit(start, start + len(words[0].group()),
                           f"Approx. {len(words)} visible words in this sentence; is its structure easy to follow?")
        for opening, offsets in openings.items():
            if len(offsets) > 1:
                for offset, length in offsets[:6]:
                    yield emit(offset, offset + length,
                               f"{len(offsets)} sentences start '{opening}' in this passage; is repetition useful?")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only, non-exhaustive prose candidate questions; stdout contains manuscript snippets (keep output private)")
    parser.add_argument("files", nargs="+", type=Path, help="explicitly authorized UTF-8 .tex, .md or .txt files only")
    args = parser.parse_args(argv)
    prepared = []
    for path in args.files:
        if path.suffix.lower() not in (".tex", ".md", ".txt") or not path.is_file():
            parser.error(f"expected an existing .tex, .md or .txt file: {path}")
        try:
            source = path.read_text(encoding="utf-8")
            scan = scan_prose(source) if path.suffix.lower() == ".tex" else scan_markdown(source)
        except (OSError, UnicodeError, CoverageError) as error:
            parser.error(f"{path}: {error}")
        prepared.append((path, source, scan))
    print("Privacy: stdout contains manuscript snippets; keep output local/private. "
          "Non-exhaustive heuristic triage, not a full audit or an authorship/claim verdict; "
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

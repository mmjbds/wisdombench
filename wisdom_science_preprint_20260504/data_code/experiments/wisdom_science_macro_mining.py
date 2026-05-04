"""Mine repeated macros from the Wisdom Science paper/code corpus.

This is deliberately simple and dependency-free. It is not a semantic parser;
it is the first auditable pass for finding repeated language, formulas, and
framework terms that deserve a cleaner representation layer.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"

SOURCE_GLOBS = [
    "papers/*.tex",
    "papers/*.md",
    "papers/P*/main.tex",
    "papers/submission_CoRL2026/P*/main.tex",
    "sovereign_core/*.py",
    "engines/*.py",
    "skills/*.py",
]

EXCLUDE_PATH_PARTS = {
    "Finalizing NeurIPS Research Portfolio.md",
    "DeepSeek Architecture Integration Strategy.md",
    "__pycache__",
    "generated",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "our",
    "not",
    "can",
    "has",
    "have",
    "into",
    "in",
    "via",
    "which",
    "where",
    "when",
    "their",
    "than",
    "then",
    "only",
    "also",
}

NOISE_TOKENS = {
    "administrator",
    "append",
    "architect",
    "artifact",
    "answer",
    "autonomous",
    "building",
    "class",
    "command",
    "conn",
    "data_dir",
    "dataclass",
    "dataclasses",
    "datetime",
    "def",
    "default_factory",
    "dict",
    "does",
    "edited",
    "ensure_ascii",
    "environment",
    "except",
    "exception",
    "execute",
    "factory",
    "false",
    "file",
    "field",
    "getlogger",
    "grep",
    "human",
    "import",
    "importerror",
    "isinstance",
    "itemsep",
    "justification",
    "join",
    "leftmargin",
    "list",
    "logger",
    "logging",
    "main",
    "nonstopmode",
    "now",
    "optional",
    "os",
    "parts",
    "path",
    "pdflatex",
    "planner",
    "powershell",
    "query",
    "question",
    "realistic",
    "real-world",
    "resolve",
    "response",
    "return",
    "searched",
    "select",
    "self",
    "staticmethod",
    "string",
    "subjects",
    "swe-bench",
    "tex",
    "time",
    "true",
    "typing",
    "user",
    "windows",
}

SEED_TERMS = [
    "Wisdom Quotient",
    "Embodied Wisdom Quotient",
    "Second Scaling Law",
    "Cognitive Immunity",
    "WisdomBench",
    "WisdomBench-Embodied",
    "Evidence Gate",
    "Intelligence-Wisdom Gap",
    "Representation Genesis",
    "Embodied Failure Immunity",
    "Observer Depth",
    "Ouroboros",
    "Cognitive Entropy",
    "failure learning",
    "plasticity",
    "immunity",
    "homeostasis",
]


def iter_sources() -> list[Path]:
    files: set[Path] = set()
    for pattern in SOURCE_GLOBS:
        for path in ROOT.glob(pattern):
            if not path.is_file():
                continue
            rel = str(path.relative_to(ROOT))
            if any(part in rel for part in EXCLUDE_PATH_PARTS):
                continue
            files.add(path)
    return sorted(files)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")


def normalize_text(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?", " ", text)
    text = re.sub(r"[^A-Za-z0-9_\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def token_ngrams(tokens: list[str], n: int) -> Counter[str]:
    counts: Counter[str] = Counter()
    for i in range(0, len(tokens) - n + 1):
        gram = tokens[i : i + n]
        if any(token in STOPWORDS for token in gram):
            continue
        if sum(len(token) for token in gram) < 8:
            continue
        counts[" ".join(gram)] += 1
    return counts


def estimate_macro_gain(phrase: str, count: int) -> dict[str, float | int | str]:
    raw_len = len(phrase)
    symbol_len = max(3, math.ceil(math.log10(count + 1)) + 2)
    definition_cost = raw_len + symbol_len
    saved = count * max(0, raw_len - symbol_len)
    net_gain = saved - definition_cost
    return {
        "phrase": phrase,
        "count": count,
        "phrase_len": raw_len,
        "symbol_len": symbol_len,
        "definition_cost": definition_cost,
        "saved_chars": saved,
        "net_gain": net_gain,
    }


def is_noise_phrase(phrase: str) -> bool:
    tokens = set(phrase.split())
    if tokens & NOISE_TOKENS:
        return True
    if any(token.startswith("_") or token.endswith("_") for token in tokens):
        return True
    if "_" in phrase:
        return True
    if any(len(token) <= 1 for token in tokens):
        return True
    if re.search(r"\d", phrase) and not any(core in phrase for core in ("wq", "ewq", "p5", "p6", "p7")):
        return True
    return False


def mine() -> dict[str, object]:
    docs = {}
    document_frequency: defaultdict[str, int] = defaultdict(int)
    phrase_counts: Counter[str] = Counter()
    seed_counts: Counter[str] = Counter()

    for path in iter_sources():
        text = read_text(path)
        docs[str(path.relative_to(ROOT))] = len(text)
        lower = text.lower()
        for term in SEED_TERMS:
            count = lower.count(term.lower())
            if count:
                seed_counts[term] += count
                document_frequency[term] += 1

        normalized = normalize_text(text)
        tokens = [token for token in normalized.split() if token and token not in STOPWORDS]
        seen_in_doc: set[str] = set()
        for n in range(2, 6):
            local = token_ngrams(tokens, n)
            phrase_counts.update(local)
            seen_in_doc.update(local.keys())
        for phrase in seen_in_doc:
            document_frequency[phrase] += 1

    candidates = [
        estimate_macro_gain(phrase, count)
        for phrase, count in phrase_counts.items()
        if count >= 4 and document_frequency[phrase] >= 2 and not is_noise_phrase(phrase)
    ]
    candidates.sort(key=lambda item: (item["net_gain"], item["count"], item["phrase_len"]), reverse=True)

    seed_summary = [
        {
            "term": term,
            "count": count,
            "document_frequency": document_frequency.get(term, 0),
        }
        for term, count in seed_counts.most_common()
    ]

    return {
        "source_count": len(docs),
        "sources": docs,
        "seed_terms": seed_summary,
        "top_macro_candidates": candidates[:80],
    }


def write_markdown(result: dict[str, object], path: Path) -> None:
    lines = [
        "# Wisdom Science Macro Registry v0",
        "",
        f"Source files scanned: {result['source_count']}",
        "",
        "## Seed Terms",
        "",
        "| term | count | document_frequency |",
        "| --- | ---: | ---: |",
    ]
    for item in result["seed_terms"]:
        lines.append(f"| {item['term']} | {item['count']} | {item['document_frequency']} |")

    lines.extend(
        [
            "",
            "## Top Macro Candidates",
            "",
            "| phrase | count | net_gain |",
            "| --- | ---: | ---: |",
        ]
    )
    for item in result["top_macro_candidates"][:40]:
        phrase = str(item["phrase"]).replace("|", "/")
        lines.append(f"| {phrase} | {item['count']} | {item['net_gain']} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result = mine()
    json_path = RESULT_DIR / "macro_registry_v0.json"
    md_path = RESULT_DIR / "macro_registry_v0.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(result, md_path)
    print(f"scanned {result['source_count']} files")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()

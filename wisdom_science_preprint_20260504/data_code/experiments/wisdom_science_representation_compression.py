"""Deterministic representation-compression study for P8.

This experiment asks a narrow question: if Wisdom Science uses a canonical
macro language, how much repeated surface form can be compressed after paying
the glossary cost?
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"
P8_GEN = ROOT / "papers" / "P8_representation_genesis" / "generated"


MACROS = {
    "Wisdom Quotient": "WQ",
    "Embodied Wisdom Quotient": "EWQ",
    "Second Scaling Law": "SSL",
    "Cognitive Immunity": "CI",
    "WisdomBench-Embodied": "WB-E",
    "WisdomBench": "WB",
    "Intelligence-Wisdom Gap": "IWG",
    "Evidence Gate": "EG",
    "Representation Genesis": "RG",
    "Embodied Failure Immunity": "EFI",
    "Cognitive Entropy": "CE",
    "Observer Depth": "OD",
    "Cognitive Operating System": "COS",
}

SOURCE_FILES = [
    "papers/WISDOM_SCIENCE_MASTER_FRAMEWORK_20260504_CN.md",
    "papers/WISDOM_SCIENCE_CLAIM_REGISTRY_20260504_CN.md",
    "papers/WISDOM_SCIENCE_TERMS_V1_CN.md",
    "papers/ZENODO_REPO_ARTICLE_INVENTORY_20260504_CN.md",
    "papers/P8_representation_genesis/main.tex",
    "papers/P9_embodied_failure_immunity/main.tex",
    "papers/P2_wisdombench/main.tex",
    "papers/P3_intelligence_wisdom_gap/main.tex",
    "papers/P4_second_scaling_law/main.tex",
    "papers/submission_CoRL2026/P5/main.tex",
    "papers/submission_CoRL2026/P6/main.tex",
    "papers/submission_CoRL2026/P7/main.tex",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")


def byte_len(text: str) -> int:
    return len(text.encode("utf-8"))


def replace_case_insensitive(text: str, phrase: str, macro: str) -> tuple[str, int]:
    pattern = re.compile(re.escape(phrase), flags=re.IGNORECASE)
    return pattern.subn(macro, text)


def glossary_cost() -> int:
    return sum(byte_len(f"{macro}={phrase}\n") for phrase, macro in MACROS.items())


def compress_text(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    compressed = text
    for phrase, macro in sorted(MACROS.items(), key=lambda item: len(item[0]), reverse=True):
        compressed, count = replace_case_insensitive(compressed, phrase, macro)
        counts[phrase] = count
    return compressed, counts


def study() -> dict[str, object]:
    rows = []
    total_before = 0
    total_after = 0
    total_counts = {phrase: 0 for phrase in MACROS}
    for rel in SOURCE_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = read_text(path)
        compressed, counts = compress_text(text)
        before = byte_len(text)
        after = byte_len(compressed)
        total_before += before
        total_after += after
        for phrase, count in counts.items():
            total_counts[phrase] += count
        rows.append(
            {
                "source": rel,
                "before_bytes": before,
                "after_bytes": after,
                "raw_gain": before - after,
                "replacement_count": sum(counts.values()),
            }
        )

    g_cost = glossary_cost()
    packed_total = total_after + g_cost
    return {
        "macro_count": len(MACROS),
        "source_count": len(rows),
        "glossary_cost": g_cost,
        "before_bytes": total_before,
        "after_bytes": total_after,
        "packed_total": packed_total,
        "raw_gain": total_before - total_after,
        "net_gain": total_before - packed_total,
        "compression_ratio": total_before / max(packed_total, 1),
        "macro_counts": total_counts,
        "sources": rows,
    }


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def write_macro_counts_table(result: dict[str, object]) -> Path:
    counts = result["macro_counts"]
    rows = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10]
    lines = [
        r"\begin{tabular}{llr}",
        r"\toprule",
        r"Macro & Long form & Count \\",
        r"\midrule",
    ]
    reverse = {macro: phrase for phrase, macro in MACROS.items()}
    for phrase, count in rows:
        macro = MACROS[phrase]
        lines.append(f"{tex_escape(macro)} & {tex_escape(reverse[macro])} & {count} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P8_GEN / "representation_compression_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_markdown(result: dict[str, object]) -> None:
    lines = [
        "# Representation Compression Study v0",
        "",
        f"Macro count: {result['macro_count']}",
        f"Source count: {result['source_count']}",
        f"Before bytes: {result['before_bytes']}",
        f"After bytes: {result['after_bytes']}",
        f"Glossary cost: {result['glossary_cost']}",
        f"Packed total: {result['packed_total']}",
        f"Net gain: {result['net_gain']}",
        f"Compression ratio: {result['compression_ratio']:.4f}",
        "",
        "## Macro Counts",
        "",
        "| macro | long form | count |",
        "| --- | --- | ---: |",
    ]
    for phrase, count in sorted(result["macro_counts"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {MACROS[phrase]} | {phrase} | {count} |")
    lines.append("")
    (RESULT_DIR / "representation_compression_v0.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    P8_GEN.mkdir(parents=True, exist_ok=True)
    result = study()
    (RESULT_DIR / "representation_compression_v0.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(result)
    table = write_macro_counts_table(result)
    print(json.dumps({k: result[k] for k in ("source_count", "net_gain", "compression_ratio")}, indent=2))
    print(table.relative_to(ROOT))


if __name__ == "__main__":
    main()

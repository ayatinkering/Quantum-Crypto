"""Simple cryptographic inventory scanner.

Crypto inventory is the first practical step in a PQC migration. The scanner
looks for cryptographic algorithm names and protocol terms in source files, then
classifies each match by migration relevance.
"""

from __future__ import annotations

import re
from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKIPPED_DIRECTORIES = {".git", ".venv", "__pycache__", ".ipynb_checkpoints"}
SCANNED_SUFFIXES = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini"}


@dataclass(frozen=True)
class Finding:
    file: Path
    line_number: int
    term: str
    category: str
    recommendation: str
    line: str


PATTERNS: list[tuple[str, str, str]] = [
    ("RSA", "quantum-vulnerable public key", "Replace or hybridize with ML-KEM/ML-DSA."),
    ("ECDSA", "quantum-vulnerable signature", "Plan migration to ML-DSA or SLH-DSA."),
    ("ECDH", "quantum-vulnerable key exchange", "Plan migration to ML-KEM or hybrid exchange."),
    ("X25519", "classical key exchange", "Use hybrid X25519 + ML-KEM during migration."),
    ("Ed25519", "quantum-vulnerable signature", "Plan migration to ML-DSA or SLH-DSA."),
    ("DSA", "quantum-vulnerable signature", "Plan migration to ML-DSA or SLH-DSA."),
    ("ML-KEM", "post-quantum key exchange", "Preferred NIST-standardized KEM for PQC migration."),
    ("MLKEM", "post-quantum key exchange", "Preferred NIST-standardized KEM for PQC migration."),
    ("ML-DSA", "post-quantum signature", "Preferred NIST-standardized signature option."),
    ("MLDSA", "post-quantum signature", "Preferred NIST-standardized signature option."),
    ("SLH-DSA", "post-quantum signature", "Hash-based signature option for conservative designs."),
    ("AES-128", "symmetric encryption", "Prefer AES-256 for larger quantum security margin."),
    ("AES-256", "symmetric encryption", "Acceptable symmetric choice for quantum-safe designs."),
    ("AESGCM", "symmetric encryption", "Check key size; prefer 256-bit keys."),
    ("SHA1", "deprecated hash", "Replace with SHA-256, SHA-384, or SHA-512."),
    ("MD5", "deprecated hash", "Replace with SHA-256, SHA-384, or SHA-512."),
    ("SHA256", "hash", "Generally acceptable; assess required security level."),
    ("SHA-256", "hash", "Generally acceptable; assess required security level."),
    ("SHA-384", "hash", "Useful for higher security-level designs."),
    ("SHA-512", "hash", "Useful for higher security-level designs."),
]


def should_scan(path: Path) -> bool:
    """Return True when the path is a source-like file worth scanning."""
    if any(part in SKIPPED_DIRECTORIES for part in path.parts):
        return False
    return path.suffix.lower() in SCANNED_SUFFIXES


def scan_file(path: Path) -> list[Finding]:
    """Scan one file for cryptographic terms."""
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8", errors="ignore")

    for line_number, line in enumerate(text.splitlines(), start=1):
        for term, category, recommendation in PATTERNS:
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(
                    Finding(
                        file=path.relative_to(REPO_ROOT),
                        line_number=line_number,
                        term=term,
                        category=category,
                        recommendation=recommendation,
                        line=line.strip(),
                    )
                )

    return findings


def scan_repository() -> list[Finding]:
    """Scan the repository for cryptographic inventory findings."""
    findings: list[Finding] = []

    for path in sorted(REPO_ROOT.rglob("*")):
        if path.is_file() and should_scan(path):
            findings.extend(scan_file(path))

    return findings


def print_report(findings: list[Finding], show_all: bool = False, limit: int = 30) -> None:
    """Print a compact inventory report grouped by finding order."""
    print("Cryptographic inventory scan")
    print(f"Repository: {REPO_ROOT}")
    print(f"Findings: {len(findings)}")

    if not findings:
        print("No cryptographic terms found.")
        return

    print("\nFindings by category:")
    for category, count in Counter(f.category for f in findings).most_common():
        print(f"- {category}: {count}")

    displayed_findings = findings if show_all else findings[:limit]
    print(f"\nDetailed findings shown: {len(displayed_findings)}")
    if not show_all and len(findings) > limit:
        print("Run with --all to print every finding.")

    for finding in displayed_findings:
        print()
        print(f"{finding.file}:{finding.line_number}")
        print(f"Term: {finding.term}")
        print(f"Category: {finding.category}")
        print(f"Recommendation: {finding.recommendation}")
        print(f"Line: {finding.line}")


def main() -> None:
    parser = ArgumentParser(description="Scan repository files for cryptographic terms.")
    parser.add_argument("--all", action="store_true", help="print every finding")
    parser.add_argument("--limit", type=int, default=30, help="number of detailed findings to print")
    args = parser.parse_args()

    findings = scan_repository()
    print_report(findings, show_all=args.all, limit=args.limit)


if __name__ == "__main__":
    main()

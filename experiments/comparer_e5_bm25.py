"""Compare BM25 et E5 sur le lot de développement RGPH."""

import re
import sys
from pathlib import Path
from statistics import median
from timeit import repeat

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.search import build_e5_ranker
from experiments.bm25_rgph import DATA_DIR, build_index, load_development_claims, rank_passages

TIMING_REPEATS = 21


def main():
    mini = (DATA_DIR / "mini-corpus-rgph.md").read_text(encoding="utf-8")
    corpus = (DATA_DIR / "corpus-rgph.md").read_text(encoding="utf-8")
    passages = re.findall(r"^\| (P\d+) \| ([^|]+) \|", corpus, re.MULTILINE)
    claims = load_development_claims(mini)
    if not passages or not claims:
        raise ValueError("Le corpus et le lot de développement doivent être renseignés.")
    index = build_index(passages)

    rank_e5 = build_e5_ranker(passages)

    print("| Cas | Méthode | Top 3 | Rangs des preuves | Temps médian (ms) |")
    print("| --- | --- | --- | --- | ---: |")
    for claim_id, (claim, evidence) in claims.items():
        methods = (("BM25", lambda: rank_passages(claim, *index)), ("E5", lambda: rank_e5(claim)))
        for name, rank in methods:
            ranking = rank()
            ranks = {pid: position for position, (pid, _) in enumerate(ranking, start=1)}
            top = ", ".join(pid for pid, _ in ranking[:3])
            evidence_ranks = ", ".join(f"{pid} ({ranks[pid]})" for pid in evidence)
            milliseconds = median(repeat(rank, repeat=TIMING_REPEATS, number=1)) * 1000
            print(f"| {claim_id} | {name} | {top} | {evidence_ranks or '—'} | {milliseconds:.3f} |")


if __name__ == "__main__":
    main()

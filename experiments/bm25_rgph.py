"""Classe les passages RGPH avec BM25."""

import argparse
import math
import re
from collections import Counter
from pathlib import Path
from statistics import median
from timeit import repeat


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TIMING_REPEATS = 101


def tokenize(text):
    return re.findall(r"[^\W_]+", text.casefold())


def load_development_claims(mini_corpus):
    annotations = (DATA_DIR / "annotations-rgph.md").read_text(encoding="utf-8")
    cases = {}
    for line in mini_corpus.splitlines() + annotations.splitlines():
        columns = [cell.strip() for cell in line.strip("|").split("|")]
        if re.fullmatch(r"T\d+", columns[0]):
            columns = columns[1:]
        if re.fullmatch(r"A\d+", columns[0]):
            claim_id, claim, _, evidence = columns[:4]
            # Le mini-corpus place l’identifiant avant l’extrait cité.
            evidence_ids = re.match(r"P\d+(?:, P\d+)*", evidence)
            cases[claim_id] = (claim, evidence_ids[0].split(", ") if evidence_ids else [])

    development_ids = []
    for row in re.findall(r"^\| Développement \| [^|]+ \| (A[^|]+) \|$", annotations, re.MULTILINE):
        development_ids.extend(row.split(", "))
    return {claim_id: cases[claim_id] for claim_id in development_ids}


def rank_passages(claim, frequencies, lengths, average_length, document_frequency):
    k1, b = 1.2, 0.75
    query_terms = dict.fromkeys(tokenize(claim))
    scores = {}
    for pid, terms in frequencies.items():
        length_factor = k1 * (1 - b + b * lengths[pid] / average_length)
        score = 0.0
        for term in query_terms:
            frequency = terms[term]
            df = document_frequency[term]
            idf = math.log1p((len(frequencies) - df + 0.5) / (df + 0.5))
            score += idf * frequency * (k1 + 1) / (frequency + length_factor)
        scores[pid] = score
    return sorted(scores.items(), key=lambda result: (-result[1], result[0]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true", help="Évalue le corpus élargi sur le lot de développement.")
    args = parser.parse_args()

    mini_corpus = (DATA_DIR / "mini-corpus-rgph.md").read_text(encoding="utf-8")
    if args.development:
        corpus = (DATA_DIR / "corpus-rgph.md").read_text(encoding="utf-8")
        claims = load_development_claims(mini_corpus)
    else:
        corpus = mini_corpus
        claims = {
            claim_id: (claim, [])
            for claim_id, claim in re.findall(r"^\| (A\d+) \| ([^|]+) \|", corpus, re.MULTILINE)
        }
    passages = re.findall(r"^\| (P\d+) \| ([^|]+) \|", corpus, re.MULTILINE)
    if not passages or not claims:
        raise ValueError("Le corpus doit contenir des passages et des affirmations.")

    frequencies = {pid: Counter(tokenize(text)) for pid, text in passages}
    lengths = {pid: sum(terms.values()) for pid, terms in frequencies.items()}
    average_length = sum(lengths.values()) / len(passages)
    document_frequency = Counter(term for terms in frequencies.values() for term in terms)

    for claim_id, (claim, evidence) in claims.items():
        ranking = rank_passages(claim, frequencies, lengths, average_length, document_frequency)

        print(claim_id)
        for rank, (pid, score) in enumerate(ranking, start=1):
            print(f"  {rank}. {pid}  {score:.3f}")
        if args.development:
            ranks = {pid: rank for rank, (pid, _) in enumerate(ranking, start=1)}
            evidence_ranks = ", ".join(f"{pid} au rang {ranks[pid]}" for pid in evidence)
            durations = repeat(
                lambda: rank_passages(claim, frequencies, lengths, average_length, document_frequency),
                repeat=TIMING_REPEATS,
                number=1,
            )
            print(f"  Preuves attendues : {evidence_ranks or 'aucune'}")
            print(f"  Recherche médiane : {median(durations) * 1000:.3f} ms")


if __name__ == "__main__":
    main()

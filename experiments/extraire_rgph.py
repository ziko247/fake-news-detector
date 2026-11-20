"""Extrait des affirmations chiffrées et mesure leur repérage sur le RGPH."""

import argparse
import re
import sys
from pathlib import Path


if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.extraction import extract_claims


ANNOTATIONS = Path(__file__).resolve().parents[1] / "data" / "annotations-rgph.md"


def evaluate_development():
    annotations = ANNOTATIONS.read_text(encoding="utf-8")
    development_texts = re.findall(r"^\| Développement \| (T\d+) \|", annotations, re.MULTILINE)
    texts = dict(re.findall(r"^### (T\d+)[^\n]*\n\n> ([^\n]+)", annotations, re.MULTILINE))
    references = re.findall(
        r"^\| (T\d+) \| (A\d+) \| ([^|]+?) \|", annotations, re.MULTILINE
    )

    correct = predicted = expected = 0
    for text_id in development_texts:
        gold = {sentence: claim_id for doc, claim_id, sentence in references if doc == text_id}
        candidates = extract_claims(texts[text_id])
        matches = sum(sentence in gold for sentence in candidates)
        correct += matches
        predicted += len(candidates)
        expected += len(gold)
        print(f"{text_id} — {matches}/{len(gold)} attendues, {len(candidates)} extraites")
        for sentence in candidates:
            print(f"  {gold.get(sentence, 'AJOUT')} | {sentence}")
        for sentence, claim_id in gold.items():
            if sentence not in candidates:
                print(f"  OMISSION {claim_id} | {sentence}")

    print(f"Précision : {correct}/{predicted}")
    print(f"Rappel : {correct}/{expected}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("texte", type=Path, nargs="?", help="Fichier texte UTF-8 à analyser.")
    args = parser.parse_args()
    if args.texte:
        for claim in extract_claims(args.texte.read_text(encoding="utf-8-sig")):
            print(claim)
    else:
        evaluate_development()


if __name__ == "__main__":
    main()

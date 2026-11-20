"""Exécute le parcours RGPH sur un fichier texte et imprime les résultats JSON."""

import argparse
import json
from pathlib import Path

from app.analysis import build_article_analyzer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("texte", type=Path, help="Fichier texte UTF-8 à analyser.")
    args = parser.parse_args()
    article = args.texte.read_text(encoding="utf-8-sig")
    if not article.strip():
        parser.error("Le texte est vide.")

    analyze = build_article_analyzer()
    print(json.dumps(analyze(article), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Repère les phrases candidates à vérifier."""

import re

OPINION_START = re.compile(r"^(?:à mon avis|selon moi|je pense|je trouve)\b", re.IGNORECASE)


def extract_claims(text):
    """Retourne les phrases candidates telles qu’elles figurent dans le texte."""
    sentences = re.split(r"(?<=[.!?…])\s+|\n\s*\n", text.strip())
    return [
        sentence
        for sentence in sentences
        if re.search(r"\d", sentence)
        and not sentence.endswith("?")
        and not OPINION_START.match(sentence)
    ]

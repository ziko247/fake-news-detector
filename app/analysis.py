"""Analyse les affirmations à partir du corpus RGPH."""

import re
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from pathlib import Path

from .extraction import extract_claims
from .verdict import EvidenceAssessment, Relation, decide_status

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

COUNT = r"(?P<value>\d{1,3}(?: \d{3})+|\d+)"
DATE = r"(?P<period>1er septembre \d{4})"
YEAR = r"(?P<period>\d{4})"
RATE = r"(?P<value>\d+(?:[,.]\d+)?)"
URBAN = rf"le taux d[’']urbanisation du maroc était de {RATE} % en {YEAR}\."

CLAIM_PATTERNS = {
    "population": rf"au {DATE}, le maroc comptait {COUNT} habitants\.",
    "ménages": rf"en {YEAR}, le maroc comptait {COUNT} ménages\.",
    "urbanisation": URBAN,
}
PASSAGE_PATTERNS = {
    "P01": ("population", rf"le recensement de \d{{4}} a établi la population légale du maroc à {COUNT} habitants au {DATE}\."),
    "P11": ("urbanisation", URBAN),
    "P12": ("urbanisation", URBAN),
    "P15": ("ménages", CLAIM_PATTERNS["ménages"]),
}


@dataclass(frozen=True)
class Fact:
    indicator: str
    period: str
    value: Decimal


@dataclass(frozen=True)
class Passage:
    text: str
    url: str
    fact: Fact | None


def read_fact(text, patterns):
    normalized = " ".join(text.casefold().split())
    for indicator, pattern in patterns:
        match = re.fullmatch(pattern, normalized)
        if match:
            value = Decimal(match["value"].replace(" ", "").replace(",", "."))
            return Fact(indicator, match["period"], value)
    return None


def load_passages():
    corpus = (DATA_DIR / "corpus-rgph.md").read_text(encoding="utf-8")
    urls = dict(re.findall(r"^\| (S\d+) \| \[[^\]]+\]\((https://[^)]+)\)", corpus, re.MULTILINE))
    passages = {}
    for pid, text, source in re.findall(r"^\| (P\d+) \| (.+?) \| [^|]+ \| (S\d+) \|$", corpus, re.MULTILINE):
        patterns = [PASSAGE_PATTERNS[pid]] if pid in PASSAGE_PATTERNS else []
        passages[pid] = Passage(text, urls[source], read_fact(text, patterns))
    if not passages:
        raise ValueError("Le corpus RGPH ne contient aucun passage.")
    return passages


def analyze_article(text, passages, rank_passages):
    results = []
    for sentence in extract_claims(text):
        claim = read_fact(sentence, CLAIM_PATTERNS.items())
        assessments = []
        proofs = []
        candidates = []
        for pid, _ in rank_passages(sentence)[:3]:
            passage = passages[pid]
            candidate = {"id": pid, "extrait": passage.text, "url": passage.url}
            candidates.append(candidate)
            fact = passage.fact
            if claim is None or fact is None:
                continue
            if (claim.indicator, claim.period) != (fact.indicator, fact.period):
                continue
            relation = Relation.SUPPORTS if claim.value == fact.value else Relation.CONTRADICTS
            assessments.append(EvidenceAssessment(relation, same_scope=True, sufficient=True))
            proofs.append({**candidate, "relation": relation})

        decision = decide_status(True, assessments)
        reason = decision.reason
        if claim is None:
            reason = "La formulation ou l’indicateur dépasse les contrôles de ce prototype."
        elif not proofs:
            reason = f"Les passages consultés ne donnent pas la valeur de cet indicateur pour la période « {claim.period} »."
        results.append({
            "affirmation": sentence,
            "statut": decision.status,
            "explication": reason,
            "preuves": proofs,
            "passages_consultes": candidates,
        })
    return results



def build_article_analyzer():
    from .search import build_e5_ranker

    passages = load_passages()
    rank = build_e5_ranker([(pid, passage.text) for pid, passage in passages.items()])
    return partial(analyze_article, passages=passages, rank_passages=rank)

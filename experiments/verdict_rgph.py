"""Attribue un statut à partir de preuves dont le contenu a été vérifié."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class Relation(StrEnum):
    SUPPORTS = "appui"
    CONTRADICTS = "contradiction"
    NEUTRAL = "neutre"


class Status(StrEnum):
    SUPPORTED = "Appuyée par les sources"
    CONTRADICTED = "Contredite"
    UNVERIFIED = "Non vérifiée"
    INSUFFICIENT = "Insuffisamment documentée"


@dataclass(frozen=True)
class EvidenceAssessment:
    """Évaluation d’un passage ou d’un ensemble de passages complémentaires."""

    relation: Relation
    same_scope: bool
    sufficient: bool


@dataclass(frozen=True)
class Decision:
    status: Status
    reason: str


def decide_status(verification_completed: bool, evidence: Iterable[EvidenceAssessment]) -> Decision:
    if not verification_completed:
        return Decision(Status.UNVERIFIED, "La vérification reste à terminer.")

    decisive_relations = {
        item.relation for item in evidence if item.same_scope and item.sufficient
    }
    supports = Relation.SUPPORTS in decisive_relations
    contradicts = Relation.CONTRADICTS in decisive_relations

    if supports and contradicts:
        return Decision(Status.INSUFFICIENT, "Les preuves appuient des conclusions divergentes.")
    if contradicts:
        return Decision(Status.CONTRADICTED, "Une preuve contredit un élément nécessaire de l’affirmation.")
    if supports:
        return Decision(Status.SUPPORTED, "Les preuves appuient les éléments nécessaires de l’affirmation.")
    return Decision(Status.INSUFFICIENT, "Les preuves examinées ne suffisent pas pour conclure.")

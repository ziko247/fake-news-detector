from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

from .verdict import Relation, Status


class AnalysisRequest(BaseModel):
    texte: str = Field(strict=True, min_length=1, max_length=12_000, description="Texte à analyser.")

    @field_validator("texte")
    @classmethod
    def reject_blank_text(cls, text: str) -> str:
        if not text.strip():
            raise ValueError("Le texte est vide.")
        return text


class PassageResponse(BaseModel):
    id: str
    extrait: str
    url: str


class EvidenceResponse(PassageResponse):
    relation: Relation


class ClaimResponse(BaseModel):
    affirmation: str
    statut: Status
    explication: str
    preuves: list[EvidenceResponse]
    passages_consultes: list[PassageResponse]


class AnalysisResponse(BaseModel):
    affirmations: list[ClaimResponse]


class ErrorResponse(BaseModel):
    detail: str


class NewsArticle(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    source: str | None = None
    published_at: str | None = None
    url: AnyHttpUrl


class NewsResponse(BaseModel):
    articles: list[NewsArticle]

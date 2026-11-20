"""API HTTP du prototype RGPH."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from .analysis import build_article_analyzer
from .verdict import Relation, Status

logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield {"analyze": build_article_analyzer()}


app = FastAPI(
    title="Vérification des affirmations RGPH",
    description="Recherche et vérification d’affirmations dans le corpus du HCP.",
    lifespan=lifespan,
)


@app.post(
    "/analyses",
    response_model=AnalysisResponse,
    summary="Analyser un texte",
    responses={500: {"model": ErrorResponse, "description": "Erreur pendant l’analyse."}},
)
def create_analysis(payload: AnalysisRequest, request: Request):
    try:
        results = request.state.analyze(payload.texte)
    except Exception as error:
        logger.error("Échec de l’analyse RGPH (%s).", type(error).__name__)
        raise HTTPException(status_code=500, detail="L’analyse a échoué.") from error
    return {"affirmations": results}

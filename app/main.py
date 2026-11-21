"""API HTTP du prototype RGPH."""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from http.client import HTTPException as TransportError
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request

from .analysis import build_article_analyzer
from .mediastack import NewsError, search_news
from .schemas import AnalysisRequest, AnalysisResponse, ErrorResponse, NewsResponse
from .storage import initialize, save_analysis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    path = Path(os.environ.get("RGPH_DB_PATH", Path(__file__).resolve().parents[1] / "data" / "history.sqlite3"))
    initialize(path)
    yield {"analyze": build_article_analyzer(), "db_path": path}


app = FastAPI(
    title="Vérification des chiffres du Maroc",
    description="Vérification d’affirmations sur le recensement, le chômage et l’inflation dans les publications du HCP.",
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
        response = AnalysisResponse(affirmations=request.state.analyze(payload.texte))
        save_analysis(request.state.db_path, payload.texte, response)
    except Exception as error:
        logger.error("Échec de l’analyse RGPH (%s).", type(error).__name__)
        raise HTTPException(status_code=500, detail="L’analyse a échoué.") from error
    return response


@app.get(
    "/actualites",
    summary="Chercher des articles en français",
    responses={code: {"model": ErrorResponse} for code in (429, 502, 503)},
)
def get_news(q: Annotated[str, Query(max_length=100)] = "") -> NewsResponse:
    api_key = os.environ.get("MEDIASTACK_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(503, "La clé Mediastack n’est pas configurée sur le serveur.")
    try:
        return search_news(api_key, q.strip())
    except NewsError as error:
        raise HTTPException(error.status_code, str(error)) from None
    except (OSError, TransportError, ValueError):
        raise HTTPException(502, "La recherche Mediastack est temporairement indisponible.") from None

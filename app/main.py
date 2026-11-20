"""API HTTP du prototype RGPH."""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from .schemas import AnalysisRequest, AnalysisResponse, ErrorResponse

from .analysis import build_article_analyzer
from .storage import initialize, save_analysis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    path = Path(os.environ.get("RGPH_DB_PATH", Path(__file__).resolve().parents[1] / "data" / "history.sqlite3"))
    initialize(path)
    yield {"analyze": build_article_analyzer(), "db_path": path}


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
        response = AnalysisResponse(affirmations=request.state.analyze(payload.texte))
        save_analysis(request.state.db_path, payload.texte, response)
    except Exception as error:
        logger.error("Échec de l’analyse RGPH (%s).", type(error).__name__)
        raise HTTPException(status_code=500, detail="L’analyse a échoué.") from error
    return response

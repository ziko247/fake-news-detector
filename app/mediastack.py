"""Recherche d’articles publiés par des médias indexés par Mediastack."""

import json
from contextlib import closing
from http.client import HTTPException as TransportError, HTTPSConnection
from urllib.parse import urlencode

from pydantic import ValidationError

from .schemas import NewsArticle, NewsResponse


def search_news(api_key: str, keywords: str) -> NewsResponse:
    params = {"access_key": api_key, "languages": "fr", "limit": 8, "keywords": keywords or "Maroc"}
    with closing(HTTPSConnection("api.apilayer.net", timeout=10)) as connection:
        connection.request("GET", f"/mediastack/v1/news?{urlencode(params)}")
        with connection.getresponse() as response:
            # Le fournisseur peut inclure le détail de sa requête dans ses erreurs.
            if response.status == 429:
                raise NewsError(429, "Le quota de recherche Mediastack est atteint.")
            if response.status == 401:
                raise NewsError(503, "Mediastack a refusé la clé configurée sur le serveur.")
            if response.status != 200:
                raise NewsError(502, "Mediastack a refusé la recherche ou est indisponible.")
            data = json.load(response)

    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise NewsError(502, "Mediastack n’a pas fourni de liste d’articles.")

    articles = []
    for item in data["data"][:8]:
        try:
            articles.append(NewsArticle.model_validate(item))
        except ValidationError:
            continue
    if data["data"] and not articles:
        raise NewsError(502, "Les articles fournis par Mediastack sont illisibles.")
    return NewsResponse(articles=articles)


class NewsError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code

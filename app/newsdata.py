"""Recherche d’articles en français avec NewsData.io."""

import json
from contextlib import closing
from http.client import HTTPSConnection
from urllib.parse import urlencode

from pydantic import ValidationError

from .schemas import NewsArticle, NewsResponse


def search_news(api_key: str, keywords: str) -> NewsResponse:
    params = {"apikey": api_key, "country": "ma", "language": "fr", "size": 8}
    if keywords:
        params["q"] = keywords
    with closing(HTTPSConnection("newsdata.io", timeout=10)) as connection:
        connection.request("GET", f"/api/1/latest?{urlencode(params)}")
        with connection.getresponse() as response:
            # Le fournisseur peut inclure le détail de sa requête dans ses erreurs.
            if response.status == 429:
                raise NewsError(429, "La limite de requêtes NewsData.io est atteinte.")
            if response.status == 401:
                raise NewsError(503, "NewsData.io a refusé la clé configurée sur le serveur.")
            if response.status != 200:
                raise NewsError(502, "NewsData.io a refusé la recherche ou est indisponible.")
            data = json.load(response)

    if not isinstance(data, dict) or data.get("status") != "success" or not isinstance(data.get("results"), list):
        raise NewsError(502, "NewsData.io n’a pas fourni de liste d’articles.")

    articles = []
    for item in data["results"][:8]:
        if not isinstance(item, dict):
            continue
        try:
            articles.append(NewsArticle(
                title=item.get("title"),
                description=item.get("description"),
                source=item.get("source_name") or item.get("source_id"),
                published_at=item.get("pubDate"),
                url=item.get("link"),
            ))
        except ValidationError:
            continue
    if data["results"] and not articles:
        raise NewsError(502, "Les articles fournis par NewsData.io sont illisibles.")
    return NewsResponse(articles=articles)


class NewsError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code

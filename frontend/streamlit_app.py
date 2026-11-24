"""Interface de vérification des chiffres du HCP."""

import os
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

from app.schemas import AnalysisRequest, AnalysisResponse, NewsResponse

st.set_page_config(page_title="Vérifier un article · Maroc", layout="centered")
st.html(Path(__file__).with_name("style.css"))
st.title("Vérifier les chiffres du Maroc")
st.write("Comparez les chiffres d’un article aux publications du HCP sur le recensement, le chômage et l’inflation.")
article_key = "article_text"
endpoint = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
demo_files = {
    "Recensement": "demo-rgph.txt",
    "Chômage et inflation": "demo-economie.txt",
}
demo = st.selectbox("Thème de la démonstration", demo_files)
if st.button("Charger l’article de démonstration"):
    demo_path = Path(__file__).resolve().parents[1] / "data" / demo_files[demo]
    st.session_state[article_key] = demo_path.read_text(encoding="utf-8")
    st.session_state.pop("analysis", None)
with st.form("article", border=True):
    text = st.text_area(
        "Texte de l’article", height=200, key=article_key, max_chars=12_000,
        placeholder="Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants.",
        help="Le prototype vérifie certaines formulations chiffrées, dont les taux annuels de chômage et d’inflation.",
    )
    st.caption("Le texte et les résultats sont enregistrés dans la base locale du serveur.")
    submitted = st.form_submit_button("Analyser le texte", type="primary")

if submitted:
    st.session_state.pop("analysis", None)
    if not text.strip():
        st.warning("Collez un article avant de lancer l’analyse.")
    else:
        try:
            payload = AnalysisRequest(texte=text).model_dump_json().encode("utf-8")
            request = Request(f"{endpoint}/analyses", data=payload, headers={"Content-Type": "application/json"})
            with st.spinner("Recherche dans les publications du HCP…"), urlopen(request, timeout=60) as reply:
                st.session_state.analysis = AnalysisResponse.model_validate_json(reply.read())
        except HTTPError as error:
            if error.code == 422:
                st.error("Le texte a été refusé. Vérifiez la saisie et la limite de 12 000 caractères.")
            else:
                st.error("Le service d’analyse a rencontré une erreur. Réessayez dans un instant.")
        except (URLError, OSError, HTTPException):
            st.error("Le service d’analyse ne répond pas. Vérifiez que FastAPI est lancé, puis réessayez.")
        except ValueError:
            st.error("L’échange avec le service d’analyse est invalide.")


def load_news_article(article):
    excerpt = "\n\n".join(part.strip() for part in (article.title, article.description or "") if part.strip())
    st.session_state[article_key] = excerpt[:12_000]
    st.session_state.pop("analysis", None)


with st.expander("Chercher des articles en français"):
    with st.form("news_search", border=False):
        keywords = st.text_input("Mots-clés", max_chars=100, placeholder="Facultatif, ex. chômage")
        search_requested = st.form_submit_button("Chercher des articles")

    if search_requested:
        st.session_state.pop("news", None)
        query = urlencode({"q": keywords.strip()})
        try:
            with st.spinner("Recherche d’articles…"), urlopen(f"{endpoint}/actualites?{query}", timeout=15) as reply:
                st.session_state.news = NewsResponse.model_validate_json(reply.read())
        except HTTPError as error:
            messages = {
                429: "La limite de requêtes NewsData.io est atteinte.",
                503: "Vérifiez que FastAPI utilise une clé NewsData.io valide.",
            }
            st.error(messages.get(error.code, "La recherche d’articles a échoué. Réessayez dans un instant."))
        except (URLError, OSError, HTTPException, ValueError):
            st.error("Le service de recherche d’articles ne répond pas correctement.")

    if "news" in st.session_state:
        articles = st.session_state.news.articles
        if not articles:
            st.info("Aucun article trouvé. Essayez d’autres mots-clés.")
        else:
            st.caption("Chargez le titre et le résumé dans le formulaire ou ouvrez l’article pour lire le texte complet.")
        for index, article in enumerate(articles):
            st.text(article.title)
            publication_date = article.published_at[:10] if article.published_at else None
            details = [value for value in (article.source, publication_date) if value]
            if details:
                st.text(" · ".join(details))
            if article.description:
                st.text(article.description)
            st.link_button("Lire l’article", str(article.url))
            st.button("Charger l’extrait", key=f"news_{index}", on_click=load_news_article, args=(article,))
            st.divider()


def show_passage(passage):
    st.text(passage.extrait)
    st.markdown(f"[Ouvrir la publication du HCP ({passage.id})]({passage.url})")


if "analysis" in st.session_state:
    st.divider()
    st.header("Résultats de l’analyse")
    claims = st.session_state.analysis.affirmations
    if not claims:
        st.info("Aucune affirmation chiffrée à vérifier n’a été repérée dans ce texte.")
    else:
        st.caption("Les statuts portent sur les passages du corpus. Les extraits reformulent les publications du HCP.")
    for claim in claims:
        colors = {"Appuyée par les sources": "green", "Contredite": "red"}
        st.badge(claim.statut.value, color=colors.get(claim.statut, "gray"))
        st.text(claim.affirmation)
        st.write(claim.explication)
        proof_ids = {proof.id for proof in claim.preuves}
        for proof in claim.preuves:
            st.caption(f"Preuve de {proof.relation}" if proof.relation != "appui" else "Preuve d’appui")
            show_passage(proof)
        others = [p for p in claim.passages_consultes if p.id not in proof_ids]
        if others:
            with st.expander("Passages consultés sans valeur de preuve"):
                for passage in others:
                    show_passage(passage)
        st.divider()

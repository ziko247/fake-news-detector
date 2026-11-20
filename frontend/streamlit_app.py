"""Interface de lecture des analyses du corpus RGPH."""

import os
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

from app.schemas import AnalysisRequest, AnalysisResponse

st.set_page_config(page_title="Vérifier un article · RGPH", layout="centered")
st.html(Path(__file__).with_name("style.css"))
st.title("Vérifier les chiffres du Maroc")
st.write("Comparez les chiffres d’un article aux publications du recensement marocain.")
article_key = "article_text"
if st.button("Charger l’article de démonstration"):
    st.session_state[article_key] = (Path(__file__).resolve().parents[1] / "data/demo-rgph.txt").read_text(encoding="utf-8")
    st.session_state.pop("analysis", None)
with st.form("article", border=True):
    text = st.text_area(
        "Texte de l’article", height=200, key=article_key, max_chars=12_000,
        placeholder="Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants.",
        help="Le prototype vérifie certaines formulations sur la population, les ménages et l’urbanisation.",
    )
    st.caption("Le texte et les résultats sont enregistrés dans la base locale du serveur.")
    submitted = st.form_submit_button("Analyser le texte", type="primary")

if submitted:
    st.session_state.pop("analysis", None)
    if not text.strip():
        st.warning("Collez un article avant de lancer l’analyse.")
    else:
        endpoint = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
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

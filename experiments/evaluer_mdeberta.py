"""Évalue la relation entre des passages RGPH et des affirmations."""

import json
import re
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

from bm25_rgph import DATA_DIR, load_development_claims

MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
REVISION = "704310ca0bb8eb15bca150fc1e11083cd423dd02"
LABELS = {"entailment": "appui", "contradiction": "contradiction", "neutral": "neutre"}


def model_file(filename):
    return hf_hub_download(MODEL, filename, revision=REVISION, token=False)


def main():
    mini = (DATA_DIR / "mini-corpus-rgph.md").read_text(encoding="utf-8")
    corpus = (DATA_DIR / "corpus-rgph.md").read_text(encoding="utf-8")
    passages = dict(re.findall(r"^\| (P\d+) \| ([^|]+) \|", corpus, re.MULTILINE))
    claims = load_development_claims(mini)

    wrong_2014 = "En 2014, la population légale du Maroc était d’environ 29,892 millions."
    rural_comparison = "De 2014 à 2024, le taux annuel moyen de croissance de la population rurale marocaine était supérieur à celui de la population urbaine."
    cases = [
        ("A01", ("P01",), claims["A01"][0], "appui"),
        ("A02", ("P04",), claims["A02"][0], "contradiction"),
        ("A03", ("P01",), claims["A03"][0], "neutre"),
        ("A04", ("P01",), claims["A04"][0], "appui"),
        ("A05, année correspondante", ("P05",), wrong_2014, "contradiction"),
        ("A05, autre année", ("P06",), wrong_2014, "neutre"),
        ("A08", ("P09",), claims["A08"][0], "appui"),
        ("A09, deux passages", ("P09", "P10"), rural_comparison, "contradiction"),
        ("A09, un seul passage", ("P09",), rural_comparison, "neutre"),
        ("Quantité modifiée", ("P01",), claims["A01"][0].replace("36 828 330", "36 828 331"), "contradiction"),
        ("Négation du total", ("P01",), "Au 1er septembre 2024, le Maroc ne comptait pas 36 828 330 habitants selon le recensement.", "contradiction"),
        ("Négation d'une baisse", ("P09",), "La population urbaine du Maroc n’a pas diminué entre 2014 et 2024.", "appui"),
        ("A16", ("P14",), claims["A16"][0], "neutre"),
    ]

    config = json.loads(Path(model_file("config.json")).read_text(encoding="utf-8"))
    labels = {int(index): LABELS[label.lower()] for index, label in config["id2label"].items()}
    tokenizer = Tokenizer.from_file(model_file("tokenizer.json"))
    tokenizer.enable_truncation(max_length=512)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(
        model_file("onnx/model_quantized.onnx"),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    input_names = [item.name for item in session.get_inputs()]

    correct = 0
    print("| Cas | Passages | Attendu | Prédit | Score de la classe prédite |")
    print("| --- | --- | --- | --- | ---: |")
    for case, ids, claim, expected in cases:
        premise = " ".join(passages[pid].strip() for pid in ids)
        tokens = tokenizer.encode(premise, claim.strip())
        encodings = {
            "input_ids": tokens.ids,
            "attention_mask": tokens.attention_mask,
            "token_type_ids": tokens.type_ids,
        }
        inputs = {name: np.asarray([encodings[name]], dtype=np.int64) for name in input_names}
        logits = session.run(["logits"], inputs)[0][0]
        weights = np.exp(logits - np.max(logits))
        best = int(np.argmax(logits))
        predicted = labels[best]
        correct += predicted == expected
        print(f"| {case} | {', '.join(ids)} | {expected} | {predicted} | {weights[best] / weights.sum():.3f} |")

    print(f"\nRelations correctes : {correct}/{len(cases)}")


if __name__ == "__main__":
    main()

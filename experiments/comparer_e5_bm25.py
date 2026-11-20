"""Compare BM25 et E5 sur le lot de développement RGPH."""

import re
from statistics import median
from timeit import repeat

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

from bm25_rgph import DATA_DIR, build_index, load_development_claims, rank_passages

MODEL = "intfloat/multilingual-e5-small"
REVISION = "ccc66d3bcd826f577e26b9a4072cc5fe3a7ad6a3"
TIMING_REPEATS = 21


def main():
    mini = (DATA_DIR / "mini-corpus-rgph.md").read_text(encoding="utf-8")
    corpus = (DATA_DIR / "corpus-rgph.md").read_text(encoding="utf-8")
    passages = re.findall(r"^\| (P\d+) \| ([^|]+) \|", corpus, re.MULTILINE)
    claims = load_development_claims(mini)
    if not passages or not claims:
        raise ValueError("Le corpus et le lot de développement doivent être renseignés.")
    index = build_index(passages)

    tokenizer = Tokenizer.from_file(hf_hub_download(MODEL, "onnx/tokenizer.json", revision=REVISION))
    tokenizer.enable_truncation(max_length=512)
    tokenizer.enable_padding(pad_id=tokenizer.token_to_id("<pad>"), pad_token="<pad>")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(
        hf_hub_download(MODEL, "onnx/model_qint8_avx512_vnni.onnx", revision=REVISION),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )

    def embed(texts):
        tokens = tokenizer.encode_batch(texts)
        attention = np.asarray([item.attention_mask for item in tokens], dtype=np.int64)
        encodings = {
            "input_ids": np.asarray([item.ids for item in tokens], dtype=np.int64),
            "attention_mask": attention,
            "token_type_ids": np.asarray([item.type_ids for item in tokens], dtype=np.int64),
        }
        inputs = {item.name: encodings[item.name] for item in session.get_inputs()}
        hidden = session.run(["last_hidden_state"], inputs)[0]
        mask = attention[:, :, None].astype(hidden.dtype)
        vectors = (hidden * mask).sum(axis=1) / mask.sum(axis=1)
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    passage_vectors = embed([f"passage: {text}" for _, text in passages])

    def rank_e5(claim):
        scores = passage_vectors @ embed([f"query: {claim}"])[0]
        ranking = [(pid, float(score)) for (pid, _), score in zip(passages, scores, strict=True)]
        return sorted(ranking, key=lambda item: (-item[1], item[0]))

    print("| Cas | Méthode | Top 3 | Rangs des preuves | Temps médian (ms) |")
    print("| --- | --- | --- | --- | ---: |")
    for claim_id, (claim, evidence) in claims.items():
        methods = (("BM25", lambda: rank_passages(claim, *index)), ("E5", lambda: rank_e5(claim)))
        for name, rank in methods:
            ranking = rank()
            ranks = {pid: position for position, (pid, _) in enumerate(ranking, start=1)}
            top = ", ".join(pid for pid, _ in ranking[:3])
            evidence_ranks = ", ".join(f"{pid} ({ranks[pid]})" for pid in evidence)
            milliseconds = median(repeat(rank, repeat=TIMING_REPEATS, number=1)) * 1000
            print(f"| {claim_id} | {name} | {top} | {evidence_ranks or '—'} | {milliseconds:.3f} |")


if __name__ == "__main__":
    main()

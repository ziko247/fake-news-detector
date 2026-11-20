"""Classe les passages par similarité sémantique avec E5."""

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

MODEL = "intfloat/multilingual-e5-small"
REVISION = "ccc66d3bcd826f577e26b9a4072cc5fe3a7ad6a3"


def build_e5_ranker(passages):
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

    return rank_e5

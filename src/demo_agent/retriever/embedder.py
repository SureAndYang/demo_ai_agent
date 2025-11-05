#!/usr/bin/env python3
import numpy as np
import lmstudio as lms
from typing import List


class Embedder:
    embed_model = "text-embedding-embeddinggemma-300m-qat"
    def __init__(self, model=None):
        self.model_name = model or Embedder.embed_model
        self.model = lms.embedding_model(self.model_name)

    def __call__(self, docs: List[str]):
        x = np.array(self.model.embed(docs))
        return np.array(self.model.embed(docs), dtype="float32")

embedder = Embedder()


if __name__ == "__main__":
    query = '[user] do you know my name?'
    print(embedder([query]))


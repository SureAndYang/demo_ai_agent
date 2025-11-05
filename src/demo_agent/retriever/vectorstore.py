#!/usr/bin/env python3

import numpy as np
import faiss
from demo_agent.retriever.embedder import embedder

class VectorStore:
    def __init__(self) -> None:
        self.dim = np.array(embedder(["hi"]), dtype="float32").shape[1]
        self.store = faiss.IndexFlatIP(self.dim)
        self.docs = list()

    def insert(self, docs) -> None:
        if len(docs) == 0: return
        self.store.add(embedder(docs))
        self.docs.extend(docs)

    def search(self, query, k=3, threshold=0.5):
        q_emb = embedder([query])
        distances, indices = self.store.search(q_emb, k)
        return [
            (self.docs[idx], float(distances[0][rank]))
            for rank, idx in enumerate(indices[0])
            if float(distances[0][rank]) > threshold
        ]


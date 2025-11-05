#!/usr/bin/env python3
class Cutter:
    def __init__(self, max_len=300, overlap=30):
        self.max_len = max_len
        self.overlap = overlap

    def __call__(self, docs):
        ret = []
        for doc in docs:
            if len(doc) < self.max_len:
                ret.append(doc)
            else:
                ret.extend(self._cut_text(doc))
        return ret

    def _cut_text(self, doc):
        ret = []
        s, e = 0, self.max_len
        while e < len(doc):
            ret.append(doc[s: e])
            s = s + self.max_len - self.overlap
            e = s + self.max_len
        return ret


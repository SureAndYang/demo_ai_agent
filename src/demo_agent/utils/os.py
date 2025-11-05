#!/usr/bin/env python3

import os
import json
from json import JSONEncoder

def read_json_file(f) -> dict:
    if not os.path.exists(f):
        return dict()
    try:
        return json.load(open(f))
    except:
        return dict()


class JsonEncoder(JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except:
            return o.to_json()


def obj2json(cls, keys):
    d = dict()
    for k in keys:
        d[k] = getattr(cls, k)
    return d



#!/usr/bin/env python3

from markitdown import MarkItDown

class Loader:

    def __init__(self, use_ocr=False):
        self.md = MarkItDown()
        if use_ocr:
            # TODO: Add deepseek-ocr for better ocr recognition.
            # from transformers import AutoModel, AutoTokenizer
            # model_name = "deepseek-ai/DeepSeek-OCR"
            pass

    def __call__(self, doc):
        try:
            return self.md.convert(doc).text_content
        except:
            raise TypeError(f"File {doc} can't be converted by markitdown!")


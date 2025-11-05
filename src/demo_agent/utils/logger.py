#!/usr/bin/env python3
import logging

logger = logging.getLogger("AI Agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

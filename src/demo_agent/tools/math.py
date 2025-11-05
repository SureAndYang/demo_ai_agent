#!/usr/bin/env python3

def math_func(expression: str) -> str:
    try:
        return str(eval(expression))
    except:
        raise TypeError("tools.math_func expression {expression}")


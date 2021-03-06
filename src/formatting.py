"""
Functionality to format the command line application's output.

> https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
"""

from typing import Any, List


def fprint(level: str, message: str) -> str:
    FBOLD = "\u001b[1m"
    FRESET = "\u001b[0m"
    FRED = "\u001b[31m"
    FGREEN = "\u001b[32m"
    FYELLOW = "\u001b[33m"
    output = ""
    if level == "info":
        output = f"[{FBOLD}{FGREEN}info{FRESET}] {message}"
    if level == "error":
        output = f"[{FBOLD}{FRED}error{FRESET}] {message}"
    if level == "warning":
        output = f"[{FBOLD}{FYELLOW}warning{FRESET}] {message}"
    print(output)
    return output


def flatten_list(to_flatten: List[List[Any]]) -> List[Any]:
    return [item for sublist in to_flatten for item in sublist]

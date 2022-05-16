"""
Construct a keyword set based on Google SERPs suggestions.

Given a list of keywords, this algorithm recursively fetches related questions and searches until a cutoff point is met.

The cutoff point represents the minimum number of rows to export.
The output might contain more keywords than the cutoff point. That's because the algorithm collects all keywords on file.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests

from src.apicalls import query_valueserp
from src.formatting import fprint

session = requests.Session()


def collect_related(response: Dict[str, Any]) -> List[str]:
    related = list()
    if "related_searches" in response:
        related.append([i["query"] for i in response["related_searches"]])
    if "related_questions" in response:
        related.append([i["question"] for i in response["related_questions"]])
    return [i for sublist in related for i in sublist]


def get_kwlist(keywords: List[str], location: str, cutoff: int, fpath: Path, cut: List[str]) -> pd.DataFrame:
    total = len(keywords)
    location = location.title()
    fprint("info", f"collecting keyword list from {total} keywords - location: {location.title()}")
    kw_stack: List[str] = list()
    kw_stack_length = len(kw_stack)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = executor.map(lambda i: query_valueserp(i, location), keywords)
        for f in futures:
            response = f.json()
            related = collect_related(response)
            kw_stack.extend(related)
            kw_stack_length += len(related)
    while kw_stack_length < cutoff:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = executor.map(lambda i: query_valueserp(i, location), kw_stack)
            for f in futures:
                stack_response = f.json()
                stack_related = collect_related(stack_response)
                kw_stack.extend(stack_related)
                kw_stack_length += len(stack_related)
    collection = list(map(str.lower, kw_stack))
    dataset = pd.DataFrame(collection, columns=["kwset"])
    if cut:
        patterns = "|".join([i for i in cut])
        dataset = dataset.loc[~dataset["kwset"].str.contains(patterns)]
    dataset.to_csv(fpath)
    fprint("info", f"keyword list completed ~ find your output @ {fpath}")
    return dataset

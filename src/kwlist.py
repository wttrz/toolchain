"""
Constructs a keyword list based on SERPs suggestions.

Given a list of keywords, it recursively fetches related questions and searches until cutoff point is met.
"""

import requests
import pandas as pd
from src.apicalls import build_valueserp_calls
import sys
from concurrent.futures import ThreadPoolExecutor


session = requests.Session()


def collect_suggestions(response):
    related = list()
    if "related_searches" in response:
        searches = [r["query"] for r in response["related_searches"]]
        related.extend(searches)
    if "related_questions" in response:
        questions = [r["question"] for r in response["related_questions"]]
        related.extend(questions)
    return related


def get_kwlist(keywords, location, cutoff, fpath):
    api_calls = build_valueserp_calls(keywords, location)
    kw_stack = list()
    kw_stack_length = len(kw_stack)
    print(f"collecting serps suggestions for {len(keywords)} keywords ...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = executor.map(session.get, api_calls)
        for f in futures:
            response = f.json()
            serps = collect_suggestions(response)
            kw_stack.extend(serps)
            kw_stack_length += len(serps)
    while kw_stack_length < cutoff:
        stack_calls = build_valueserp_calls(kw_stack, location)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = executor.map(session.get, stack_calls)
            for f in futures:
                stack_response = f.json()
                stack_serps = collect_suggestions(stack_response)
                kw_stack.extend(stack_serps)
                kw_stack_length += len(stack_serps)
    collection = list(map(str.lower, kw_stack))
    dataset = pd.DataFrame(collection, columns=["kwset"])
    dataset.to_csv(fpath)
    return dataset

"""
Construct a keyword set based on SERPs suggestions.

Given a list of keywords, this algorithm recursively fetches related questions and searches until a cutoff point is met.
"""

import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from src.authentication import get_api_credit, get_api_key

session = requests.Session()

# TODO: use the get_valueserp queries intead of using build_valueserp_calls


def build_valueserp_calls(keywords, location):
    apikey = get_api_key("valueserp")
    get_api_credit("valueserp")
    supported_locations = {
        "Norway": ["google.no", "no", "no"],
        "Sweden": ["google.se", "se", "sv"],
        "Canada": ["google.ca", "ca", "en"],
        "Denmark": ["google.dk", "dk", "da"],
        "Finland": ["google.fi", "fi", "fi"],
        "United States": ["google.com", "us", "en"],
        "United Kingdom": ["google.co.uk", "uk", "en"],
    }
    if location.title() not in supported_locations:
        sys.exit("[error] unsupported location")
    locale = supported_locations.get(location.title())
    google_domain = locale[0]
    gl = locale[1]
    hl = locale[2]
    url = f"https://api.valueserp.com/search?api_key={apikey}"
    geo = f"&gl={gl}" + f"&location={location}"
    lang = f"&hl={hl}"
    domain = f"&google_domain={google_domain}"
    datafmt = "&output=json&flatten_results=true"
    api_calls = [url + f"&q={k}" + lang + geo + domain + datafmt for k in keywords]
    return api_calls


# TODO: check how i resolved this in the on page module
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
    total = len(keywords)
    print(f"[info] collecting keyword list from {total} keywords in {location.title()}.")
    api_calls = build_valueserp_calls(keywords, location)
    kw_stack = list()
    kw_stack_length = len(kw_stack)
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

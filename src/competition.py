"""
Find the most prominent competitors for a keyword set.

Given a list of keywords, this algorithm creates a sorted list of Google Search domains ordered by frequency of appearance.
"""

import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import requests

from src.authentication import get_api_credit, get_api_key

# TODO: Redo this module. Instead of building API calls, use the query_valueserp() function
# use the constant for value serps locations, modify the build_value_serps_calls

session = requests.Session()


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


def enumerate_competition(keywords, location, fpath):
    total = len(keywords)
    print(f"[info] collecting competitors for {total} keywords in {location.title()}...")
    api_calls = build_valueserp_calls(keywords, location)
    domains = list()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = executor.map(session.get, api_calls)
        for f in futures:
            response = f.json()
            serps = [r["domain"] for r in response["organic_results"] if "domain" in r]
            domains.append(serps)
    flat_domain_list = [i.replace("www.", "") for sublist in domains for i in sublist]
    tally = dict(Counter(flat_domain_list))
    sorted_tally = dict(sorted(tally.items(), key=lambda x: x[1], reverse=True))
    with open(fpath, "w") as f:
        for k, v in sorted_tally.items():
            line = f"{k}: {v}\n"
            f.write(line)
    return sorted_tally

"""
Finds the most prominent competitors for a keyword set.

Given a list of keywords, it creates a sorted list of domains ordered by frequency of appearance.
"""

import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from src.authentication import get_api_key, get_api_credit
from src.apicalls import build_valueserp_calls

session = requests.Session()


def enumerate_competition(keywords, location, fpath):
    print(f"finding competitors for {len(keywords)} keywords")
    api_calls = build_valueserp_calls(keywords, location)
    domains = list()
    print("processing ...")
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

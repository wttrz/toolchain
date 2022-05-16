"""
Find the most prominent competitors for a keyword set.

Given a list of keywords, this algorithm creates a sorted list of Google Search domains ordered by frequency of appearance.
"""

import csv
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

import requests

from src.apicalls import query_valueserp
from src.formatting import fprint

session = requests.Session()


def enumerate_competition(keywords: List[str], location: str, fpath: Path) -> Dict[str, int]:
    total = len(keywords)
    location = location.title()
    fprint("info", f"collecting competitors for {total} keywords - location: {location.title()}")
    domains: List[List[str]] = list()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = executor.map(lambda i: query_valueserp(i, location), keywords)
        for f in futures:
            response = f.json()
            serps = [i["domain"] for i in response["organic_results"] if "domain" in i]
            domains.append(serps)
    flat_domain_list = [i.replace("www.", "") for sublist in domains for i in sublist]
    tally = dict(Counter(flat_domain_list))
    sorted_tally = dict(sorted(tally.items(), key=lambda x: x[1], reverse=True))
    file_object = open(fpath, "w")
    writer = csv.writer(file_object)
    for k, v in sorted_tally.items():
        writer.writerow([k, v])
    file_object.close()
    fprint("info", f"competitors collected ~ find your output @ {fpath}")
    return sorted_tally

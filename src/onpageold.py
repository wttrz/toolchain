"""
On page optimization suggestions.

This module collects metadata from the SERPs for a set of search terms.
The metadata can then be used to support on page optimization for a given page.
"""

# TODO: add functionality to create the content brief itself (?) along with the suggestions
# TODO: explain this in docstring above too
# TODO: add mobile friendliness api, pagespeed api
# TODO: add (??)    schema = html.xpath("//*[@itemtype]/@itemtype")
# TODO: add (??)    meta_names = html.xpath("//meta/@name")
# TODO: add (??)    meta_contents = html.xpath("//meta/@content")
# TODO: add (??)    img_alts = html.xpath("//img/@alt")
# TODO: add (??)    img_links = html.xpath("//img/@src")
# TODO: add (??)    links = html.xpath("//@href")
# TODO: add (??)    hreflang = html.xpath("//*[@hreflang]/@hreflang")

import sys
from concurrent.futures import ThreadPoolExecutor

import lxml.html
import requests

from src.authentication import get_api_credit, get_api_key
from src.constants import VALUESERP_LOCATIONS

session = requests.Session()


def get_page_data(url):
    print(f"[info] collecting page data for {url}")
    r = session.get(url)

    if not r.content:
        sys.exit("[error] no data found for the url")

    html = lxml.html.fromstring(r.content)
    titles = html.xpath(".//title//text()")
    descriptions = html.xpath("//meta[@name='description']/@content")
    h1s = html.xpath("//h1//text()")
    h2s = html.xpath("//h2//text()")
    return {
        "url": r.url,
        "title": titles,
        "description": descriptions,
        "h1": h1s,
        "h2": h2s,
    }


def get_serps(terms, location):
    if location not in VALUESERP_LOCATIONS:
        sys.exit(f"[error] unsupported location, try > {VALUESERP_LOCATIONS.keys()}")
    get_api_credit("valueserp")
    api_key = get_api_key("valueserp")
    locale = VALUESERP_LOCATIONS.get(location.title())
    domain, country, language = locale[0], locale[1], locale[2]
    endpoint = f"https://api.valueserp.com/search?api_key={api_key}"
    calls = [
        endpoint
        + f"&q={t}"
        + f"&gl={country}"
        + f"&hl={language}"
        + f"&location={location.title()}"
        + f"&google_domain={domain}"
        + "&output=json&flatten_results=true"
        for t in terms
    ]
    print(f"[info] collecting serps for {terms} from {location} ...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = executor.map(session.get, calls)
        # the queries and questions are not coming up
        for f in futures:
            r = f.json()
            serps_links = [r["link"] for r in r["organic_results"] if "link" in r]
            domain_links = [l for l in serps_links if not "google" in l]
    return {"results": domain_links}


def pfetch(url, term, terms, location, fpath):
    print(f"[info] optimizing {url} for '{term}'")
    print(f"[info] secondary search terms > {terms}")
    if terms:
        terms.append(term)
        terms = [t.replace(" ", "+") for t in terms]
    else:
        terms = term
    page_data = get_page_data(url)
    serps = get_serps(terms, location)

    serps_data = [get_page_data(l) for l in serps["results"]]

    urls = [d["url"] for d in serps_data]
    urls.append(page_data["url"])

    titles = [d["title"] for d in serps_data]
    titles.append(page_data["title"])
    flat_titles = [item.strip() for sublist in titles for item in sublist]

    descriptions = [d["description"] for d in serps_data]
    descriptions.append(page_data["description"])
    flat_descriptions = [item.strip() for sublist in descriptions for item in sublist]

    h1s = [d["h1"] for d in serps_data]
    h1s.append(page_data["h1"])
    flat_h1s = [item.strip() for sublist in h1s for item in sublist]

    h2s = [d["h2"] for d in serps_data]
    h2s.append(page_data["h2"])
    flat_h2s = [item.strip() for sublist in h2s for item in sublist]

    with open(fpath, "w") as f:
        f.write("-" * 50)
        f.write("\n")
        f.write("URLS:\n\n")
        for i in urls:
            f.write(i)
            f.write("\n")
        f.write("\n")

        f.write("-" * 50)
        f.write("\n")
        f.write("TITLES:\n\n")
        for t in flat_titles:
            f.write(t)
            f.write("\n")
        f.write("\n")

        f.write("-" * 50)
        f.write("\n")
        f.write("H1s:\n\n")
        for t in flat_h1s:
            f.write(t)
            f.write("\n")
        f.write("\n")

        f.write("-" * 50)
        f.write("\n")
        f.write("H2s:\n\n")
        for t in flat_h2s:
            f.write(t)
            f.write("\n")
        f.write("\n")

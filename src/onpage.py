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
import requests
import lxml.html
from src.constants import VALUESERP_LOCATIONS
from concurrent.futures import ThreadPoolExecutor
from src.authentication import get_api_credit, get_api_key


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
            rs = [r["query"] for r in r["related_searches"]]
            rq = [r["question"] for r in r["related_questions"]]
            serps_links = [r["link"] for r in r["organic_results"] if "link" in r]
            domain_links = [l for l in serps_links if not "google" in l]
    return {"searches": rs, "questions": rq, "results": domain_links}


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
        f.write("RECOMMENDED QUERIES:\n\n")
        for i in serps["questions"]:
            f.write(i)
            f.write("\n")
        for i in serps["searches"]:
            f.write(i)
            f.write("\n")
        f.write("\n")

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


# def collect_metadata(url):
#    print(f"[info] collecting metadata for {url}")
#    r = session.get(url)
#    if not r.content:
#        sys.exit("[error] could not download content from the url")
#    html = lxml.html.fromstring(r.content)
#    metadata = dict()
#    title = html.xpath(".//title//text()")
#    h1 = html.xpath("//h1//text()")
#    h2 = html.xpath("//h2//text()")
#    canonical = html.xpath("//link[@rel='canonical']/@href")
#    description = html.xpath("//meta[@name='description']/@content")
#    jsonld = html.xpath("//script[@type='application/ld+json']//text()")
#    metadata.update(
#        {
#            "url": r.url,
#            "canonical": canonical,
#            "status_code": r.status_code,
#            "page_title": title,
#            "description": description,
#            "h1": h1,
#            "h2": h2,
#        }
#    )
#    return metadata
#
#
# def collect_serps(terms, location):
#    if location not in VALUESERP_LOCATIONS:
#        sys.exit(f"[error] unsupported location, try > {VALUESERP_LOCATIONS.keys()}")
#    get_api_credit("valueserp")
#    api_key = get_api_key("valueserp")
#    locale = VALUESERP_LOCATIONS.get(location.title())
#    domain = locale[0]
#    country = locale[1]
#    language = locale[2]
#    endpoint = f"https://api.valueserp.com/search?api_key={api_key}"
#    calls = [
#        endpoint
#        + f"&q={t}"
#        + f"&gl={country}"
#        + f"&hl={language}"
#        + f"&location={location.title()}"
#        + f"&google_domain={domain}"
#        + "&output=json&flatten_results=true"
#        for t in terms
#    ]
#    print(f"[info] collecting serps for {terms} from {location} ...")
#    with ThreadPoolExecutor(max_workers=4) as executor:
#        futures = executor.map(session.get, calls)
#        for f in futures:
#            r = f.json()
#            rs = [r["query"] for r in r["related_searches"] if "related_searches" in r]
#            rq = [r["question"] for r in r["related_questions"] if "related_questions" in r]
#            serps_links = [r["link"] for r in r["organic_results"] if "link" in r]
#            domain_links = [l for l in serps_links if not "google" in l]
#    return {"searches": rs, "questions": rq, "results": domain_links}
#
#
# def pfetch(url, term, terms, location, fpath):
#    print(f"[info] optimizing {url} for '{term}'")
#    print(f"[info] secondary search terms > {terms}")
#    if terms:
#        terms.append(term)
#        terms = [t.replace(" ", "+") for t in terms]
#    else:
#        terms = term
#    page_data = collect_metadata(url)
#    serps = collect_serps(terms, location)
#    serps_data = [collect_metadata(l) for l in serps["results"]]
#
#    urls = [d["url"] for d in serps_data]
#    urls.append(page_data["url"])
#    flat_urls = [item for sublist in urls for item in sublist]
#    print(flat_urls)
#
#    titles = [d["page_title"] for d in serps_data]
#    titles.append(page_data["page_title"])
#    flat_titles = [item for sublist in titles for item in sublist]
#
#    descriptions = [d["description"] for d in serps_data]
#    descriptions.append(page_data["description"])
#    flat_descriptions = [item for sublist in descriptions for item in sublist]
#
#    h1s = [d["h1"] for d in serps_data]
#    h1s.append(page_data["h1"])
#    flat_h1s = [item for sublist in h1s for item in sublist]
#
#    h2s = [d["h2"] for d in serps_data]
#    h2s.append(page_data["h2"])
#    flat_h2s = [item for sublist in h2s for item in sublist]
#
#    with open(fpath, "w") as f:
#        f.write("-" * 50)
#        f.write("\n")
#        f.write("URLS:\n\n")
#        for i in flat_urls:
#            f.write(i)
#            f.write("\n\n")
#
#        f.write("-" * 50)
#        f.write("\n")
#        f.write("TITLES:\n\n")
#        for t in flat_titles:
#            f.write(t)
#            f.write("\n\n")
#
#        f.write("-" * 50)
#        f.write("\n")
#        f.write("DESCRIPTIONS:\n\n")
#        for d in flat_descriptions:
#            f.write(d)
#            f.write("\n\n")
#
#        f.write("-" * 50)
#        f.write("\n")
#        f.write("H1s:\n\n")
#        for d in flat_h1s:
#            f.write(d)
#            f.write("\n\n")
#
#        f.write("-" * 50)
#        f.write("\n")
#        f.write("H2s:\n\n")
#        for d in flat_h2s:
#            f.write(d)
#            f.write("\n\n")

"""
On page optimization suggestions.

This module collects metadata from the SERPs for a set of search terms.
The metadata can then be used to support on page optimization for a given page.
"""

# Emil's suggestion > https://precisdigital.atlassian.net/wiki/spaces/TECHDATAMENU/pages/2114715676/On-page+Optimization+Tool
# Inputs > url, primary query, secondary queries, target language
# Calculations > aggregated search volume
# Mobile Friendliness Summary (target url)
# Pagespeed Score Mobile + Desktop (target url)
# Classifications > title len, description len, primary kw in meta and title

# TODO: add functionality to create the content brief itself (?) along with the suggestions
# TODO: explain this in docstring above too
# TODO: add (??)    schema = html.xpath("//*[@itemtype]/@itemtype")
# TODO: add         pagespeed and mobile friendliness tests

import sys

import lxml.html
import numpy as np
import requests

from src.apicalls import query_valueserp
from src.authentication import get_api_credit, get_api_key
from src.constants import USER_AGENT

session = requests.Session()


def get_response(url):
    print(f"[info] fetching {url}")
    try:
        response = session.get(url, headers=USER_AGENT)
    except ConnectionError:
        print("[error] connection error for the url")
    if response and not response.content:
        sys.exit("[error] no data found for the url")
    return response


def get_titles(response):
    html = lxml.html.fromstring(response.content)
    title_list = html.xpath("//title//text()")
    return [i.strip() for i in title_list]


def get_descriptions(response):
    html = lxml.html.fromstring(response.content)
    description_list = html.xpath("//meta[@name='description']/@content")
    return [i.strip() for i in description_list]


def get_h1s(response):
    html = lxml.html.fromstring(response.content)
    h1_list = html.xpath(".//h1//text()")
    return [i.strip() for i in h1_list]


def get_h2s(response):
    html = lxml.html.fromstring(response.content)
    h2_list = html.xpath("//h2//text()")
    return [i.strip() for i in h2_list]


def get_canonical_link(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//link[@rel='canonical']/@href")


def get_alternate_links(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//link[@rel='alternate']/@href")


def get_hreflang(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//link[@rel='alternate']/@hreflang")


def get_links(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//@href")


def get_image_links(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//img/@src")


def get_metarobots(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//meta[@name='robots']/@content")


def get_paragraphs(response):
    html = lxml.html.fromstring(response.content)
    return html.xpath("//p//text()")


def get_wordcount(response):
    html = lxml.html.fromstring(response.content)
    title = " ".join(get_titles(response))
    h1s = " ".join(get_h1s(response))
    h2s = " ".join(get_h2s(response))
    paragraphs = " ".join(get_paragraphs(response))
    all_text = title + h1s + h2s + paragraphs
    return len(all_text.split())


def get_page_metadata(url):
    metadata = dict()
    response = get_response(url)
    metadata.update(
        {
            "titles": get_titles(response),
            "descriptions": get_descriptions(response),
            "h1s": get_h1s(response),
            "h2s": get_h2s(response),
            "canonical": get_canonical_link(response),
            "alternate_links": get_alternate_links(response),
            "hreflang": get_hreflang(response),
            "links": get_links(response),
            "image_links": get_image_links(response),
            "meta_robots": get_metarobots(response),
            "wordcount": get_wordcount(response),
        }
    )
    return metadata


def create_brief(url, terms, location, page, related, serps, fpath):
    main_query = terms[-1]
    secondary_queries = ", ".join(terms)
    nonempty_serps_titles = set(list(filter(None, serps["titles"])))
    nonempty_serps_descriptions = set(list(filter(None, serps["descriptions"])))
    nonempty_serps_h1s = set(list(filter(None, serps["h1s"])))
    nonempty_serps_h2s = set(list(filter(None, serps["h2s"])))
    nonempty_page_titles = set(list(filter(None, page["titles"])))
    nonempty_page_descriptions = set(list(filter(None, page["descriptions"])))
    nonempty_page_h1s = set(list(filter(None, page["h1s"])))
    nonempty_page_h2s = set(list(filter(None, page["h2s"])))
    serps_avg_wordcounts = int(np.mean(serps["wordcounts"]))

    with open(fpath, "w") as f:
        ndashes = 150
        f.write("Content Brief\n")
        f.write("-" * ndashes)
        f.write(f"\n\nTarget Page: {url}\n")
        f.write(f"Main Query: {main_query}\n")
        f.write(f"Secondary Queries: {secondary_queries}\n")
        f.write(f"Location: {location}\n\n")
        f.write(f"SERPS Organic Results Pages:\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(serps["urls"]))
        f.write(f"\n\nSERPS Related Searches & Questions: {len(related)}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(related))
        f.write(f"\n\nSERPs titles:\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_serps_titles))
        f.write(f"\n\nSERPs descriptions:\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_serps_descriptions))
        f.write(f"\n\nSERPs h1s:\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_serps_h1s))
        f.write(f"\n\nSERPs h2s:\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_serps_h2s))
        f.write(f"\n\nSERPs Average Page Word Count: {serps_avg_wordcounts}\n")
        f.write("-" * ndashes)
        f.write(f"\n\nTarget Page Canonical: {', '.join(page['canonical'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.write(f"\nTarget Page Meta Robots: {', '.join(page['meta_robots'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.write(f"\nTarget Page Wordcount: {page['wordcount']}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.write(f"\nTarget Page Titles: {len(nonempty_page_titles)}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_page_titles))
        f.write(f"\n\nTarget Page Descriptions: {len(nonempty_page_descriptions)}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_page_descriptions))
        f.write(f"\n\nTarget Page H1s: {len(nonempty_page_h1s)}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_page_h1s))
        f.write(f"\n\nTarget Page H2s: {len(nonempty_page_h2s)}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(nonempty_page_h2s))
        f.write(f"\n\nTarget Page Hreflang: {len(page['hreflang'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(page["hreflang"]))
        f.write(f"\nTarget Page Alternate Links: {len(page['alternate_links'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(page["alternate_links"]))
        f.write(f"\n\nTarget Page Image Links: {len(page['image_links'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(page["image_links"]))
        f.write(f"\n\nTarget Page Links: {len(page['links'])}\n")
        f.write("-" * ndashes)
        f.write("\n")
        f.writelines("\n".join(page["links"]))


def suggest(url, term, terms, location, fpath):
    if terms:
        terms.append(term)
        queries = [t.replace(" ", "+") for t in terms]
    else:
        queries = [term]
    organic_results = list()
    related_results = list()
    for i in queries:
        print(f"[info] collecting serps for {i}")
        serps = query_valueserp(i, location)
        for i in serps["organic_results"]:
            if "domain" in i:
                organic_results.append(i["link"])
        if "related_searches" in serps:
            related_results.append([i["query"] for i in serps["related_searches"]])
        if "related_questions" in serps:
            related_results.append([i["question"] for i in serps["related_questions"]])
    flat_related = [i for l in related_results for i in l]
    page_data = get_page_metadata(url)
    serps_metadata = dict()
    serps_titles = list()
    serps_descriptions = list()
    serps_h1s = list()
    serps_h2s = list()
    serps_wordcounts = list()
    for i in organic_results:
        print(f"[info] collecting page metadata for {i}")
        metadata = get_page_metadata(i)
        serps_titles.append(metadata["titles"])
        serps_descriptions.append(metadata["descriptions"])
        serps_h1s.append(metadata["h1s"])
        serps_h2s.append(metadata["h2s"])
        serps_wordcounts.append(metadata["wordcount"])
    serps_metadata.update(
        {
            "urls": organic_results,
            "titles": [i for l in serps_titles for i in l],
            "descriptions": [i for l in serps_descriptions for i in l],
            "h1s": [i for l in serps_h1s for i in l],
            "h2s": [i for l in serps_h2s for i in l],
            "wordcounts": serps_wordcounts,
        }
    )
    create_brief(url, queries, location, page_data, flat_related, serps_metadata, fpath)
    return

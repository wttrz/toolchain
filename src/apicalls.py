"""
Routines to call APIs.

References:

> https://www.valueserp.com/docs
> https://developer.semrush.com/api/
"""

import sys
from typing import Any

import requests

from src.authentication import get_api_credit, get_api_key
from src.constants import VALUESERP_LOCATIONS
from src.formatting import fprint

session = requests.Session()


def query_valueserp(term: str, location: str) -> requests.Response:
    get_api_credit("valueserp")
    api_key = get_api_key("valueserp")
    locale = VALUESERP_LOCATIONS.get(location.title())
    if not locale:
        locales = ", ".join(list(VALUESERP_LOCATIONS.keys()))
        fprint("error", f"unsupported location, try any of {locales}")
        sys.exit()
    endpoint = f"https://api.valueserp.com/search?api_key={api_key}"
    domain = locale[0] if locale else "google.se"
    country = locale[1] if locale else "se"
    language = locale[2] if locale else "sv"
    parameters = {
        "q": term,
        "gl": country,
        "hl": language,
        "location": location.title(),
        "google_domain": domain,
        "output": "json",
        "flatten_results": "true",
    }
    return session.get(endpoint, params=parameters)


def query_semrush(domain: str, location: str, rows: int) -> requests.Response:
    apikey = get_api_key("semrush")
    get_api_credit("valueserp")
    database = location.lower()
    databases = ["se", "no", "dk", "fi", "uk", "us"]
    if database not in databases:
        fprint("error", f"unsupported location, try: {', '.join(databases)}")
        sys.exit()
    url = f"https://api.semrush.com/?type=domain_organic&key={apikey}"
    export_columns = f"&export_columns=Ph,Ur,Po,Nq&domain={domain}"
    display = f"&display_sort=nq_desc&display_limit={rows}&database={database}"
    api_call = url + export_columns + display
    return requests.get(api_call)


def query_pagespeed(url: str) -> Any:
    fprint("info", f"collecting lighthouse mobile pagespeed data for {url}")
    apikey = get_api_key("pd-tech-seo")
    payload = {"url": url, "key": apikey, "strategy": "mobile"}
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    response = session.get(endpoint, params=payload).json()
    return response["lighthouseResult"]["categories"]["performance"]["score"]


def query_mobile_friendliness(url: str) -> Any:
    fprint("info", f"collecting mobile friendliness data for {url}")
    apikey = get_api_key("pd-tech-seo")
    payload = {"url": url, "key": apikey}
    endpoint = "https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run"
    response = session.post(endpoint, data=payload).json()
    return response["mobileFriendliness"]

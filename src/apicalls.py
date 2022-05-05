import sys

import requests

from src.authentication import get_api_credit, get_api_key
from src.constants import VALUESERP_LOCATIONS

session = requests.Session()


def query_valueserp(term, location):
    get_api_credit("valueserp")
    api_key = get_api_key("valueserp")
    locale = VALUESERP_LOCATIONS.get(location.title())
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
    return session.get(endpoint, params=parameters).json()

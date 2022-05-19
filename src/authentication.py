"""
Perform authentication operations.

This module contains routines to authenticate in various API.

References:

> https://google-auth.readthedocs.io/en/master/
> https://developers.google.com/identity/protocols/oauth2/scopes
> https://precisdigital.atlassian.net/wiki/spaces/TECH/pages/1335132191/GCP+Authentication+Guidelines
> https://docs.google.com/presentation/d/1AQTVogaSoh3ZKq4LrQbgonzg7L-MCQ55BZ7xu255zdg/edit?usp=sharing
"""

import os
import sys
from typing import Optional

import requests

from src.formatting import fprint


def get_api_key(api_name: str) -> Optional[str]:
    supported_apis = ["semrush", "valueserp", "pd-tech-seo"]
    if api_name not in supported_apis:
        fprint("error", f"{api_name} is not supported")
        sys.exit()
    if api_name == "semrush":
        return os.environ.get("SEMRUSHKEY")
    if api_name == "valueserp":
        return os.environ.get("VALUESERPKEY")
    if api_name == "pd-tech-seo":
        return os.environ.get("PDTECHSEO")
    return None


def get_api_credit(api_name: str) -> int:
    apikey = get_api_key(api_name)
    if api_name == "semrush":
        endpoint = "http://www.semrush.com/users/countapiunits.html"
        params = {"key": apikey}
        r = requests.get(endpoint, params)
        credit = int(r.text)
    if api_name == "valueserp":
        endpoint = "https://api.valueserp.com/account"
        params = {"api_key": apikey}
        r = requests.get(endpoint, params)
        r_dict = r.json()
        credit = r_dict["account_info"]["monthly_credits_remaining"]
    if credit < 1000:
        fprint("error", "credt limit reached, contact seo team for more credits")
        sys.exit()
    else:
        fprint("info", f"{credit} credit points left for the {api_name} api")
    return credit

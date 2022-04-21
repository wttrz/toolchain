import sys
from src.authentication import get_api_key, get_api_credit


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

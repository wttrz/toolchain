import os
import sys
import requests


def get_api_key(api_name):
    if api_name not in ["semrush", "valueserp"]:
        sys.exit(f"[error] {api_name} is not supported")
    if api_name == "semrush":
        return os.environ.get("SEMRUSHKEY")
    if api_name == "valueserp":
        return os.environ.get("VALUESERPKEY")


def get_api_credit(api_name):
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
        sys.exit(f"credit limit reached, get in touch to get more credits")
    else:
        print(f"{credit} credit points left for the {api_name} api")
    return credit

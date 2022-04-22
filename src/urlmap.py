import io
import pandas as pd
import sys
import requests
from src.authentication import get_api_key, get_api_credit


def get_domain_queries(domain, database, limit):
    apikey = get_api_key("semrush")
    get_api_credit("valueserp")
    databases = ["SE", "NO", "DK", "FI", "UK", "US"]
    if database.upper() not in databases:
        sys.exit("[error] unsupported database")
    url = f"https://api.semrush.com/?type=domain_organic&key={apikey}"
    export_columns = f"&export_columns=Ph,Ur,Po,Nq&domain={domain}"
    display = f"&display_sort=nq_desc&display_limit={limit}&database={database}"
    api_call = url + export_columns + display
    return requests.get(api_call)


def set_score(data):
    ctr = {
            1: 0.329, 2: 0.1534, 3: 0.0897, 4: 0.0594, 5: 0.0417,
            6: 0.0305, 7: 0.0228, 8: 0.0177, 9: 0.0143, 10: 0.0117,
            11: 0.0101, 12: 0.01, 13: 0.0104, 14: 0.0104, 15: 0.01,
            16: 0.0089, 17: 0.0084, 18: 0.0075, 19: 0.0072, 20: 0.0064
            }
    data["position"] = round(data["position"], 0)
    data["search volume"] = round(data["search volume"], 0)
    data["ctr"] = round(data["position"].map(ctr).fillna(0), 2)
    data["score"] = round((data["search volume"] * data["ctr"]) / data["position"], 2)
    pairs = data.groupby("keyword").head(1).sort_values("score", ascending=False)
    output = pairs[(pairs["position"].isnull()) | (pairs["position"] <= 20)].copy()
    output["url"].fillna("no mapping - create new page", inplace=True)
    return output.reset_index(drop=True).fillna(0)


def map_domain(domain, database, limit, upload, fpath):
    response = get_domain_queries(domain, database, limit)
    if "NOTHING" in response.text:
        empty_data = pd.DataFrame(columns=["keyword"])
        empty_data.to_csv(fpath)
        sys.exit("[error] no data found in semrush")
    api_data = pd.read_csv(io.StringIO(response.text), header=0, sep=";")
    api_data.columns = api_data.columns.str.lower()
    if upload:
        upload_dataframe = pd.DataFrame(upload, columns=["keyword"])
        merged = upload_dataframe.merge(api_data, on="keyword", how="outer")
        mapped = set_score(merged)
    else:
        mapped = set_score(api_data)
    mapped.to_csv(fpath)
    return mapped

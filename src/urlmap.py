"""
Map queries to individual pages.

This algorithm finds which page has the highest potential to be optimized for a given keyword.
Given a list of keywords and a domain, it maps each keyword with the page with the best score.

By default, the algorithm collects all the keywords associated with the domain from SEMRush.

The page score is computed using Search Volume, CTR and (keyword) Position.

> score = (search volume * ctr) / position

Only keywords for which the domain ranks between position 1 to 20 are mapped.

The rows option determines how many rows to retrieve from the SEMRush database.
This can be useful to test the output or save SEMRush credits.

When providing a file with keywords, it is mapped against all the keywords in the database.
The output always contains the SEMRush data as well, use --no-semrush to skip that data.
The --no-semrush option only works when a file of keywords have been provided.

When a keyword is not found in the database, the algorithm suggests creating a new page.
The domain might still be ranking for the term, however, SEMRush has no data for it.
Either way, the algorithm recommends creating new content to target the keyword.

The --remove option can be used to filter the SEMRush data.
Patterns with slashes e.g., '/path' or '/path/' will exclude pages containing the 'path'.
Patterns without slashes e.g., 'term' will exclude keywords containing the 'term'.
"""

import io
import sys
from pathlib import Path
from typing import List

import pandas as pd

from src.apicalls import query_semrush
from src.formatting import fprint


def set_score(data: pd.DataFrame) -> pd.DataFrame:
    # FIXME: see if it'd be possible to model the ctr distribution to generate expected ctr values past the top twenty positions
    ctr = {
        1: 0.329,
        2: 0.1534,
        3: 0.0897,
        4: 0.0594,
        5: 0.0417,
        6: 0.0305,
        7: 0.0228,
        8: 0.0177,
        9: 0.0143,
        10: 0.0117,
        11: 0.0101,
        12: 0.01,
        13: 0.0104,
        14: 0.0104,
        15: 0.01,
        16: 0.0089,
        17: 0.0084,
        18: 0.0075,
        19: 0.0072,
        20: 0.0064,
    }
    data["position"] = round(data["position"], 0)
    data["search volume"] = round(data["search volume"], 0)
    data["ctr"] = round(data["position"].map(ctr).fillna(0), 2)
    data["score"] = round((data["search volume"] * data["ctr"]) / data["position"], 2)
    pairs = data.groupby("keyword").head(1).sort_values("score", ascending=False)
    output = pairs[(pairs["position"].isnull()) | (pairs["position"] <= 20)].copy()
    output["url"].fillna("unmapped - create new page", inplace=True)
    return output.reset_index(drop=True)


def map_domain(domain: str, database: str, rows: int, upload: str, fpath: Path, semrush: bool, cut: List[str]) -> pd.DataFrame:
    if any(x in domain for x in ["http", "www"]):
        fprint("error", "domain should not contain http(s) or www")
        sys.exit()
    fprint("info", f"mapping keywords to {domain} - location: {database}")
    response = query_semrush(domain, database, rows)
    if "NOTHING" in response.text:
        empty_data = pd.DataFrame(columns=["keyword"])
        empty_data.to_csv(fpath)
        fprint("error", f"no data found in semrush for {domain}")
        sys.exit()
    api_data = pd.read_csv(io.StringIO(response.text), header=0, sep=";")
    api_data.columns = api_data.columns.str.lower()
    if cut:
        regex_paths = "|".join([i.replace("/", "") for i in cut if "/" in i])
        regex_keywords = "|".join([i for i in cut if "/" not in i])
        cut_paths = regex_paths if regex_paths != "" else None
        cut_keywords = regex_keywords if regex_keywords != "" else None
        if cut_paths:
            api_data = api_data.loc[~api_data["url"].str.contains(cut_paths)]
        if cut_keywords:
            api_data = api_data.loc[~api_data["keyword"].str.contains(cut_keywords)]
    mapped = pd.DataFrame()
    if upload:
        upload_data = pd.DataFrame(upload, columns=["keyword"])
        merged = upload_data.merge(api_data, on="keyword", how="outer", indicator=True)
        mapped = set_score(merged)
        if semrush is False:
            mapped = mapped[mapped["_merge"].str.contains("both|left_only")]
    else:
        mapped = set_score(api_data)
    if "_merge" in mapped:
        mapped.drop(columns=["_merge"], inplace=True)
    mapped.to_csv(fpath)
    fprint("info", f"mapping completed ~ find your output @ {fpath}")
    return mapped.fillna(0)

"""
Cluster a list of keywords.

This algorithm computes the pairwise editing distance between each keyword.
The editing distance measures how different any two keywords are from each other.
The higher the number, the more different the keywords are.

Then, it clusters the keywords similarities using the Affinity Propagation algorithm.
Affinity Propagation is a clustering algorithm that generates clusters automatically.
It finds exemplars in the dataset (representative elements) and creates clusters around them.
It outputs a one-level clustering output that works on keyword lists in any language.

A higher damping factor makes the algorithm slower but might increase cluster accuracy.
The algorithm is not always perfect and might mislabel some keywords. Review the output.

References:

> http://genes.toronto.edu/affinitypropagation/faq.html
> https://en.wikipedia.org/wiki/Levenshtein_distance
> https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
"""

import itertools
import sys
from pathlib import Path
from typing import Any, List

import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation

from src.formatting import fprint


def levenshtein(string1: str, string2: str) -> int:
    fprint("info", f"calculating distance between {string1} -> {string2}")
    n = len(string1)
    m = len(string2)
    d = [[0 for x in range(n + 1)] for y in range(m + 1)]
    for i in range(1, m + 1):
        d[i][0] = i
    for j in range(1, n + 1):
        d[0][j] = j
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if string1[j - 1] is string2[i - 1]:
                delta = 0
            else:
                delta = 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + delta)
    return d[m][n]


def cluster_keywords(searches: List[str], damping: float, fpath: Path) -> pd.DataFrame:
    words: np.ndarray[Any, Any] = np.asarray(searches)
    if damping < 0.5 or damping > 1.0:
        fprint("error", "the damping factor should be a number between 0.5 and 1.0")
        sys.exit()
    fprint("info", f"computing levenshtein similarity for {len(words)} keywords")
    distance_matrix = -1 * np.array([[levenshtein(w1, w2) for w1 in words] for w2 in words])
    affprop = AffinityPropagation(affinity="precomputed", damping=damping, max_iter=1000)
    affprop.fit(distance_matrix)
    datasets = list()
    fprint("info", "applying labels to clusters")
    for label in np.unique(affprop.labels_):
        exemplar = searches[affprop.cluster_centers_indices_[label]]
        cluster: np.ndarray[Any, Any] = np.unique(words[np.nonzero(affprop.labels_ == label)])
        zipped = list(zip(cluster, itertools.cycle([exemplar])))
        data = pd.DataFrame(zipped, columns=["keywords", "cluster"])
        datasets.append(data)
    dataframe = pd.concat(datasets, ignore_index=True)
    dataframe.to_csv(fpath)
    fprint("info", f"clustering completed ~ find your output @ {fpath}")
    return dataframe

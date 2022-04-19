"""
This clustering operation works on lists of keywords. 

The algorithm computes the pairwise Levenshtein or Damerau-Levenshtein distance between each keyword.
This distance measures the difference between strings, i.e., how different the strings are.
Think of it as the editing distance between them. The lower, the number, the closer the strings.

Once the keywords have been turned into numbers, they're clustered using the Affinity Propagation algorithm.
The output is a one-level clustering scheme that works on keyword lists in any language.

Levenshtein and Damerau-Levenshtein are pretty similar, the default Levenshtein will work most of the time.
The damping factor should be between 0.5 and 1.0 and, the higher it is, the more clusters will be formed.
"""

import io
import sys
import itertools
import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation


def levenshtein(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for idx2, char2 in enumerate(s2):
        new_distances = [idx2 + 1]
        for idx1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[idx1])
            else:
                new_distances.append(
                    1
                    + min(
                        (
                            distances[idx1],
                            distances[idx1 + 1],
                            new_distances[-1],
                        )
                    )
                )
        distances = new_distances
    return distances[-1]


def damerau(s1, s2):
    d = dict()
    len_str1 = len(s1)
    len_str2 = len(s2)
    for i in range(-1, len_str1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len_str2 + 1):
        d[(-1, j)] = j + 1
    for i in range(len_str1):
        for j in range(len_str2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost,
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)
    return d[len_str1 - 1, len_str2 - 1]


def cluster_keywords(searches, similarity, damping, fpath):
    words = np.asarray(searches)
    if similarity != "leven" and similarity != "damerau":
        sys.exit("The similarity metric should be either leven or damerau.")
    if damping < 0.5 or damping > 1.0:
        sys.exit("The damping factor should be between 0.5 and 1.0")
    if similarity == "leven":
        print(f"computing levenshtein similarity for {len(words)} keywords ...")
        distance_matrix = -1 * np.array(
            [[levenshtein(w1, w2) for w1 in words] for w2 in words]
        )
    if similarity == "damerau":
        print(f"computing damerau similarity for {len(words)} keywords ...")
        distance_matrix = -1 * np.array(
            [[damerau(w1, w2) for w1 in words] for w2 in words]
        )
    affprop = AffinityPropagation(
        affinity="precomputed", damping=damping, max_iter=1000
    )
    affprop.fit(distance_matrix)
    datasets = list()
    print("applying labels ...")
    for label in np.unique(affprop.labels_):
        exemplar = searches[affprop.cluster_centers_indices_[label]]
        cluster = np.unique(
            words[np.nonzero(affprop.labels_ == label)]
        )
        zipped = list(zip(cluster, itertools.cycle([exemplar])))
        data = pd.DataFrame(zipped, columns=["keywords", "cluster"])
        datasets.append(data)
    dataframe = pd.concat(datasets, ignore_index=True)
    dataframe.to_csv(fpath)
    return dataframe

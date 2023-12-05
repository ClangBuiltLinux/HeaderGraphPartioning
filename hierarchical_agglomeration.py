import sys
from collections import defaultdict
import json
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from lib.graph_utils import extract_symbols_from_file

def compute_proximity(header_filename, c_filenames):
    with open(c_filenames) as json_data:
        header_symbols = extract_symbols_from_file(header_filename, [], header=True)
        proximity = defaultdict(int)
        data = json.load(json_data)["data"]
        for sym1 in header_symbols:
            for sym2 in header_symbols:
                if sym1 != sym2 and sym1 in data and sym2 in data:
                    pairings = set(data[sym1]).intersection(set(data[sym2]))
                    if pairings:
                        proximity[(sym1, sym2)] = len(pairings)
    return proximity

def create_distance_matrix(proximity, symbols):
    n = len(symbols)
    LARGE_VALUE = 2
    matrix = np.full((n, n), LARGE_VALUE)
    print(symbols, n)
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0
            else:
                pair = (symbols[i], symbols[j])
                if pair in proximity:
                    matrix[i][j] = 1 / proximity[pair]

    return matrix


def hierarchical_clustering(proximity):
    symbols = list(extract_symbols_from_file(header_filename, [], header=True))
    distance_matrix = create_distance_matrix(proximity, symbols)
    linked = linkage(distance_matrix, method='average')
    
    plt.figure(figsize=(10, 7))
    dendrogram(linked, orientation='top', labels=symbols, distance_sort='descending')
    plt.show()

    clusters = fcluster(linked, 2, criterion='maxclust')
    symbol_to_cluster = {symbols[i]: cluster_id for i, cluster_id in enumerate(clusters)}

    return symbol_to_cluster

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <header_filename> <compile_commands.json>")
        sys.exit(1)

    header_filename = Path(sys.argv[1])
    c_filenames = Path(sys.argv[2])
    proximity = compute_proximity(header_filename, c_filenames)

    sorted_data = sorted([(count, sym1, sym2) for (sym1, sym2), count in proximity.items()], reverse=True)
    for count, sym1, sym2 in sorted_data:
        print(f"Proximity SYM:{sym1} - SYM:{sym2}: {count}")

    clusters = hierarchical_clustering(proximity)
    for symbol, cluster_id in clusters.items():
        print(f"Symbol {symbol} is in cluster {cluster_id}")

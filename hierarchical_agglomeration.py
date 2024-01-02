import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt

from lib.graph_utils import extract_symbols_from_file

DEBUG = False

def compute_proximity(header_filename: Path, c_filenames: Path) -> Dict[Tuple[str, str], int]:
    '''finds number of times all symbols in a header appear in the same file and outputs a dict
    of tuples with the number of occurrences as the value'''
    with open(c_filenames, encoding="utf-8") as json_data:
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

def create_distance_matrix(proximity: Dict[Tuple[str, str], int],
                           symbols: List[str]) -> np.ndarray:
    '''Creates a distance matrix where each edge i,j =
    1/(num_occcurences of i and j in the same c file) or 2 if not'''
    n = len(symbols)
    large_val = 2
    matrix = np.full((n, n), large_val)

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0
            else:
                pair = (symbols[i], symbols[j])
                if pair in proximity:
                    matrix[i][j] = 1 / proximity[pair]

    return matrix


def hierarchical_clustering(proximity: Dict[Tuple[str, str], int], header_filename: Path, method_name: str):
    '''Generates a graph from the proxiimity of the symbols to partition them into two groups'''
    symbols = list(extract_symbols_from_file(header_filename, [], header=True))
    distance_matrix = create_distance_matrix(proximity, symbols)
    linked = linkage(distance_matrix, method=method_name)

    plt.figure(figsize=(10, 7))
    dendrogram(linked, orientation='top', labels=symbols, distance_sort='descending')
    plt.title(f'Hierarchical Agglomeration of Symbols in {header_filename}')
    plt.savefig('filename.png')

    clusters = fcluster(linked, 2, criterion='maxclust')
    symbol_to_cluster = {symbols[i]: cluster_id for i, cluster_id in enumerate(clusters)}

    return symbol_to_cluster

def main():
    global DEBUG
    parser = argparse.ArgumentParser(description='''This script finds the occurrences of
                                     tokens in a compile_commands.json.''')
    parser.add_argument('-c', '--commands', type=Path, required=True,
                        help='Path to compile_commands.json')
    parser.add_argument('-f', '--header_filename', type=Path, required=True,
                        help='Path to header')
    parser.add_argument('-m', '--method', default='average',
                        help='Linkage method can be average, single, complete,' +
                        'weighted, centroid, median, or ward')
    parser.add_argument('-d', action='store_true',
                        help='Debug mode on.')
    args = parser.parse_args()

    header_filename = args.header_filename
    c_filenames = args.commands
    DEBUG = args.d

    proximity = compute_proximity(header_filename, c_filenames)

    if DEBUG:
        sorted_data = sorted([(count, sym1, sym2) for (sym1, sym2), count in proximity.items()],
                             reverse=True)
        for count, sym1, sym2 in sorted_data:
            print(f"Proximity SYM:{sym1} - SYM:{sym2}: {count}")

    clusters = hierarchical_clustering(proximity, header_filename, args.method)
    if DEBUG:
        for symbol, cluster_id in clusters.items():
            print(f"Symbol {symbol} is in cluster {cluster_id}")

if __name__ == "__main__":
    main()

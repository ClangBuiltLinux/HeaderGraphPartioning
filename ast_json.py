import argparse
from collections import defaultdict
import json
from pathlib import Path
import os
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

from pydantic import BaseModel
from lib.graph_utils import extract_symbols_from_file


class DataModel(BaseModel):
    data: Dict[str, List[str]]


def process_file(row: Dict[str, str]) -> str:
    c_file = Path(row["file"])
    # This takes everything between clang and -o not inclusive
    # TODO: Remove Magic constants
    flags = row["command"].split()[1:-4]
    os.chdir(row["directory"])
    c_file_symbols = extract_symbols_from_file(c_file, flags)
    # Strips absolute path ie a/b/c/linux/include/linux -> include/linux
    pieces = "linux".join(str(c_file).split("linux")[1:])
    return (pieces, c_file_symbols)


def compute_usage(c_commands: Path):
    result = []
    with open(c_commands, encoding="utf-8") as json_data:
        data = json.load(json_data)
        rows = list(data)
        workers = len(os.sched_getaffinity(0))
        with ProcessPoolExecutor(max_workers=workers // 2 + 1) as executor:
            futures = [executor.submit(process_file, row) for row in rows]
            for future in as_completed(futures):
                result.append(future.result())
    return result


def parse_file(data: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    inverted_dict = defaultdict(list)
    for file, symbols in data:
        for value in symbols:
            value = value.strip()
            if value == "":
                continue
            inverted_dict[value].append(file)
    return inverted_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""This script formats an ast-dump from
                                     process_ast.py into a json file."""
    )
    parser.add_argument(
        "-c",
        "--commands",
        type=Path,
        required=True,
        help="Path to compile_commands.json",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=Path,
        default="outfile.json",
        help="Name of the output json",
    )
    args = parser.parse_args()
    parsed_data = parse_file(compute_usage(args.commands))
    model = DataModel(data=parsed_data)
    model_json = model.json()
    with open(args.outfile, "w", encoding="utf-8") as out_file:
        out_file.write(model_json)

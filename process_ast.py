import argparse
import json
import os

from pathlib import Path
from typing import Dict
from concurrent.futures import ProcessPoolExecutor, as_completed
from lib.graph_utils import extract_symbols_from_file

def process_file(row: Dict[str, str]) -> str:
    c_file = row["file"]
    flags = row["command"].split()[1:-4]
    os.chdir(row["directory"])
    c_file_symbols = extract_symbols_from_file(c_file, flags)
    pieces = "linux".join(c_file.split("linux")[1:])
    return f"{pieces} : {c_file_symbols}".replace("'", "")

def compute_usage(c_commands: Path):
    with open(c_commands, encoding="utf-8") as json_data:
        data = json.load(json_data)
        rows = list(data)
        workers = len(os.sched_getaffinity(0))
        with ProcessPoolExecutor(max_workers = workers // 2 + 1) as executor:
            futures = [executor.submit(process_file, row) for row in rows]
            for future in as_completed(futures):
                print(future.result())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''This script suggests an automatic partition of a
                                    header file.''')
    parser.add_argument('-c', '--commands', type=Path, required=True,
                        help='Path to compile_commands.json')

    args = parser.parse_args()
    compile_commands = args.commands
    compute_usage(compile_commands)

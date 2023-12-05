import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel

class DataModel(BaseModel):
    data: Dict[str, List[str]]


def parse_file(file_path: Path) -> Dict[str, List[str]]:
    inverted_dict = defaultdict(list)
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            data = line.strip().split(" : ")
            key, values_str = data[0], " ".join(data[1:])
            values = values_str.strip("{}").split(",")
            for value in values:
                value = value.strip()
                if value == "":
                    continue
                inverted_dict[value].append(key)
    return inverted_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''This script formats an ast-dump from
                                     process_ast.py into a json file.''')
    parser.add_argument("-f", "--file", type=Path, required=True,
                        help="Path to the ast_dump")
    parser.add_argument("-o", "--outfile", type=Path, default="outfile.json",
                        help="Name of the output json")
    args = parser.parse_args()
    parsed_data = parse_file(args.file)
    model = DataModel(data=parsed_data)
    json_data = model.json()
    with open(args.outfile, "w", encoding="utf-8") as out_file:
        out_file.write(json_data)

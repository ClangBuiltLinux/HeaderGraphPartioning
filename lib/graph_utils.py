"""functions used in performing hierarchical agglomeration"""
from pathlib import Path
from typing import List, Set
from clang.cindex import Index, CursorKind

usable_types = frozenset(
    {
        CursorKind.STRUCT_DECL,
        CursorKind.ENUM_DECL,
        CursorKind.TYPEDEF_DECL,
        CursorKind.FUNCTION_DECL,
        CursorKind.MACRO_DEFINITION,
        CursorKind.FIELD_DECL,
    }
)


def extract_symbols_from_file(
    filename: Path, flags: List[str], header=False
) -> Set[str]:
    """Obtains all the ast-nodes from filename built with flags"""
    index = Index.create()
    translation_unit = index.parse(str(filename), args=flags)
    symbols = set()

    def visit_node(node, depth=0):
        """Recursively crawls AST and adds relevant nodes"""
        if not header:
            name = node.spelling

            if depth == 0 or (filename.name in str(node.location.file)):
                symbols.add(name)
                for child in node.get_children():
                    visit_node(child, 1)

        else:
            name = node.spelling

            if node.kind in usable_types and filename.name in str(node.location.file):
                symbols.add(name)

            if node.kind in [
                CursorKind.STRUCT_DECL,
                CursorKind.UNION_DECL,
                CursorKind.FUNCTION_DECL,
            ]:
                # Stops us from recursing too deep because we don't care for headers
                return

            for child in node.get_children():
                visit_node(child, 1)

    visit_node(translation_unit.cursor)
    return symbols

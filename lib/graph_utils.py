from pathlib import Path
from typing import List, Set
from clang.cindex import Index, CursorKind

def extract_symbols_from_file(filename: Path, flags: List[str], header = False) -> Set[str]:
    '''Obtains all the ast-nodes from filename built with flags'''
    index = Index.create()
    translation_unit = index.parse(str(filename), args = flags)
    seentwice = set()
    symbols = set()

    usable_types = {
        CursorKind.STRUCT_DECL, CursorKind.ENUM_DECL, CursorKind.TYPEDEF_DECL,
        CursorKind.CLASS_DECL, CursorKind.VAR_DECL, CursorKind.FUNCTION_DECL,
        CursorKind.MACRO_DEFINITION, CursorKind.FIELD_DECL
    }

    def visit_node(node):
        '''Recursively crawls AST and adds relevant nodes'''
        if not header and node.kind in usable_types:
            name = node.spelling
            if ".c" in str(node.location.file) or name in symbols:
                seentwice.add(name)
            else:
                symbols.add(name)

        if header and node.kind in usable_types:
            name = node.spelling
            symbols.add(name)

        for child in node.get_children():
            visit_node(child)

    visit_node(translation_unit.cursor)
    return symbols

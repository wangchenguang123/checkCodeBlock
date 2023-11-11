from tree_sitter_parser.TreeSitterInit import TreeSitterParser
from tree_sitter_parser.domain import get_all_function_names
from utils.FileUtils import read_file_as_string

so_path = "/datapro/wcg/build/my-languages.so"


def check_new_file_type(filepath):
    """
    Check the type of a file based on its extension.

    Parameters:
    - filepath (str): The path to the file.

    Returns:
    - str: The file type, or 'other' if the type is not recognized.
    """
    tree_sitter_parser = TreeSitterParser(so_path)
    if filepath.endswith(".h") or filepath.endswith('.c'):
        return tree_sitter_parser.get_c_parser()
    elif filepath.endswith('.cpp') or filepath.endswith('.cc') or filepath.endswith('.hpp'):
        return tree_sitter_parser.get_cpp_parser()
    elif filepath.endswith('.java'):
        return tree_sitter_parser.get_java_parser()
    elif filepath.endswith('.py'):
        return tree_sitter_parser.get_py_parser()
    else:
        return None


def get_source_code_ast(source_code, tree_sitter_parser):
    if source_code and tree_sitter_parser:
        return tree_sitter_parser.parse(bytes(source_code, 'utf-8'))


if __name__ == '__main__':
    source_code = read_file_as_string("/datapro/wcg/resource/s_loongarch.h")
    tree_sitter_parser = check_new_file_type("/datapro/wcg/resource/s_loongarch.h")
    ast_tree = get_source_code_ast(source_code, tree_sitter_parser)
    print(get_all_function_names(ast_tree.root_node, source_code))

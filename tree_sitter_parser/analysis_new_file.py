from tree_sitter_parser.TreeSitterInit import TreeSitterParser
from tree_sitter_parser.domain import get_all_function_names, get_function_body
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


# def get_same_struct_file(source_code,function_name_list):

if __name__ == '__main__':
    source_code = read_file_as_string("/datapro/wcg/resource/s_loongarch.h")
    tree_sitter_parser = check_new_file_type("/datapro/wcg/resource/s_loongarch.h")
    ast_tree = get_source_code_ast(source_code, tree_sitter_parser)
    function_names = get_all_function_names(ast_tree.root_node, source_code)
    # # print(get_all_function_definitions(tree_sitter_parser, source_code))
    # print(function_names)
    # for fun in function_names:
    #     print(get_function_body(ast_tree,source_code,fun,"c"))

    origin_same_code = read_file_as_string("/datapro/wcg/resource/s_x86_64.h")
    tree_sitter_parser_origin = check_new_file_type("/datapro/wcg/resource/s_x86_64.h")
    ast_tree_origin = get_source_code_ast(origin_same_code, tree_sitter_parser_origin)
    for fun in function_names:
        print(get_function_body(ast_tree_origin, origin_same_code, fun, "c"))
    # print(origin_same_code)

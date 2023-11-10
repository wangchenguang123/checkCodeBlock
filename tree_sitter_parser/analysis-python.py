import tree_sitter

from tree_sitter_parser.business import find_functions_with_arch_words
from tree_sitter_parser.domain import get_up_node_for_assignment, get_all_class_definitions, get_up_node_for_function, \
    get_up_node_for_class, find_code_lines, get_nodes_list_within_start_end, find_preproc_if_binary_expressions_python, \
    get_block_function_parent, get_elif_sibling_node_list_in_fun_python, get_same_sibling_node_code_list, \
    get_target_code_function_name, get_all_function_names, get_function_body, get_target_code_class_name, \
    get_class_definition_body

py_LANGUAGE = tree_sitter.Language('build/my-languages.so', 'python')
py_parser = tree_sitter.Parser()
py_parser.set_language(py_LANGUAGE)

with open('fileresource/test.py', 'r') as file:
    code = file.read()
source_p = py_parser.parse(bytes(code, 'utf-8'))
archWord = []


def find_class_with_arch_words(class_names):
    pass


def analysis_py(target_code, source_code):
    source_p = py_parser.parse(bytes(source_code, 'utf-8'))
    target_p = py_parser.parse(bytes(target_code, 'utf-8'))
    lines = find_code_lines(target_code, source_code)
    print(lines)
    loongarch_code = ""
    for line in lines:
        start_line = line[0] - 1
        end_line = line[1] - 1
        node_type_list = get_nodes_list_within_start_end(source_p.root_node, start_line, end_line)
        print(node_type_list)
        if node_type_list[0].type in ["if_statement", "expression_statement", "return_statement"]:
            loongarch_code = get_up_node_for_function(node_type_list[0])
            if not loongarch_code:
                loongarch_code = get_up_node_for_class(node_type_list[0])
            print(loongarch_code)
        elif node_type_list[0].type == "call" or node_type_list[0].type == "not_operator":
            bi_list = find_preproc_if_binary_expressions_python(source_p.root_node, start_line, end_line)
            if bi_list:
                for bi in bi_list:
                    if bi.type == "if_statement":
                        loongarch_code = get_up_node_for_function(bi)
                    else:
                        loongarch_code = bi.text.decode()
            else:
                loongarch_code = get_up_node_for_assignment(node_type_list[0])
            if not loongarch_code:
                print(11)
                loongarch_code = get_up_node_for_function(node_type_list[0])
            print(loongarch_code)
        elif node_type_list[0].type == "block":
            loongarch_code = get_block_function_parent(node_type_list[0])
            print(loongarch_code)
        elif node_type_list[0].type == "elif_clause":  ## 存在问题
            sibling_node_list = get_elif_sibling_node_list_in_fun_python(node_type_list[0])
            code_list = get_same_sibling_node_code_list(source_code, sibling_node_list)
            for code in code_list:
                print("---------------------------------------------------------------------")
                print(code)
        elif node_type_list[0].type == "function_definition":
            function_name = get_target_code_function_name(target_code, target_p)
            if function_name:
                for key in archWord:
                    if function_name.find(key) > -1:
                        function_names = get_all_function_names(source_p.root_node, source_code)
                        if function_names:
                            analysis_function_names = find_functions_with_arch_words(function_names)
                            for analysis_function_name in analysis_function_names:
                                code_body = get_function_body(source_p, source_code,
                                                              analysis_function_name.get("function_name"))
                                code_map = {"arch_word": analysis_function_name.get("architectures")[0],
                                            "code_body": code_body}
                                print(code_map)
        elif node_type_list[0].type in ["pair", "list", "set", "tuple", "string", "keyword_argument"]:
            loongarch_code = get_up_node_for_assignment(node_type_list[0])
            print(loongarch_code)
        elif node_type_list[0].type == "class_definition":
            class_name = get_target_code_class_name(node_type_list)
            if class_name:
                for key in archWord:
                    if class_name.find(key) > -1:
                        class_names = get_all_class_definitions(source_p.root_node, source_code)
                        if class_names:
                            analysis_class_names = find_class_with_arch_words(class_names)
                            for analysis_class_name in analysis_class_names:
                                code_body = get_class_definition_body(source_p, source_code,
                                                                      analysis_class_name.get("function_name"))
                                code_map = {"arch_word": analysis_class_name.get("architectures")[0],
                                            "code_body": code_body}
                                print(code_map)

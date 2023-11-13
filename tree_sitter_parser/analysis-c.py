import tree_sitter

from tree_sitter_parser.domain import find_code_lines, get_nodes_list_within_start_end, get_node_with_start_row, \
    is_in_fun, get_elif_sibling_node_list_in_fun_c, get_elif_sibling_node_list_out_fun, get_same_sibling_node_code_list

C_LANGUAGE = tree_sitter.Language('build/my-languages.so', 'c')
c_parser = tree_sitter.Parser()
c_parser.set_language(C_LANGUAGE)


def analysis_c(target_code, source_code):
    source_p = c_parser.parse(bytes(source_code, 'utf-8'))
    target_p = c_parser.parse(bytes(target_code, 'utf-8'))
    lines = find_code_lines(target_code, source_code)
    loongarch_code = ""
    for line in lines:
        start_line = line[0] - 1
        end_line = line[1] - 1
        node_type_list = get_nodes_list_within_start_end(source_p.root_node, start_line, end_line)
        print(node_type_list)
        if node_type_list[0].type in ["preproc_elif", "preproc_ifdef", "#elif"]:
            node = get_node_with_start_row(source_p.root_node, start_line)
            is_in = is_in_fun(node)
            if is_in:
                sibling_node_list, function_name = get_elif_sibling_node_list_in_fun_c(node, node.type, "c")
            else:
                sibling_node_list = get_elif_sibling_node_list_out_fun(node, node.type)
            if sibling_node_list:
                print(sibling_node_list)
                code_list = get_same_sibling_node_code_list(source_code, sibling_node_list)
                for code in code_list:
                    print("---------------------------------------------------------------------")
                    print(code)

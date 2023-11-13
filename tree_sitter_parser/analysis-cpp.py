import tree_sitter

from tree_sitter_parser.business import find_functions_with_arch_words
from tree_sitter_parser.domain import get_function_body, get_all_function_names, get_elif_sibling_node_list_out_fun, \
    get_same_sibling_node_code_list, get_elif_sibling_node_list_in_fun_cpp, is_in_fun, get_up_node_for_function, \
    get_nodes_list_within_start_end, find_code_lines

CPP_LANGUAGE = tree_sitter.Language('D:\\checkCodeBlock\\build\\my-languages.so', 'cpp')
cpp_parser = tree_sitter.Parser()
cpp_parser.set_language(CPP_LANGUAGE)

archWord = ['aarch64', 'amd64', 'arm64', 'i386', 'i486', 'i586', 'i686', 'i786', 'i886', 'i986', 'ia32', 'ia64', 'm68k',
            'mc68000', 'mips64', 'powerpc64', 'ppc', 'powerpc64le', 'riscv', 's390', 's390x', 'sparc', 'arm32',
            'x86_64', 'ppc64', 'loongarch', 'loongarch64']


def analysis_cpp(target_code, source_code):
    source_p = cpp_parser.parse(bytes(source_code, 'utf-8'))
    target_p = cpp_parser.parse(bytes(target_code, 'utf-8'))
    lines = find_code_lines(target_code, source_code)
    print(lines)
    loongarch_code = ""
    for line in lines:
        start_line = line[0] - 1
        end_line = line[1] - 1
        node_type_list = get_nodes_list_within_start_end(source_p.root_node, start_line, end_line)
        # print(node_type_list)
        if node_type_list[0].type == "#if":
            loongarch_code = get_up_node_for_function(node_type_list[0])
            print(loongarch_code)
        elif node_type_list[0].type == "preproc_if" or node_type_list[0].type == "#elif":
            is_in = is_in_fun(node_type_list[0])
            if is_in:
                if node_type_list[0].type == "#elif":
                    sibling_node_list, function_name = get_elif_sibling_node_list_in_fun_cpp(node_type_list[0].parent)
                else:
                    sibling_node_list, function_name = get_elif_sibling_node_list_in_fun_cpp(node_type_list[0])
            else:
                sibling_node_list = get_elif_sibling_node_list_out_fun(node_type_list[0], node_type_list[0].type)
            if sibling_node_list:
                print(sibling_node_list)
                print(function_name)
                code_list = get_same_sibling_node_code_list(source_code, sibling_node_list)
                for code in code_list:
                    print("---------------------------------------------------------------------")
                    print(code)
        elif node_type_list[0].type == "function_definition":
            function_name = get_all_function_names(target_p.root_node, target_code)
            print(function_name)
            if function_name:
                for key in archWord:
                    if function_name.find(key) > -1:
                        function_names = get_all_function_names(source_p.root_node, source_code)
                        if function_names:
                            analysis_function_names = find_functions_with_arch_words(function_names)
                            for analysis_function_name in analysis_function_names:
                                code_body = get_function_body(source_p, source_code,
                                                              analysis_function_name.get("function_name"), "c")
                                code_map = {"arch_word": analysis_function_name.get("architectures")[0],
                                            "code_body": code_body}
                                print(code_map)

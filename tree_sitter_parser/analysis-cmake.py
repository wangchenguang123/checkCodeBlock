import tree_sitter

from tree_sitter_parser.domain import find_code_lines, get_node_with_start_row, get_elif_sibling_node_list_in_cmake, \
    get_nodes_list_within_start_end, get_same_sibling_node_code_list

CMAKE_LANGUAGE = tree_sitter.Language('E:\\WcgResearch\\build\\cmake.so', 'cmake')
c_parser = tree_sitter.Parser()
c_parser.set_language(CMAKE_LANGUAGE)


def analysis_cmake(target_code, source_code):
    source_p = c_parser.parse(bytes(source_code, 'utf-8'))
    target_p = c_parser.parse(bytes(target_code, 'utf-8'))
    lines = find_code_lines(target_code, source_code)
    print(lines)
    loongarch_code = ""
    for line in lines:
        start_line = line[0] - 1
        end_line = line[1] - 1
        node_type_list = get_nodes_list_within_start_end(source_p.root_node, start_line, end_line)
        print(node_type_list)
        if node_type_list[0].type in ["elseif_command", "if_condition", "else_command"]:
            node = get_node_with_start_row(source_p.root_node, start_line)
            sibling_node_list = get_elif_sibling_node_list_in_cmake(node, node.type)
            if sibling_node_list:
                print(sibling_node_list)
                code_list = get_same_sibling_node_code_list(source_code, sibling_node_list)
                for code in code_list:
                    print("---------------------------------------------------------------------")
                    print(code)


def print_tree(node, depth=0):
    print("  " * depth + f"{node.type} --- {node.start_point} - {node.end_point}")
    for child in node.children:
        print_tree(child, depth + 1)

# if __name__ == '__main__':
#
#     source_code = read_file_as_string("E:\\WcgResearch\\NewUtils\\CMakeLists.txt")
#     source_node = c_parser.parse(bytes(source_code, encoding='utf-8')).root_node
#     # print(source_node)
#     print(source_node)
#
#     target_code = """dep_option(SDL_LSX                 "Use LSX assembly routines" ON "SDL_ASSEMBLY;SDL_CPU_LOONGARCH64" OFF)
# dep_option(SDL_LASX                "Use LASX assembly routines" ON "SDL_ASSEMBLY;SDL_CPU_LOONGARCH64" OFF)"""
#     # print_tree(source_node)
#     analysis_cmake(target_code,source_code)

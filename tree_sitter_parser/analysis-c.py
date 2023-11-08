import tree_sitter

C_LANGUAGE = tree_sitter.Language('build/my-languages.so', 'c')
c_parser = tree_sitter.Parser()
c_parser.set_language(C_LANGUAGE)


def get_line_number(source_code, index):
    return source_code.count('\n', 0, index) + 1


def get_node_types_in_range(source_code, start_line, end_line):
    tree = c_parser.parse(bytes(source_code, "utf8"))

    function_node = find_function_definition(tree, start_line, end_line)

    if function_node:
        return {
            "type": function_node.type,
            "start_line": function_node.start_point[0] + 1,
            "end_line": function_node.end_point[0] + 1
        }

    return None


def find_function_definition(tree, start_line, end_line):
    def traverse(node):
        start = node.start_point[0]
        end = node.end_point[0]

        if start <= end_line and end >= start_line:
            if node.type == 'function_definition':
                return node
            else:
                parent = node.parent
                if parent and parent.type == 'function_definition':
                    return parent

        for child in node.children:
            result = traverse(child)
            if result:
                return result

    root_node = tree.root_node
    function_node = traverse(root_node)
    return function_node


def extract_code_in_range(source_code, start_line, end_line):
    lines = source_code.split('\n')
    code_lines = lines[start_line - 1: end_line]

    return '\n'.join(code_lines)


def find_and_extract_function_definition(source_code, start_line, end_line):
    tree = c_parser.parse(bytes(source_code, "utf8"))
    function_node = find_function_definition(tree, start_line, end_line)
    if function_node:
        start_line = function_node.start_point[0] + 1
        end_line = function_node.end_point[0] + 1
        code_snippet = extract_code_in_range(source_code, start_line, end_line)
        return code_snippet
    return None


def find_code_lines(target_code, code):
    code_lines = code.split('\n')
    target_lines = target_code.split('\n')

    line_count = 0
    matches = []
    for idx, line in enumerate(code_lines):
        line_count += 1
        if target_lines[0] in line and code_lines[idx:idx + len(target_lines)] == target_lines:
            start_line = line_count
            end_line = line_count + len(target_lines) - 1
            matches.append((start_line, end_line))

    return matches

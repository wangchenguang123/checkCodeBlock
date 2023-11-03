import tree_sitter

py_LANGUAGE = tree_sitter.Language('/datapro/wcg/build/my-languages.so', 'python')
py_parser = tree_sitter.Parser()
py_parser.set_language(py_LANGUAGE)


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
    tree = py_parser.parse(bytes(source_code, "utf8"))
    function_node = find_function_definition(tree, start_line, end_line)
    if function_node:
        start_line = function_node.start_point[0] + 1
        end_line = function_node.end_point[0] + 1
        code_snippet = extract_code_in_range(source_code, start_line, end_line)
        return code_snippet
    return None


function_names = []


def extract_function_names(node):
    if node.type == 'function_definition':
        function_name_node = node.children[1]
        function_names.append(code[function_name_node.start_byte:function_name_node.end_byte])
    for child in node.children:
        extract_function_names(child)


def get_function_body(tree, target_function_name):
    def find_function_code(node):
        if node.type == 'function_definition':
            function_name_node = node.children[1]
            function_name = code[function_name_node.start_byte:function_name_node.end_byte]
            if function_name == target_function_name:
                # 找到目标函数名，提取整个函数定义
                return code[node.start_byte:node.end_byte]

        for child in node.children:
            result = find_function_code(child)
            if result:
                return result

    return find_function_code(tree.root_node)


def find_function_containing_code(source_parser, code_to_find):
    for node in source_parser.root_node.children:
        if node.type == 'function_definition':
            function_code = code[node.start_byte: node.end_byte]
            if code_to_find in function_code:
                # Extract the function name
                function_name_node = node.children[1]
                function_name = code[function_name_node.start_byte: function_name_node.end_byte]
                print(f"Function containing code: {function_name}")


def get_target_code_type(target_code):
    target_p = py_parser.parse(bytes(target_code, 'utf-8'))
    target_root = target_p.root_node
    node = target_root.children[0]
    node_type = node.type
    if node_type == "function_definition":
        function_name_node = node.children[1]
        function_name = target_code[function_name_node.start_byte: function_name_node.end_byte]
        return function_name


def find_functions_with_arch_words(function_names):
    # List to store functions containing arch words
    functions_with_arch_words = []

    for function_name in function_names:
        arch_found = [word for word in archWord if word in function_name.lower()]
        if arch_found:
            functions_with_arch_words.append({'function_name': function_name, 'architectures': arch_found})

    return functions_with_arch_words

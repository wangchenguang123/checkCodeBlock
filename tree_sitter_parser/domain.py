from tree_sitter_parser.TreeSitterInit import TreeSitterParser
from utils.FileUtils import read_file_as_string

so_path = "/datapro/wcg/build/my-languages.so"

def get_parser(filepath):
    treesitter = TreeSitterParser(so_path)
    if filepath.endswith(".c") or filepath.endswith(".h"):
        return treesitter.get_c_parser()
    elif filepath.endswith(".py"):
        return treesitter.get_py_parser()
    elif filepath.endswith(".java"):
        return treesitter.get_java_parser()
    elif filepath.endswith(".cpp") or filepath.endswith(".hpp"):
        return treesitter.get_cpp_parser()

def get_source_code(filepath):
    data = read_file_as_string(filepath)
    return data

def get_target_code_type_list(target_parser):
    # target_p = sitter_parser.parse(bytes(target_code, 'utf-8'))
    target_root = target_parser.root_node
    child_type_list = target_root.children
    return child_type_list

def choose_first_type(type_list):
    if len(type_list) > 0:
        return type_list[0]

def do_error_type(node):
    if node.type == 'ERROR':
        return True

def get_same_sibling_node_code_list(source_code, node_list):
    code_list = []
    start_row_list = []  # 获取所有结点的 start_row
    for node in node_list:
        start_row_list.append(node.start_point[0])
    start_row_list.append(node_list[0].end_point[0])  # 添加最后一行的行数
    start_row_list = sorted(start_row_list)  # 排序
    c_code_list = source_code.split("\n")
    for i in range(len(start_row_list) - 1):
        c = ""
        for e in c_code_list[start_row_list[i]:start_row_list[i + 1]]:
            c += e + "\n"
        code_list.append(c)
    return code_list

def get_function_name_cpp(node):
    while node:
        if node.type == 'function_definition':
            function_name_node = None
            for child in node.children:
                if child.type == 'function_declarator':
                    function_name_node = child
                    break
            if function_name_node:
                for child in function_name_node.children:
                    if child.type == 'qualified_identifier':
                        return child.text.decode()
                    if child.type == 'identifier':
                        return child.text.decode()
            break
        node = node.parent
    return None

def get_function_name_c(node):
    while node:
        if node.type == 'function_definition':
            function_name_node = None
            for child in node.children:
                if child.type == 'function_declarator':
                    function_name_node = child
                    break
            if function_name_node:
                for child in function_name_node.children:
                    if child.type == 'identifier':
                        return child.text
            break
        node = node.parent
    return None


def check_function_name(node, is_c_or_cpp):
    if is_c_or_cpp == "c":
        return get_function_name_c(node)
    elif is_c_or_cpp == "cpp":
        return get_function_name_cpp(node)


def get_elif_sibling_node_list_in_fun_c(node, node_type, is_c_or_cpp):
    function_name = check_function_name(node, is_c_or_cpp)
    node_list = []
    node_list.append(node)
    current_node = node
    another_type = "preproc_if" if node_type == "preproc_elif" else "preproc_elif"
    while (node.prev_sibling and (
            node.prev_sibling.parent.type == node_type or node.prev_sibling.parent.type == another_type)):
        node = node.prev_sibling.parent
        node_list.append(node)
    length = -1
    while True:
        for child in current_node.children:
            if child and child.type == "preproc_elif":
                node_list.append(child)
                current_node = child
                break
        if (length == len(node_list)):
            break
        else:
            length = len(node_list)
    if function_name:
        return node_list, function_name
    else:
        return node_list, None


def get_elif_sibling_node_list_in_fun_cpp(node):
    function_name = check_function_name(node, "cpp")
    node_list = []
    #如果是兄弟结点中的第一个if结点，直接找孩子结点
    if node.type == "preproc_if":
        node_list.append(node)
        for n in node.children:
            if n.type == "preproc_elif" or n.type == "preproc_else":
                node_list.append(n)
    else:  # 先找到兄弟结点中的if结点
        while node.type == "preproc_elif":
            node = node.prev_sibling
        if node:
            parent_if_node = node.prev_sibling.parent
            node_list.append(parent_if_node)
            for n in parent_if_node.children:
                if n.type == "preproc_elif" or n.type == "preproc_else":
                    node_list.append(n)
    if function_name:
        return node_list, function_name
    else:
        return node_list, None

def get_elif_sibling_node_list_in_fun_python(node):
    # function_name = check_function_name(node,is_c_or_cpp)
    node_list = []
    #如果是兄弟结点中的第一个if结点，直接找孩子结点
    if node.type == "if_statement":
        node_list.append(node)
        for n in node.children:
            if n.type == "elif_clause" or n.type == "else_clause":
                node_list.append(n)
    else:  # 先找到兄弟结点中的if结点
        while node.type == "elif_clause":
            node = node.prev_sibling
        parent_if_node = node.prev_sibling.parent
        node_list.append(parent_if_node)
        for n in parent_if_node.children:
            if n.type == "elif_clause" or n.type == "else_clause":
                node_list.append(n)
    return node_list


def get_elif_sibling_node_list_out_fun(node, node_type):
    node_list = []
    if node_type == "preproc_ifdef":
        node_list.append(node)
        current_node = node  # 用于向下遍历

        another_type = "preproc_if" if node_type == "preproc_ifdef" else "preproc_ifdef"

        # 向上遍历
        while (node.prev_sibling and (node.prev_sibling.type == node_type or node.prev_sibling.type == another_type)):
            node = node.prev_sibling
            node_list.append(node)
        # 向下遍历

        while (current_node.next_sibling and (
                current_node.next_sibling.type == node_type or current_node.next_sibling.type == another_type)):
            current_node = current_node.next_sibling
            node_list.append(current_node)

    elif node_type == "preproc_elif" or node_type == "preproc_else":
        while True:
            if (node.type == "preproc_if"):
                break
            node = node.parent  # preproc_if

        node_list.append(node)


        while node_list[-1].type != "preproc_else":
            for n in node_list[-1].children:
                if n.type == "preproc_elif" or n.type == "preproc_else":
                    node_list.append(n)

    elif node_type == "preproc_if":
        node_list.append(node)

        while node_list[-1].type != "preproc_else":
            for n in node_list[-1].children:
                if n.type == "preproc_elif" or n.type == "preproc_else":
                    node_list.append(n)

    else:
        print("传入的结点不是preproc_if、preproc_elif、preproc_else、preproc_ifdef类型")

    return node_list


def get_node_with_start_row(node, start_row):
    if node.start_point[0] == start_row:
        return node
    for child in node.children:
        found_node = get_node_with_start_row(child, start_row)
        if found_node:
            return found_node
    return None

def get_nodes_list_within_start_end(node, start_row, end_row):
    nodes_within_range = []
    if node.start_point[0] >= start_row and node.end_point[0] <= end_row:
        nodes_within_range.append(node)
    for child in node.children:
        nodes_within_range.extend(get_nodes_list_within_start_end(child, start_row, end_row))
    return nodes_within_range

def get_code_blocks_list_with_start_end(node, start_row, end_row):
    if node.start_point[0] > end_row or node.end_point[0] < start_row:
        return ""  # 超出指定范围，返回空字符串

    code_snippet = ""

    if node.start_point[0] >= start_row and node.end_point[0] <= end_row:
        code_snippet = node.text.decode()  # 节点完全在范围内，直接获取节点文本
    else:
        for child in node.children:
            code_snippet += get_code_blocks_list_with_start_end(child, start_row, end_row)

    return code_snippet

def get_node_with_start_end(node, start_row, end_row):
    if node.start_point[0] >= start_row and node.end_point[0] <= end_row:
        return node
    for child in node.children:
        found_node = get_node_with_start_end(child, start_row, end_row)
        if found_node:
            return found_node  # 返回找到的节点
    return None

def compare_line_for_target_code(node, target_start_line, target_end_line):
    return node.start_point[0] <= target_start_line and node.end_point[0] >= target_end_line

def get_target_node_in_preproc_if_binary_expressions_c_cpp(node, target_start_line, target_end_line):
    results = []
    if node.type == 'preproc_if':
        if compare_line_for_target_code(node, target_start_line, target_end_line):
            results.append(node)

        for child in node.children:
            results.extend(
                get_target_node_in_preproc_if_binary_expressions_c_cpp(child, target_start_line, target_end_line))
    else:
        for child in node.children:
            results.extend(
                get_target_node_in_preproc_if_binary_expressions_c_cpp(child, target_start_line, target_end_line))
    return results

def find_preproc_if_binary_expressions_python(node, target_start_line, target_end_line):
    results = []
    if node.type == 'if_statement':
        if compare_line_for_target_code(node, target_start_line, target_end_line):
            results.append(node)
        for child in node.children:
            results.extend(find_preproc_if_binary_expressions_python(child, target_start_line, target_end_line))
    else:
        for child in node.children:
            results.extend(find_preproc_if_binary_expressions_python(child, target_start_line, target_end_line))
    return results


def check_file_find_preproc_if_binary_expressions(node, target_start_line, target_end_line, is_c_or_py):
    results = []
    if is_c_or_py == 'c':
        results = get_target_node_in_preproc_if_binary_expressions_c_cpp(node, target_start_line, target_end_line)
    elif is_c_or_py == 'py':
        results = find_preproc_if_binary_expressions_python(node, target_start_line, target_end_line)
    return results

def find_code_lines(target_code, source_code):
    code_lines = source_code.split('\n')
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


# def get_function_body(sitter_parser,source_code,target_function_name):
#     def find_function_code(node):
#         if node.type == 'function_definition':
#             function_name_node = node.children[1]
#             function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
#             if function_name == target_function_name:
#                 # 找到目标函数名，提取整个函数定义
#                 return source_code[node.start_byte:node.end_byte]
#
#         for child in node.children:
#             result = find_function_code(child)
#             if result:
#                 return result
#     return find_function_code(sitter_parser.root_node)

def get_up_node_for_function(node):
    function_code = ""
    while node.parent:
        if node.type == "function_definition":
            function_code = node.text.decode()
            break
        node = node.parent
    return function_code

def get_up_node_for_preproc_if(node):
    function_code = ""
    while node.parent:
        if node.type == "preproc_elif" or node.type == "preproc_ifdef":
            current_node = node
            while current_node.parent:
                if current_node.type == "function_definition":
                    function_code = current_node.text.decode()  # 可能需要根据实际情况更改
                    break
                current_node = current_node.parent
            if function_code:  # 如果找到了 function_definition，直接返回
                return function_code
        node = node.parent
    return node.text

def get_up_node_for_assignment(node):
    get_node = node.prev_sibling
    function_code = ""
    while get_node.parent:
        if get_node.type == "assignment":
            function_code = get_node.text.decode()
            break
        get_node = get_node.parent
    return function_code

def get_up_node_for_class(node):
    get_node = node.prev_sibling
    function_code = ""
    while get_node.parent:
        if get_node.type == "class_definition":
            function_code = get_node.text.decode()
            break
        get_node = get_node.parent
    return function_code

def get_all_class_definitions(node, source_code):
    class_definitions = []

    def get_names(node):
        nonlocal class_definitions
        if node.type == 'class_definition':
            function_name_node = node.children[1]
            class_definitions.append(source_code[function_name_node.start_byte:function_name_node.end_byte])
        for child in node.children:
            get_names(child)

    get_names(node)
    return class_definitions

def get_all_function_names(node, source_code):
    function_names = []

    def get_names(node):
        nonlocal function_names
        if node.type == 'function_definition':
            function_name_node = find_identifier_child(node)
            if function_name_node:
                function_names.append(source_code[function_name_node.start_byte:function_name_node.end_byte])
        for child in node.children:
            get_names(child)

    get_names(node)
    return function_names

def get_block_function_parent(node):
    while node:
        if node.type == 'function_definition':
            return node.text.decode()

        if node.type in ['if_statement', 'while_statement', 'for_statement', 'with_statement', 'try_statement']:
            node = node.parent
        node = node.parent
    return None

def get_target_code_class_name(node_type_list):
    for node in node_type_list:
        if node.type == "identifier":
            return node.text.decode()


def get_class_definition_body(sitter_parser, source_code, target_function_name):
    def find_function_code(node):
        if node.type == 'class_definition':
            function_name_node = node.children[1]
            function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
            if function_name == target_function_name:
                # 找到目标函数名，提取整个函数定义
                return source_code[node.start_byte:node.end_byte]

        for child in node.children:
            result = find_function_code(child)
            if result:
                return result
    return find_function_code(sitter_parser.root_node)

def is_in_fun(node):
    while node:
        if node.type == 'function_definition':
            return True
        node = node.parent
    return False

def get_all_function_definitions(ast_tree, source_code):
    # Find all function nodes
    function_nodes = find_all_function_nodes(ast_tree.root_node)
    function_definitions = []
    # Extract the function definitions
    for function_node in function_nodes:
        function_name_node = find_identifier_child(function_node)
        if function_name_node:
            function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
            function_body_node = find_function_body_node(function_node)
            print(function_body_node)
            if function_body_node:
                function_body = source_code[function_body_node.start_byte:function_body_node.end_byte]
                function_definitions.append({'name': function_name, 'body': function_body})

    return function_definitions

def find_all_function_nodes(parent_node):
    function_nodes = []
    for child in parent_node.children:
        if child.type == 'function_definition':
            function_nodes.append(child)
        elif child.child_count > 0:
            function_nodes.extend(find_all_function_nodes(child))
    return function_nodes


def find_function_body_node(function_node, is_c_or_py="c"):
    for child in function_node.children:
        if is_c_or_py == "c":
            if child.type == 'compound_statement':
                return child
            elif child.child_count > 0:
                # Recursively search for a block in the child's subtree
                result = find_function_body_node(child, is_c_or_py)
                if result:
                    return result
        elif is_c_or_py == "python":
            # Handle Python-specific conditions
            # (modify this part based on how Python function bodies are represented in your case)
            if child.type == 'block':  # Assuming 'suite' represents a Python function body
                return child
            elif child.child_count > 0:
                # Recursively search for a block in the child's subtree
                result = find_function_body_node(child, is_c_or_py)
                if result:
                    return result
    return None

def find_identifier_child(parent_node):
    for child in parent_node.children:
        if child.type == 'identifier':
            return child
        elif child.child_count > 0:
            # Recursively search for an identifier in the child's subtree
            result = find_identifier_child(child)
            if result:
                return result
    return None


### 获取多个节点
def find_function_nodes(ast_node, source_code, target_function_name, target_function_start):
    matching_function_nodes = []

    for child in ast_node.children:
        if child.type == 'function_definition':
            function_name_node = find_identifier_child(child)
            if function_name_node:
                function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
                if function_name == target_function_name and child.start_byte >= target_function_start:
                    matching_function_nodes.append(child)
        # 递归在子节点中查找函数节点
        matching_function_nodes.extend(
            find_function_nodes(child, source_code, target_function_name, target_function_start))

    return matching_function_nodes


### 源文件中的有多个重名函数
def get_function_bodies(ast_tree, source_code, target_function_name, is_c_or_py):
    function_nodes = find_function_nodes(ast_tree.root_node, source_code, target_function_name, 0)
    function_list = []

    for function_node in function_nodes:
        function_name_node = find_identifier_child(function_node)
        if function_name_node:
            function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
            function_body_node = find_function_body_node(function_node, is_c_or_py)
            if function_body_node:
                function_body = source_code[function_body_node.start_byte:function_body_node.end_byte]
                # 提取函数参数
                parameters = get_function_parameters(function_node, source_code)
                function_list.append({'name': function_name, 'body': function_body, 'parameters': parameters})

    return function_list

def get_function_parameters(function_node, source_code):
    parameter_list_node = find_function_parameters_node(function_node)
    if parameter_list_node:
        return source_code[parameter_list_node.start_byte:parameter_list_node.end_byte]
    return None


# Add a new helper function to find the parameter list node in the function node
def find_function_parameters_node(function_node):
    for child in function_node.children:
        if child.type == 'parameter_list':
            return child
        # Recursively search for parameter_list in child nodes
        parameter_list_node = find_function_parameters_node(child)
        if parameter_list_node:
            return parameter_list_node
    return None


## 单一结点
def find_function_node(ast_node, source_code, target_function_name, target_function_start):
    end_row = 0
    for child in ast_node.children:
        if child.type == 'function_definition':
            function_name_node = find_identifier_child(child)
            if function_name_node:
                function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
                end_row = function_name_node.end_byte
                print(end_row)
                if function_name == target_function_name and child.start_byte >= target_function_start:
                    return child
        # Recursively search for the function node in child nodes
        function_node = find_function_node(child, source_code, target_function_name, end_row)
        if function_node:
            return function_node
    return None


## 获取一个函数内容
def get_function_body(ast_tree, source_code, target_function_name, is_c_or_py):
    function_node = find_function_node(ast_tree.root_node, source_code, target_function_name, 0)
    if function_node:
        function_name_node = find_identifier_child(function_node)
        if function_name_node:
            function_name = source_code[function_name_node.start_byte:function_name_node.end_byte]
            function_body_node = find_function_body_node(function_node, is_c_or_py)
            if function_body_node:
                function_body = source_code[function_body_node.start_byte:function_body_node.end_byte]
                # Extract function parameters
                parameters = get_function_parameters(function_node, source_code)
                return {'name': function_name, 'body': function_body, 'parameters': parameters}
    return None

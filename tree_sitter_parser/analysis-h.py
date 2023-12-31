import json


###################根据行号获取结点 arg1:根节点  arg2:结点开始的行号  return：结点
def find_node(node, start_row):
    if node.start_point[0] == start_row:
        return node

    for child in node.children:
        found_node = find_node(child, start_row)
        if found_node:
            return found_node  # 返回找到的节点

    # 如果没有找到匹配的节点，返回 None
    return None

def find_function_name(node):
    while node:
        if node.type == 'function_definition':
            # Assuming function name is within a function_declarator node
            function_name_node = None
            for child in node.children:
                if child.type == 'function_declarator':
                    function_name_node = child
                    break

            if function_name_node:
                # Now, search for the identifier which is typically the function name
                for child in function_name_node.children:
                    if child.type == 'identifier':
                        return child.text
            break
        node = node.parent
    return None  # Return None if function definition is not found or no function name is found


####################获取兄弟结点存入list  arg1:源代码，arg2: 已知结点，arg3:已知结点类型 return:list
def get_sibling_node_list(node, node_type):
    node_list = []
    node_list.append(node)
    current_node = node  # 用于向下遍历
    function_name = find_function_name(node)

    another_type = "preproc_if" if node_type == "preproc_elif" else "preproc_elif"
    # 向上遍历
    while (node.prev_sibling and (
            node.prev_sibling.parent.type == node_type or node.prev_sibling.parent.type == another_type)):
        node = node.prev_sibling.parent
        node_list.append(node)
    # 向下遍历
    length = -1
    while True:  # 如何有更好的跳出while循环的方法?

        for child in current_node.children:
            if child and child.type == "preproc_elif":  # 向下找兄弟结点只能是这个类型    可能会有隐患
                # print(child)
                node_list.append(child)
                current_node = child
                break
        if (length == len(node_list)):
            break  # 如何有更好的跳出while循环的方法
        else:
            length = len(node_list)
    if function_name:
        return node_list, function_name
    else:
        return node_list, None





####################获取兄弟结点代码list  arg1:源代码 arg2:兄弟结点list return：兄弟结点代码list
def get_code_list(source_code, node_list):
    code_list = []

    start_row_list = []  # 获取所有结点的 start_row
    for node in node_list:
        start_row_list.append(node.start_point[0])

    start_row_list.append(node_list[0].end_point[0])  # 添加最后一行的行数
    start_row_list = sorted(start_row_list)  # 排序

    # start_row = node.start_point[0]
    # end_row = node.end_point[0]

    # 提取节点的文本范围
    c_code_list = source_code.split("\n")
    print(start_row_list)
    for i in range(len(start_row_list) - 1):

        c = ""
        for e in c_code_list[start_row_list[i]:start_row_list[i + 1]]:
            c += e + "\n"
        code_list.append(c)

    return code_list


####################生成json文件，输入data为list 第二个参数为json文件路径
def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

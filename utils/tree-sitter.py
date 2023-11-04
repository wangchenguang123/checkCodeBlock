###找到某一区间内的所有节点信息
def find_nodes_within_range(node, start_row, end_row):
    nodes_within_range = []

    if node.start_point[0] >= start_row and node.end_point[0] <= end_row:
        nodes_within_range.append(node)

    for child in node.children:
        nodes_within_range.extend(find_nodes_within_range(child, start_row, end_row))

    return nodes_within_range


### 获取某一区间内的代码片段
def get_code_snippet_within_range(node, start_row, end_row):
    if node.start_point[0] > end_row or node.end_point[0] < start_row:
        return ""  # 超出指定范围，返回空字符串

    code_snippet = ""

    if node.start_point[0] >= start_row and node.end_point[0] <= end_row:
        code_snippet = node.text.decode()  # 节点完全在范围内，直接获取节点文本
    else:
        for child in node.children:
            code_snippet += get_code_snippet_within_range(child, start_row, end_row)

    return code_snippet

def read_file_as_string(file_path):
    """
    读取文件内容，并按照字符串方式返回文件的全部内容。

    Parameters:
        file_path (str): 文件路径。

    Returns:
        str: 文件内容作为一个字符串。
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 '{file_path}' 不存在.")

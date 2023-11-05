import os

from tree_sitter import Language, Parser


### 目前使用build文件夹下提供的so即可
class TreeSitterParser:
    def __init__(self, so_path):
        self.so_path = so_path

    def build_language_so(self, filepath, filename, file_list):
        Language.build_library(
            os.path.join(filepath, filename),
            file_list
        )
        return os.path.join(filepath, filename)

    def get_py_parser(self):
        PY_LANGUAGE = Language(self.so_path, 'python')
        py_parser = Parser()
        py_parser.set_language(PY_LANGUAGE)
        return py_parser

    def get_c_parser(self):
        C_LANGUAGE = Language(self.so_path, 'c')
        c_parser = Parser()
        c_parser.set_language(C_LANGUAGE)
        return c_parser

    def get_cpp_parser(self):
        CPP_LANGUAGE = Language(self.so_path, 'cpp')
        cpp_parser = Parser()
        cpp_parser.set_language(CPP_LANGUAGE)
        return cpp_parser

    def get_java_parser(self):
        JAVA_LANGUAGE = Language(self.so_path, 'java')
        java_parser = Parser()
        java_parser.set_language(JAVA_LANGUAGE)
        return java_parser

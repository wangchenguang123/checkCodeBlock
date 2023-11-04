import tree_sitter

CPP_LANGUAGE = tree_sitter.Language('D:\\checkCodeBlock\\build\\my-languages.so', 'cpp')
cpp_parser = tree_sitter.Parser()
cpp_parser.set_language(CPP_LANGUAGE)

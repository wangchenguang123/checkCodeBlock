archWord = []


def find_functions_with_arch_words(function_names):
    functions_with_arch_words = []
    for function_name in function_names:
        arch_found = [word for word in archWord if word in function_name.lower()]
        if arch_found:
            functions_with_arch_words.append({'function_name': function_name, 'architectures': arch_found})
    return functions_with_arch_words


def find_class_with_arch_words(class_names):
    class_with_arch_words = []
    for class_name in class_names:
        arch_found = [word for word in archWord if word in class_name.lower()]
        if arch_found:
            class_with_arch_words.append({'class_name': class_name, 'architectures': arch_found})
    return class_with_arch_words


def get_code_contains_loongarch(target_code):
    lines = target_code.split('\n')  # Split the code into lines
    loongarch_lines = [line.strip() for line in lines if 'loongarch' in line.lower()]
    return loongarch_lines

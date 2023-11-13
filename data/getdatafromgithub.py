import base64
import difflib
import os
import re

import requests

from tree_sitter_parser.domain import get_source_code, find_code_lines

token = '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'


def search_pull_requests_with_keyword(keyword):
    base_url = 'https://api.github.com/search/issues'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    page = 1
    per_page = 30  # 可以根据需求调整每页返回的数量

    while True:
        params = {'q': f'{keyword} type:pr in:title,body', 'page': page, 'per_page': per_page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            pull_requests = response.json()
            if len(pull_requests) == 0:
                break  # 如果当前页没有数据，表示到达最后一页
            page += 1
            for pr in pull_requests.get('items', []):
                pr_details_url = pr['repository_url']  # URL to fetch the specific PR details
                pr_response = requests.get(pr_details_url, headers=headers)
                if pr_response.status_code == 200:
                    pr_data = pr_response.json()
                    print(f"Repository: {pr_data['full_name']} - Title: {pr['title']} - URL: {pr['html_url']}")
                    repo_owner, repo_name, pull_request_number = "lxc", "lxc", 4363
                    files_status = get_files_status(repo_owner, repo_name, pull_request_number)
                    files_list = get_repository_contents(repo_owner, repo_name)
                    fetch_diff_of_pull_request(repo_owner, repo_name, pull_request_number, files_status, files_list)
                else:
                    print(f"Failed to fetch details for PR: {pr['url']}")
        else:
            print("Failed to search pull requests")
            break


archWord = ['aarch64', 'amd64', 'arm64', 'i386', 'i486', 'i586', 'i686', 'i786', 'i886', 'i986', 'ia32', 'ia64', 'm68k',
            'mc68000', 'mips64', 'powerpc64', 'ppc', 'powerpc64le', 'riscv', 's390', 's390x', 'sparc', 'arm32',
            'x86_64', 'ppc64', 'loongarch', 'loongarch64']


def get_simliar_file_in_same_dir(repo_owner, repo_name, pull_number, file_path_map):
    file_result = []
    for path in file_path_map["files"]:
        if any(path.find(arch) > -1 for arch in archWord):
            content = get_pr_file_content(repo_owner, repo_name, pull_number, path)
            res = {"filepath": path, "content": content}
            file_result.append(res)
    return file_result


def fetch_diff_of_pull_request(owner, repo, pull_number, files_status, file_list):
    base_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.get(base_url, headers=headers)
    lines = []
    if response.status_code == 200:
        diff_content = response.text  # 获取差异内容
        # print(diff_content)
        diffs = process_diff_content(diff_content)  # 处理差异内容
        for diff in diffs:
            # print(diff)
            if diff["filepath"] in files_status.keys() and files_status[diff["filepath"]] == "modified":
                blocks = diff["diff_blocks"]
                result = []
                if len(blocks) == 1:
                    result.append(("\n").join(blocks[0]))
                else:
                    for b in blocks:
                        child_b = ("\n").join(b)
                        result.append(child_b)
                # print("------")
                # print(result)
                source_code = get_pr_file_content(owner, repo, pull_number, diff["filepath"])
                res = {"filepath": diff["filepath"], "target_code": result, "source_code": source_code}
                if len(result) == 1:
                    lines = find_code_lines(result[0], source_code)  ## 源文件定位目标文件行数
                else:
                    for r in result:
                        lines.extend(find_code_lines(r, source_code))  ## 源文件定位目标文件多行数
            elif files_status[diff["filepath"]] == "added":
                file_path_map = get_parent_path_for_added_file(owner, repo, diff["filepath"])
                print(get_simliar_file_in_same_dir(owner, repo, pull_number, file_path_map))


    else:
        print("无法获取拉取请求的差异内容")


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def get_files_status(owner, repo, pull_number):
    base_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(base_url, headers=headers)

    files_status = {}  # Dictionary to store file names and their statuses

    if response.status_code == 200:
        files_info = response.json()
        for file_info in files_info:
            filename = file_info['filename']
            status = file_info['status']
            files_status[filename] = status
    else:
        print("Failed to fetch files information.")

    return files_status


def get_parent_path_for_added_file(repo_owner, repo_name, filepath):
    if filepath.find("/") > -1:
        folder_path = os.path.dirname(filepath)
    else:
        folder_path = filepath
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    response = requests.get(url)
    all_files_in_folder = []
    if response.status_code == 200:
        contents = response.json()
        all_files_in_folder = [content['path'] for content in contents if content['type'] == 'file']
    info = {"folder_path": folder_path, "files": all_files_in_folder, "origin_filepath": filepath}
    return info


def get_repository_contents(repo_owner, repo_name, path=''):
    # GitHub API Endpoint for repo contents
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"

    # 发起 GET 请求
    response = requests.get(url)

    if response.status_code == 200:
        contents = response.json()
        items = []
        for content in contents:
            if content['type'] == 'file':
                items.append((content['name'], content['path']))
            elif content['type'] == 'dir':
                items.append((content['name'], content['path']))
                sub_items = get_repository_contents(repo_owner, repo_name, content['path'])
                if sub_items is not None:
                    items += sub_items  # Append the items from sub-directory
        return items
    else:
        print("无法获取内容")
        return None


def get_pr_file_content(repo_owner, repo_name, pr_number, file_path):
    # GitHub API Endpoint for pull request files
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    # 发起 GET 请求
    print(url)
    response = requests.get(url)
    file_content = ""
    if response.status_code == 200:
        pr_files = response.json()
        for pr_file in pr_files:
            if pr_file['filename'] == file_path:
                print(file_path)
                print(pr_file['filename'])
                # Found the file in the pull request
                content_url = pr_file['contents_url']
                content_response = requests.get(content_url)

                if content_response.status_code == 200:
                    file_details = content_response.json()
                    file_content = base64.b64decode(file_details['content']).decode('utf-8')
                    print(f"File Content for {file_path} in PR {pr_number}:\n")
                    return file_content
                else:
                    print(f"Unable to get content for {file_path} in PR {pr_number}")
                    return None
        if len(file_content) == 0:
            file_content = get_origin_file_content(repo_owner, repo_name, file_path)
            return file_content
        return None
    else:
        print(f"Unable to get pull request files for PR {pr_number}")
        return None


def get_origin_file_content(repo_owner, repo_name, file_path):
    # GitHub API Endpoint for file content
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    # 发起 GET 请求
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        file_details = response.json()
        if 'content' in file_details:
            file_content = base64.b64decode(file_details['content']).decode('utf-8')
            print(f"File Content for {file_path}:\n")
            return file_content
        else:
            print("找不到文件内容")
    else:
        print("无法获取文件")


def process_diff_content(diff_content):
    diff_lines = diff_content.splitlines()
    modified_files = []

    current_file = None
    diff_blocks = []  # Store all change blocks within a file
    child_list = []
    for line in diff_lines:
        if line.startswith('+++'):
            if current_file is not None:
                file_path = current_file.split("b/")[-1]
                file_dict = {
                    "filepath": file_path,
                    "diff_blocks": diff_blocks + [child_list]
                }
                modified_files.append(file_dict)
            current_file = line
            diff_blocks = []
            child_list = []
        elif line.startswith('@@'):
            if child_list:
                diff_blocks.append(child_list)  # Create a new dictionary
                child_list = []  # Reset child_list for the next block
        elif line.startswith('+'):
            child_list.append(line[1:])

    if current_file is not None:
        file_path = current_file.split("b/")[-1]
        file_dict = {
            "filepath": file_path,
            "diff_blocks": diff_blocks + [child_list]
        }
        modified_files.append(file_dict)

    return modified_files


def extract_parts_from_github_url(url):
    # 使用正则表达式匹配
    matches = re.search(r'https://github.com/([^/]+)/([^/]+)/pull/(\d+)', url)

    if matches:
        repo_owner = matches.group(1)
        repo_name = matches.group(2)
        pull_request_number = matches.group(3)

        return repo_owner, repo_name, pull_request_number
    else:
        return None


def get_files_content(repo_owner, repo_name, pull_request_number):
    # 构建 API 请求的 URL
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_request_number}/files'

    # 添加 token 进行身份验证
    headers = {'Authorization': f'token {token}'}

    # 发起 API 请求
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json()

        file_contents = []

        # 获取包含 PR 的文件列表
        for file in files:
            file_url = file['raw_url']  # 获取文件的原始 URL

            # 获取文件内容
            file_response = requests.get(file_url, headers=headers)
            if file_response.status_code == 200:
                file_content = file_response.text
                file_contents.append({
                    'filename': file['filename'],
                    'content': file_content
                })

        return file_contents
    else:
        print(f"Failed to fetch files. Status code: {response.status_code}")
        return None


def getfilename(filepath):
    if filepath.find("/") > -1:
        return filepath.split("/")[1]
    else:
        return filepath


archWord = ['loongarch64', 'aarch64', 'amd64', 'arm64', 'i386', 'i486', 'i586', 'i686', 'i786', 'i886', 'i986', 'ia32',
            'ia64', 'm68k',
            'mc68000', 'mips64', 'powerpc64', 'ppc', 'powerpc64le', 'riscv', 's390', 's390x', 'sparc', 'arm32',
            'x86_64', 'ppc64', 'loongarch', 'powerpc']

if __name__ == '__main__':
    # search_pull_requests_with_keyword("LoongArch")

    repo_owner, repo_name, pull_request_number = "sphde", "sphde", 69
    files_status = get_files_status(repo_owner, repo_name, pull_request_number)
    files_list = get_repository_contents(repo_owner, repo_name)
    fetch_diff_of_pull_request(repo_owner, repo_name, pull_request_number, files_status, files_list)
    get_source_code("E:\\WcgResearch\\resource\\arch_parse.c")

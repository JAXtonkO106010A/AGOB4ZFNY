import base64
import datetime
import random
import string
import sys
import time
import chardet
import requests
import json
import pandas as pd


def detect_encoding(file_path):
    with open(file_path, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result["encoding"]


def generate_random_string(min_length, max_length):
    # 随机生成字符串长度
    length = random.randint(min_length, max_length)
    # 定义字符集
    charset = string.ascii_letters + string.digits
    # 生成第一个字符，确保不是数字
    first_char = random.choice(string.ascii_letters).upper()
    # 生成剩余的字符
    remaining_chars = "".join(random.choice(charset) for _ in range(length - 1))
    # 将第一个字符和剩余的字符组合起来
    result = first_char + remaining_chars
    return result


def get_proxy_ip(proxy):
    if "@" in proxy:
        return proxy
    proxys = proxy.split(":")
    return (
            "http://"
            + str(proxys[2])
            + ":"
            + str(proxys[3])
            + "@"
            + str(proxys[0])
            + ":"
            + str(proxys[1])
    )


GITHUB_API_BASE_URL = "https://api.github.com"


class Github(object):
    def __init__(self, token, proxy=None):
        self.token = token
        self.proxies = {}
        if proxy:
            self.proxy = proxy
            self.proxies = (
                {"http": self.proxy, "https": self.proxy}
                if "@" in self.proxy
                else {"http": get_proxy_ip(self.proxy), "https": get_proxy_ip(self.proxy)}
            )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Awesome-Octocat-App",
        }
        self.target_repo_name = None
        print("=" * 80)
        self.username = self._get_username()
        print(self.username, "当前用户的用户名")
        self.USER_REPOS_URL = f"{GITHUB_API_BASE_URL}/users/{self.username}/repos"
        repositories = self.list_repositories().json()
        match_repositories = [
            repo["name"] for repo in repositories if repo["name"].endswith("Y")
        ]
        if self.username == "lhhc2IH":
            self.target_repo_name = "gitcoin_lhhc2IH_test"
        elif self.username == "daihaojun554":
            self.target_repo_name = "auto_green"
        else:
            self.target_repo_name = (
                random.choice(match_repositories) if match_repositories else None
            )

        if not self.target_repo_name and (
                self.username != "lhhc2IH"
        ):
            print("No repository ,need to create repo")
            self.create_repo()
        print(f"当前需要操作的仓库: {self.target_repo_name or 'None'}")
        # with open("./repo.csv", 'a', encoding='utf-8') as file:
        #     file.write(
        #         f'{self.username},https://github.com/{self.username}/{self.target_repo_name}\n')
        # 需要将 ci.yml文件 和 ci-puls.yml上传 和 github.py本身文件上传
        # need_to_upload_files = [
        #     {
        #         "path": ".github/workflows/ci-plus.yml",
        #         "content_path": ".github/workflows/ci-plus.yml",
        #         "message": "Update CI workflow",
        #     },
        #     # {
        #     #     "path": ".github/workflows/ci.yml",
        #     #     "content_path": ".github/workflows/ci.yml",
        #     #     "message": "Update CI workflow",
        #     # },
        #     {
        #         "path": "github.py",
        #         "content_path": "github.py",
        #         "message": "update github.py",
        #     },
        #     # {
        #     #     "path": "script.py",
        #     #     "content_path": "script.py",
        #     #     "message": "update script.py",
        #     # },
        #     {
        #         "path": "requirements.txt",
        #         "content_path": "requirements.txt",
        #         "message": "update requirement.txt",
        #     },
        # ]

        # for file_info in need_to_upload_files:
        #     file_path = file_info["path"]
        #     content_path = file_info["content_path"]
        #     commit_message = file_info["message"]
        #     self.upload_file_to_repo(file_path, content_path, commit_message)
        #     time.sleep(3)

    def _get_username(self):
        """获取当前用户的用户名"""
        response = self._make_request("GET", "https://api.github.com/user")
        return response.json().get("login") if response else None

    def _make_request(self, method, url, data=None, **kwargs):
        """封装发起请求的过程"""
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                data=data,
                proxies=self.proxies,
                **kwargs,
            )
            # response.raise_for_status()  # Raise an HTTPError for bad responses
            print(response.text)
            if response.status_code == 200:
                return response
        except requests.HTTPError as http_err:
            print(f"Http请求错误 {http_err}")
            if response.status_code == 422:
                print(f"{response.status_code}--{response.text}")

            elif response.status_code in [404, 401]:
                print(
                    f"response.status_code :{response.status_code}:{response.text}"
                )
        except Exception as err:
            print(f"An error occurred: {err}")

    def create_repo(self):
        repo_name = generate_random_string(6, 10)
        """创建一个新的仓库."""
        data = {
            "name": f"{repo_name}Y",
            "private": False,
            "description": "nothing to do",  # todo
            "auto_init": False,
        }
        self.target_repo_name = repo_name + "Y"
        return self._make_request("POST", self.USER_REPOS_URL, json.dumps(data))

    def get_user(self):
        """获取用户的信息"""
        url = "https://api.github.com/user"
        for _ in range(3):
            try:
                resp = requests.get(url, headers=self.headers, proxies=self.proxies)
                print(f"用户信息:{resp.text}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                print(e)

    def list_repositories(self):
        """列出当前用户所有的仓库信息（对外公开的）"""
        return self._make_request("GET", self.USER_REPOS_URL)

    def upload_file_to_repo(
            self, file_path, content_path, commit_message, branch="main"
    ):
        encoding = detect_encoding(content_path)
        with open(content_path, "r", encoding=encoding) as file:
            content = file.read()
        # Encode content in base64
        encoded_content = base64.b64encode(content.encode()).decode()
        # Get the current SHA of the file if it exists
        sha = self._get_file_sha(file_path)

        # Prepare the payload
        data = {
            'message': commit_message,
            'content': encoded_content
        }
        if sha:
            data['sha'] = sha
        # 对内容进行base64编码
        # Make the API call
        self._make_request('put',
                           f'https://api.github.com/repos/{self.username}/{self.target_repo_name}/contents/{file_path}',
                           data=json.dumps(data)
                           )
        # if response.status_code == 201:
        #     print(f"File '{file_path}' created successfully.")
        # elif response.status_code == 200:
        #     print(f"File '{file_path}' updated successfully.")
        # else:
        #     print(f"Failed to create or update file '{file_path}'. Status code: {response.status_code}")
        #     print(response.text)

    def search_repositories(self, q):
        url = (
                GITHUB_API_BASE_URL
                + f"/search/repositories?q={q}&per_page=10&page=1&order=desc&sort=stars"
        )
        response = self._make_request("GET", url)
        return response.json()["items"] if response else None

    def _get_file_sha(self, file_path, branch='main'):
        response = self._make_request(
            "GET",
            f"{GITHUB_API_BASE_URL}/repos/{self.username}/{self.target_repo_name}/contents/{file_path}?ref={branch}",
        )
        return response.json().get("sha") if response else None

    def main_workflow(self):
        print("*" * 80)
        repositories = self.list_repositories()
        match_repositories = [
            repo["name"] for repo in repositories if repo["name"].endswith("Y")
        ]
        if self.username == "lhhc2IH":
            self.target_repo_name = "gitcoin_lhhc2IH_test"
        elif self.username == "daihaojun554":
            self.target_repo_name = "auto_green"
        else:
            self.target_repo_name = (
                random.choice(match_repositories) if match_repositories else None
            )
        if not self.target_repo_name and (
                self.username != "lhhc2IH" or self.username != "daihaojun554"
        ):
            print("No repository ,need to create repo")
            self.create_repo()
        print(f"当前需要操作的仓库: {self.target_repo_name or 'None'}")
        if self.target_repo_name:
            # with open("./github_template/repo.csv", 'a', encoding='utf-8') as file:
            #     file.write(
            #         f'{self.username},https://github.com/{self.username}/{self.target_repo_name}\n')
            # Example usage of the upload_file_to_repo method\
            files_to_upload = [
                {
                    "path": ".gitignore",
                    "content_path": ".gitignore",
                    "message": "add .gitignore",
                },
                # {
                #     'path': 'script.py',
                #     "content_path": "./github_template/script.py",
                #     "message": "add script.py"
                # },
                # {
                #   "path"
                # },
                {
                    "path": "requirements.txt",
                    "content_path": "./github_template/requirements.txt",
                    "message": "Add requirement.txt",
                },
                {
                    "path": ".github/workflows/ci.yml",
                    "content_path": ".github/workflows/ci.yml",
                    "message": "Update CI workflow",
                },
                # {
                #     "path": "README.md",
                #     "content_path": "./github_template/README.md",
                #     "message": "Add README"
                # },
                # Add more files as needed
            ]
            for file_info in files_to_upload:
                file_path = file_info["path"]
                content_path = file_info["content_path"]
                commit_message = file_info["message"]
                encoding = detect_encoding(file_path)
                # Read file content
                file_content = open(content_path, "r", encoding=encoding).read()
                # Upload file to the repository
                self.upload_file_to_repo(
                    self.target_repo_name, file_path, file_content, commit_message
                )
                # Sleep for a bit to avoid hitting GitHub API rate limits
                time.sleep(1)
        else:
            print("No target repository found to operate on.")
        print("*" * 80)

    def main_random(self):
        print("*" * 80)
        repositories = self.list_repositories()
        match_repositories = [
            repo["name"] for repo in repositories if repo["name"].endswith("Y")
        ]

        if self.username == "lhhc2IH":
            self.target_repo_name = "gitcoin_lhhc2IH_test"
        else:
            self.target_repo_name = (
                random.choice(match_repositories) if match_repositories else None
            )
        if not self.target_repo_name and self.username != "lhhc2IH":
            print("No repository ,need to create repo")
            self.create_repo()
        print(f"当前需要操作的仓库: {self.target_repo_name or 'None'}")
        if self.target_repo_name:
            with open("./github_template/repo.csv", "a", encoding="utf-8") as file:
                file.write(
                    f"{self.username},https://github.com/{self.username}/{self.target_repo_name}\n"
                )

            file_content = generate_random_string(20, 50)
            print(file_content)
            commit_message = generate_random_string(
                29, 70
            )  # todo commit message 不能固定
            file_path = generate_random_string(4, 7) + ".txt"
            self.upload_file_to_repo(
                self.target_repo_name, file_path, file_content, commit_message
            )
        else:
            print("No target repository found to operate on.")
        print("*" * 80)

    # 获取仓库文件列表
    def get_repo_files_list(self, owner, repo_name, path=""):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
        all_content = []
        page = 1

        while True:
            if page >= 3:
                break
            params = {"page": page}
            response = self._make_request("GET", url, params=params)

            if response:
                content = response.json()
                all_content.extend(content)

                # 检查是否还有更多页面
                link_header = response.headers.get("Link")
                if link_header and 'rel="next"' in link_header:
                    page += 1
                else:
                    break
            else:
                break

        # 递归处理子目录
        for item in all_content:
            if len(all_content) >= 30:
                break
            if item["type"] == "dir":
                sub_content = self.get_repo_files_list(owner, repo_name, item["path"])
                all_content.extend(sub_content)

        return all_content

    def get_random_file_(self, query):
        reps = self.search_repositories(query)
        r = random.choice(reps)
        owner = r.get("owner", {}).get("login")
        reps_name = r.get("name")
        xxx = self.get_repo_files_list(owner, reps_name)
        print(xxx)

        for _ in xxx:
            if _.get("type") != "file":
                continue
            if _.get("name").endswith("README.md"):
                continue
            elif _.get("name").endswith(".gitignore"):
                continue
            elif _.get("name").endswith("script.py"):
                continue
            else:
                if random.randint(0, 2) == 1:
                    continue
                else:
                    file_ = _
                    return file_

    def upload_file_to_repo_forsha(self, fiel, commit_message):
        url = f"https://api.github.com/repos/{self.username}/{self.target_repo_name}/contents/{fiel.get('path')}"
        for _ in range(3):
            resp = requests.get(
                fiel.get("download_url"), proxies=self.proxies, headers=self.headers
            )
            if resp.status_code == 200:
                break
        content_encoded = base64.b64encode(resp.content).decode("utf-8")
        data = {
            "message": commit_message,
            "content": content_encoded,
            "branch": "main",
            "sha": fiel.get("sha"),
        }
        # sha = self._get_file_sha(self.target_repo_name, fiel.get('path'), 'main')
        # if sha:
        #      data['sha'] = fiel.get('sha')
        return self._make_request("PUT", url, data=json.dumps(data))


def upload_random_file_to_repo(token, commit_message):
    g = Github(token=token, proxy=None)
    keyword = str(random.choice(open('keywords.txt', encoding='utf-8').read().splitlines()))
    file_ = g.get_random_file_(keyword)
    g.upload_file_to_repo_forsha(file_, commit_message)


import random

# 定义一个包含多个模板消息的列表
commit_message_templates = [
    "修复了 {issue} 问题",
    "添加了 {feature} 功能",
    "优化了 {module} 模块的性能",
    "更新了 {file} 文件",
    "改进了 {function} 函数的实现",
    "增加了 {test} 单元测试",
    "调整了 {config} 配置文件",
    "解决了 {bug} Bug",
    "合并了 {branch} 分支",
    "重构了 {code} 代码"
]


# 生成随机的 commit message
def generate_random_commit_message():
    template = random.choice(commit_message_templates)
    # 假设我们有一些变量可以填充到模板中
    placeholders = {
        "issue": "登录失败",
        "feature": "用户认证",
        "module": "网络请求",
        "file": "config.py",
        "function": "validate_user",
        "test": "test_login",
        "config": "settings.json",
        "bug": "空指针异常",
        "branch": "feature-branch",
        "code": "main.py"
    }
    commit_message = template.format(**placeholders)
    return commit_message


# 示例调用


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github.py <token>")
        sys.exit(1)
    my_test_token = sys.argv[1]
    commit_message = [generate_random_commit_message()]
    upload_random_file_to_repo(
        my_test_token, commit_message=commit_message[0]
    )

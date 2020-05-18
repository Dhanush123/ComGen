import os
import json
import base64

import requests
import ray
from github import Github
from dotenv import load_dotenv

github = Github(os.getenv('GITHUB_ACCESS_TOKEN'), per_page=100)
load_dotenv()


def print_rate_limit():
    rate_limit = github.get_rate_limit()
    print('rate limit (core/search): {}/{}'.format(rate_limit.core, rate_limit.search))


def base64_to_string(data):
    return str(base64.b64decode(data, validate=True))


def get_mostpopular_repos(lang, max_repos=100):
    candidate_repos = []
    repositories = github.search_repositories(
        query='language:{}'.format(lang), sort='stars')
    for i, repo in zip(range(max_repos), repositories):
        candidate_repos.append(repo)
        print('got repo {} info: {}'.format(i, repo.full_name))
    return candidate_repos


# def filter_english_only_repos(repos):
#     def is_english_string(s):
#         try:
#             s.encode(encoding='utf-8').decode('ascii')
#         except UnicodeDecodeError:
#             return False
#         else:
#             return True

#     def is_english_repo(repo):
#         repo_name = repo.full_name
#         readme = repo.get_contents('README.md').content
#         # readme = base64_to_string(repo.get_contents('README.md').content)
#         print(repo_name, readme, is_english_string(
#             repo_name), is_english_string(readme))
#         return is_english_string(repo_name) and is_english_string(readme)

#     repos[:] = [repo for repo in repos if is_english_repo(repo)]
#     return repos


@ray.remote
def get_filter_save_repo_files(lang, repo, ext_filters):
    def get_file_ext(file_name):
        splits = file_name.rsplit('.', maxsplit=1)
        # return just file name if doesn't have ext
        return splits[1] if len(splits) == 2 else splits[0]

    def save_file(file_name, file_content):
        print(os.getcwd(), '/{}/{}'.format(lang, file_name))
        with open('{}/{}/{}'.format(os.getcwd(), lang, file_name), 'w+') as writeable_file:
            writeable_file.write(file_content)

    repo_items = repo.get_contents('')
    while repo_items:
        repo_item = repo_items.pop(0)
        # print(repo_item.type, repo_item.name)
        if repo_item.type == 'dir':
            more_items = repo.get_contents(repo_item.path)
            if more_items:
                repo_items.extend(repo.get_contents(repo_item.path))
        elif repo_item.type == 'file' and get_file_ext(repo_item.name) in ext_filters:
            try:
                save_file(repo_item.name, base64_to_string(repo_item.content))
            except:
                pass
    print('{} processed'.format(repo.full_name))


if __name__ == '__main__':
    ray.init()
    lang = 'Java'
    max_repos = 3
    ext_filters = set(['java'])
    # repos = filter_english_only_repos(get_mostpopular_repos(lang, max_repos))
    repos = get_mostpopular_repos(lang, max_repos)
    print("{} filtered repos found".format(len(repos)))
    print_rate_limit()
    futures = [get_filter_save_repo_files.remote(
        lang, repo, ext_filters) for repo in repos]
    print(ray.get(futures))
    print_rate_limit()

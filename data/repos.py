import os
import json
import base64
import random
import string
import subprocess
import zipfile
import glob
import shutil
from pathlib import Path
import time
import sys

from constants import lang_dir, raw_dir, filtered_dir
from utilities import get_filename_from_path

import requests
import ray
from github import Github
from dotenv import load_dotenv

github = Github(os.getenv('GITHUB_ACCESS_TOKEN'), per_page=100)
load_dotenv()


def print_rate_limit():
    rate_limit = github.get_rate_limit()
    print(f'rate limit (core/search): {rate_limit.core}/{rate_limit.search}')


def get_mostpopular_repos(max_repos=100):
    def save_repo_data(repo):
        with open('repos.txt', 'a+') as repo_file:
            repo_file.write(
                f'{repo.full_name},{repo.html_url},{repo.stargazers_count}\n')
    repos = []
    repositories = github.search_repositories(
        query='language:Python', sort='stars')
    for i, repo in zip(range(max_repos), repositories):
        repos.append(repo)
        save_repo_data(repo)
        print(f'got repo {i} info: {repo.full_name}')
    print(f'{len(repos)} repos found')
    return repos


@ray.remote
def get_and_filter_repo_files(repo, raw_dir, filtered_dir):
    def rand_folder_name_gen():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    download_url = repo.archive_url.replace(
        '{archive_format}{/ref}', 'zipball/master'
    )

    repo_zip_path = os.path.join(raw_dir, f'{repo.name}.zip')
    repo_unzip_path = os.path.join(raw_dir, rand_folder_name_gen())
    curl_cmd = f'curl -u \"{os.getenv("GITHUB_USERNAME")}:{os.getenv("GITHUB_ACCESS_TOKEN")}\" -Lk {download_url} -o {repo_zip_path}'

    try:
        Path(raw_dir).mkdir(parents=True)
        Path(filtered_dir).mkdir(parents=True)
        Path(repo_unzip_path).mkdir(parents=True)
    except:
        pass

    try:
        # to not spam github with all requests at once
        time.sleep(random.randint(1, 5))
        print(curl_cmd)
        subprocess.run(curl_cmd, shell=True, text=True)

        with zipfile.ZipFile(repo_zip_path) as repo_zip:
            repo_zip.extractall(repo_unzip_path)

        matching_files = configfiles = glob.glob(
            f'{repo_unzip_path}/**/*.py', recursive=True)
        print(f'{len(matching_files)} matching files found in {repo.full_name} repo')
        for old_file_path in matching_files:
            new_file_path = os.path.join(
                filtered_dir, get_filename_from_path(old_file_path))
            shutil.move(old_file_path, new_file_path)

    except Exception as e:
        print(e)


def final_steps(raw_dir, filtered_dir):
    num_files = len([f for f in os.listdir(
        filtered_dir)if os.path.isfile(os.path.join(filtered_dir, f))])
    print(f'{num_files} total files collected')
    # remove zip files and unzipped folders
    if os.path.isdir(raw_dir):
        shutil.rmtree(raw_dir)


if __name__ == '__main__':
    ray.init()
    max_repos = 1000

    repos = get_mostpopular_repos(max_repos)
    print_rate_limit()
    futures = [get_and_filter_repo_files.remote(
        repo, raw_dir, filtered_dir) for repo in repos]
    ray.get(futures)
    print_rate_limit()
    final_steps(raw_dir, filtered_dir)

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

import ray
from github import Github
from dotenv import load_dotenv
from tqdm import tqdm

github = Github(os.getenv('GITHUB_ACCESS_TOKEN'), per_page=100)
load_dotenv()


def print_rate_limit():
    rate_limit = github.get_rate_limit()
    print(f'rate limit (core/search): {rate_limit.core}/{rate_limit.search}')


def create_relevant_dirs():
    try:
        if not os.path.exists(raw_dir):
            Path(raw_dir).mkdir(parents=True)
        if not os.path.exists(filtered_dir):
            Path(filtered_dir).mkdir(parents=True)
    except Exception as e:
        print(e)


def get_mostpopular_repos(max_repos=100):
    def save_repo_data(repo):
        with open('repos.txt', 'a+') as repo_file:
            repo_file.write(
                f'{repo.full_name},{repo.html_url},{repo.stargazers_count}\n')
    repos = []
    repositories = github.search_repositories(
        query='language:Python', sort='stars')
    print('Collecting GitHub repos metadata:')
    for i, repo in tqdm(zip(range(max_repos), repositories)):
        repos.append(repo)
        save_repo_data(repo)
    return repos


@ray.remote
def get_and_filter_repo_files(repo):
    def rand_folder_name_gen():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    download_url = repo.archive_url.replace(
        '{archive_format}{/ref}', 'zipball/master'
    )

    repo_zip_path = os.path.join(raw_dir, f'{repo.name}.zip')
    repo_unzip_path = os.path.join(raw_dir, rand_folder_name_gen())
    curl_cmd = f'curl -u \"{os.getenv("GITHUB_USERNAME")}:{os.getenv("GITHUB_ACCESS_TOKEN")}\" -Lk {download_url} -o {repo_zip_path}'

    try:
        Path(repo_unzip_path).mkdir(parents=True)
    except Exception as e:
        print(e)

    try:
        # to not spam github with all requests at once
        time.sleep(random.randint(1, 5))
        subprocess.run(curl_cmd, shell=True, text=True)

        with zipfile.ZipFile(repo_zip_path) as repo_zip:
            repo_zip.extractall(repo_unzip_path)

        matching_files = configfiles = glob.glob(
            f'{repo_unzip_path}/**/*.py', recursive=True)
        print(f'{len(matching_files)} matching files found in {repo.full_name} repo')
        for old_file_path in tqdm(matching_files):
            new_file_path = os.path.join(
                filtered_dir, get_filename_from_path(old_file_path))
            shutil.move(old_file_path, new_file_path)
    except Exception as e:
        print(e)


def final_steps(raw_dir, filtered_dir):
    num_files = len([f for f in os.listdir(filtered_dir)
                     if os.path.isfile(os.path.join(filtered_dir, f))])
    print(f'{num_files} total files collected')
    # remove zip files and unzipped folders
    if os.path.isdir(raw_dir):
        shutil.rmtree(raw_dir)


if __name__ == '__main__':
    ray.init()
    create_relevant_dirs()
    max_repos = 1000
    repos = get_mostpopular_repos(max_repos)
    print_rate_limit()
    futures = [get_and_filter_repo_files.remote(repo) for repo in repos]
    ray.get(futures)
    print("Shutting down Ray...")
    ray.shutdown()
    print_rate_limit()
    final_steps(raw_dir, filtered_dir)

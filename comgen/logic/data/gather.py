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

from comgen.constants import lang_dir, raw_dir, filtered_dir, repos_path
from comgen.utilities import get_filename_from_path

import ray
from tqdm import tqdm


def print_rate_limit(github_client):
    rate_limit = github_client.get_rate_limit()
    print(f'rate limit (core/search): {rate_limit.core}/{rate_limit.search}')


def create_relevant_dirs():
    try:
        if not os.path.exists(raw_dir):
            Path(raw_dir).mkdir(parents=True)
        if not os.path.exists(filtered_dir):
            Path(filtered_dir).mkdir(parents=True)
    except Exception as e:
        print(e)


def get_mostpopular_repos(github_client, max_repos=100):
    def save_repo_data(repo):
        with open(repos_path, 'a+') as repo_file:
            repo_file.write(
                f'{repo.full_name},{repo.html_url},{repo.stargazers_count}\n')
    repos = []
    repositories = github_client.search_repositories(
        query='language:Python', sort='stars')
    print('Collecting GitHub repos metadata:')
    for i, repo in tqdm(zip(range(max_repos), repositories)):
        repos.append(repo)
        save_repo_data(repo)
    return repos


@ray.remote
def get_and_filter_repo_files(repo, github_username, github_access_token):
    def rand_folder_name_gen():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    download_url = repo.archive_url.replace(
        '{archive_format}{/ref}', 'zipball/master'
    )

    repo_zip_path = os.path.join(raw_dir, f'{repo.name}.zip')
    repo_unzip_path = os.path.join(raw_dir, rand_folder_name_gen())
    curl_cmd = f'curl -u \"{github_username}:{github_access_token}\" -Lk {download_url} -o {repo_zip_path}'

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
    # remove zip files and unzipped folders
    if os.path.isdir(raw_dir):
        print("Removing raw folder...")
        shutil.rmtree(raw_dir)
    num_files = len([f for f in os.listdir(filtered_dir)
                     if os.path.isfile(os.path.join(filtered_dir, f))])
    print(f'{num_files} total files collected')

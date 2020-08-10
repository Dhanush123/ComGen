
import os
import sys

import ray
from dotenv import load_dotenv
from github import Github

from comgen.logic.data.gather import create_relevant_dirs, get_repo_info, get_and_filter_repo_files, final_steps, print_rate_limit
from comgen.constants import lang_dir, raw_dir, filtered_dir, repos_path

if __name__ == '__main__':
    load_dotenv()
    github_username, github_name, github_access_token = os.getenv(
        'GITHUB_USERNAME'), os.getenv('GITHUB_NAME'), os.getenv('GITHUB_ACCESS_TOKEN')
    create_relevant_dirs()
    repos_index = sys.argv[1]  # 1 <= repos_index <= 29
    subset_repos_path = repos_path.replace('.csv', f'-{repos_index}.csv')
    repos_info = get_repo_info(subset_repos_path)
    print_rate_limit(github_username, github_access_token)
    ray.init()
    futures = [get_and_filter_repo_files.remote(
        repo_name, repo_archive_url, github_username, github_access_token) for repo_name, repo_archive_url in repos_info]
    ray.get(futures)
    ray.shutdown()
    print_rate_limit(github_username, github_access_token)
    final_steps(raw_dir, filtered_dir)

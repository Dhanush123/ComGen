
import os

import ray
from dotenv import load_dotenv
from github import Github

from comgen.logic.data.gather import create_relevant_dirs, get_mostpopular_repos, print_rate_limit, get_and_filter_repo_files, final_steps
from comgen.constants import lang_dir, raw_dir, filtered_dir

if __name__ == '__main__':
    load_dotenv()
    github_username, github_access_token = os.getenv(
        "GITHUB_USERNAME"), os.getenv('GITHUB_ACCESS_TOKEN')
    github_client = Github(github_access_token, per_page=100)
    # ray.init()
    # create_relevant_dirs()
    # max_repos = 1000
    # print_rate_limit(github_client)
    # repos = get_mostpopular_repos(github_client, max_repos)
    # futures = [get_and_filter_repo_files.remote(
    #     repo, github_username, github_access_token) for repo in repos]
    # ray.get(futures)
    print("Shutting down Ray...")
    ray.shutdown()
    print_rate_limit(github_client)
    final_steps(raw_dir, filtered_dir)

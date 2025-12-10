import os
import json
import requests
from time import sleep
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIG ----------
GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER: str = "BaseMax"
CACHE_FILE: str = "repos_cache.json"
MERGE_METHOD: str = "squash"  # merge, squash, or rebase
REQUEST_DELAY: int = 2        # seconds to sleep between API requests
REPO_DELAY: int = 3           # seconds to sleep between repositories
HEADERS: Dict[str, str] = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# ---------- HELPER FUNCTIONS ----------
def log(message: str) -> None:
    print(f"[LOG] {message}")


def fetch_all_repos() -> List[Dict]:
    """Fetch all repositories for the authenticated user and cache them"""
    if os.path.exists(CACHE_FILE):
        log(f"Loading cached repositories from {CACHE_FILE}")
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    log("Fetching repositories from GitHub...")
    repos: List[Dict] = []
    page: int = 1
    while True:
        # url: str = f"https://api.github.com/user/repos?per_page=100&page={page}"
        url: str = f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch repos: {resp.text}")
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        sleep(REQUEST_DELAY)

    with open(CACHE_FILE, "w") as f:
        json.dump(repos, f, indent=2)
        log(f"Cached {len(repos)} repositories to {CACHE_FILE}")

    return repos


def fetch_open_prs(repo_full_name: str) -> List[Dict]:
    """Fetch all open pull requests for a repository"""
    prs: List[Dict] = []
    page: int = 1
    while True:
        url: str = f"https://api.github.com/repos/{repo_full_name}/pulls?state=open&per_page=100&page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            log(f"Failed to fetch PRs for {repo_full_name}: {resp.text}")
            break
        data = resp.json()
        if not data:
            break
        prs.extend(data)
        page += 1
        sleep(REQUEST_DELAY)
    return prs


def fetch_pr_details(repo_full_name: str, pr_number: int) -> Optional[Dict]:
    """Fetch details for a single PR"""
    url: str = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        log(f"Failed to fetch PR details #{pr_number}: {resp.text}")
        return None
    sleep(REQUEST_DELAY)
    return resp.json()


def merge_pr(repo_full_name: str, pr_number: int) -> bool:
    """Try to merge a PR"""
    url: str = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/merge"
    resp = requests.put(url, headers=HEADERS, json={"merge_method": MERGE_METHOD})
    if resp.status_code == 200:
        log(f"Merged PR #{pr_number} successfully in {repo_full_name}")
        return True
    else:
        log(f"Failed to merge PR #{pr_number} in {repo_full_name}: {resp.text}")
        return False


def comment_pr(repo_full_name: str, pr_number: int, message: str) -> bool:
    """Add a comment to a PR"""
    url: str = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    resp = requests.post(url, headers=HEADERS, json={"body": message})
    if resp.status_code == 201:
        log(f"Commented on PR #{pr_number} in {repo_full_name}")
        return True
    else:
        log(f"Failed to comment on PR #{pr_number} in {repo_full_name}: {resp.text}")
        return False


def handle_dependabot_pr(repo_full_name: str, pr: Dict) -> None:
    """Check mergeability and merge or comment"""
    pr_number: int = pr["number"]
    pr_title: str = pr["title"]
    mergeable: Optional[bool] = pr.get("mergeable")

    if mergeable is None:
        sleep(5)
        pr_details = fetch_pr_details(repo_full_name, pr_number)
        mergeable = pr_details.get("mergeable") if pr_details else False

    log(f"PR #{pr_number}: {pr_title} -> mergeable: {mergeable}")

    if mergeable:
        merge_pr(repo_full_name, pr_number)
    else:
        comment_pr(repo_full_name, pr_number, "@dependabot recreate")


def process_repository(repo: Dict) -> None:
    """Process all open Dependabot PRs in a repository"""
    full_name: str = repo["full_name"]
    log(f"Checking repository: {full_name}")

    prs: List[Dict] = fetch_open_prs(full_name)
    dependabot_prs: List[Dict] = [pr for pr in prs if pr["user"]["login"] == "dependabot[bot]"]

    log(f"Found {len(dependabot_prs)} Dependabot PR(s) in {full_name}")

    for pr in dependabot_prs:
        handle_dependabot_pr(full_name, pr)

    sleep(REPO_DELAY)


# ---------- MAIN SCRIPT ----------
def main() -> None:
    repos: List[Dict] = fetch_all_repos()
    log(f"Total repositories to process: {len(repos)}")

    for repo in repos:
        process_repository(repo)


if __name__ == "__main__":
    main()

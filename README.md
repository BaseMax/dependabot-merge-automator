# Dependabot Merge Automator

[![GitHub](https://img.shields.io/badge/github-BaseMax-blue)](https://github.com/BaseMax/dependabot-merge-automator)

> A Python tool to manage security and dependency updates across multiple repositories by automatically merging Dependabot PRs or requesting updates when conflicts occur.

Automate the merging of Dependabot pull requests across all your GitHub repositories. This Python script fetches all your repositories, detects open Dependabot PRs, merges them automatically if possible, or requests a rebase using `@dependabot recreate` if conflicts are detected.

---

## Features

- Fetch all repositories for a user or organization
- Detect open Dependabot PRs
- Automatically merge mergeable PRs using your preferred merge method (`squash`, `merge`, or `rebase`)
- Comment on PRs with conflicts to request a rebase (`@dependabot recreate`)
- Caches repository list for faster subsequent runs
- Configurable delays to avoid GitHub API rate limits
- Logs actions for full transparency

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/BaseMax/dependabot-merge-automator.git
cd dependabot-merge-automator
```

2. Install dependencies:

```bash
pip3 install -r requirements.txt
```

3. Create a `.env` file in the project root:

```bash
GITHUB_TOKEN=your_personal_access_token_here
```

Make sure your token has at least the following permissions:

* `repo` (for private repositories)
* `public_repo` (for public repositories)
* `read:org` (if accessing organization repositories)

---

## Usage

Run the script:

```bash
python3 merger.py
```

The script will:

1. Fetch all repositories for your GitHub user
2. Check for open Dependabot PRs
3. Merge PRs automatically if possible
4. Comment on PRs with conflicts requesting `@dependabot recreate`

---

## Configuration

* `MERGE_METHOD`: Choose `merge`, `squash`, or `rebase`
* `REQUEST_DELAY`: Seconds to sleep between API requests (default: 2)
* `REPO_DELAY`: Seconds to sleep between processing repositories (default: 3)
* `CACHE_FILE`: File to cache repository list (default: `repos_cache.json`)

You can edit these directly in `merger.py` or enhance the script to read from environment variables.

---

## License

MIT License

---

## Author

Seyyed Ali Mohammadiyeh (Max Base)

[GitHub Profile](https://github.com/BaseMax)

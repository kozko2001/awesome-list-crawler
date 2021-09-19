from pathlib import Path

from awesome_crawler.awesome_repo import process_awesome_repo

if __name__ == "__main__":
    repos = ["https://github.com/TheJambo/awesome-testing"]

    dest = Path("/tmp/xxx")

    for repo_url in repos:
        process_awesome_repo(repo_url)

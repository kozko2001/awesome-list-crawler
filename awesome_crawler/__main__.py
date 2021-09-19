from pathlib import Path

from awesome_crawler.awesome_repo import clone, extract_all_commits

if __name__ == "__main__":
    repos = ["https://github.com/TheJambo/awesome-testing"]

    dest = Path("/tmp/xxx")

    for repo_url in repos:
        repo = clone(repo_url, dest)
        x = extract_all_commits(repo)

        for y in x:
            print("---------------")
            print(y)

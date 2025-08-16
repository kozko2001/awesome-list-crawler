import time

from github import Github

from awesome_crawler.awesome_repo import process_awesome_repo
from awesome_crawler.process import AwesomeList


def from_awesome_awesome():
    list_of_awesome_projects = [
        AwesomeList(p.item.name, p.item.source, p.item.description)
        for p in process_awesome_repo("https://github.com/sindresorhus/awesome", 1)
    ]

    return list_of_awesome_projects


def from_github_topics():
    g = Github(per_page=100)

    paginated = g.search_repositories("topic:awesome-list")
    lists = []
    for i, repo in enumerate(paginated):
        r = AwesomeList(repo.name, repo.html_url, repo.description)
        print(r, i)
        lists.append(r)
        if i % 100 == 0:
            time.sleep(6)
    return lists


def find_repos():
    awesome_awesome = from_awesome_awesome()
    # github_topics = from_github_topics()

    # duplicated_urls = set([r.source.strip().replace("#readme", "") for r in awesome_awesome]) & set([r.source.strip() for r in github_topics])
    # github_topics = list(filter(lambda r: r.source not in duplicated_urls, github_topics))

    # repos = awesome_awesome + github_topics
    repos = awesome_awesome[0:20]

    return repos

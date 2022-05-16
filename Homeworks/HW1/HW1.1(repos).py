import json
import requests
from pprint import pprint
from tokens import git_token

GITHUB_TOKEN = git_token
USERNAME = "Androkotey"


def main():
    search = 'Androkotey'

    url = f"https://api.github.com/users/{search}/repos"
    response = requests.get(url, auth=(USERNAME, GITHUB_TOKEN))
    j_data = response.json()

    with open(f'{search.lower()}_github.txt', 'w', encoding='utf-8') as f:
        json.dump(j_data, f)

    repos = dict()
    for repo in j_data:
        repos[repo['full_name']] = repo['html_url']

    pprint(repos)


if __name__ == '__main__':
    main()

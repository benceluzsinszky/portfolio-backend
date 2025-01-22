import requests


class Scraper:
    def __init__(self, username, db):
        self.username = username
        self.db = db
        self.repos = []

    def get_repos(self):
        try:
            response = requests.get(
                f"https://api.github.com/users/{self.username}/repos"
            )
            if not response.ok:
                print(f"Failed to get repos for {self.username}")
                return

            repos_dict = response.json()
            for repo in repos_dict:
                self.repos.append(repo["name"])
            return

        except requests.exceptions.RequestException as e:
            print(e)
            return

    def get_contributions(self):
        # contributions: loop "https://api.github.com/repos/{name}/{repo}/contributors" and count "contributions"
        pass

    def get_languages(self):
        # language usage: loop "https://api.github.com/repos/{name}/{repo}/languages" and count "bytes" for each languag
        pass

    def get_lines_pushed(self):
        # lines pushed:  loop repos, pull each to ../repos/{repo}, count lines in each files recursively
        pass

    def run(self):
        self.get_repos()
        self.get_contributions()
        self.get_languages()
        self.get_lines_pushed()


if __name__ == "__main__":
    ...

import requests
import dotenv
import os
import logging
from logging.handlers import SysLogHandler
import platform
from datetime import datetime


class Scraper:
    def __init__(self, username: str, token: str, db: str):
        self.username = username
        self.auth_header = {"Authorization": f"token {token}"}
        self.db = db
        self.repos = []

        self.logger = logging.getLogger("ScraperLogger")
        self.logger.setLevel(logging.INFO)

        if platform.system() == "Linux":
            handler = SysLogHandler(address="/dev/log")
        else:
            handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_repos(self):
        try:
            response = requests.get(
                f"https://api.github.com/users/{self.username}/repos",
                headers=self.auth_header,
            )
            if not response.ok:
                self.logger.error(f"Failed to get repos for {self.username}")
                return

            repos_dict = response.json()
            for repo in repos_dict:
                self.repos.append(repo["name"])

            self.logger.info(f"Successfully retrieved repos for {self.username}")
            return

        except requests.exceptions.RequestException as e:
            self.logger.error(f"RequestException: {e}")
            return

    def get_last_year_contributions(self):
        try:
            query = f"""
                    query {{
                        user(login: "{self.username}") {{
                            name
                            contributionsCollection {{
                                contributionCalendar {{
                                    colors
                                    totalContributions
                                    weeks {{
                                        contributionDays {{
                                            date
                                            contributionLevel
                                            contributionCount
                                        }}
                                        firstDay
                                    }}
                                }}
                            }}
                        }}
                    }}
                    """
            response = requests.post(
                "https://api.github.com/graphql",
                headers=self.auth_header,
                json={"query": query},
            )
            data = response.json()
            response_calendar = data["data"]["user"]["contributionsCollection"][
                "contributionCalendar"
            ]
            calendar = {}
            for week in response_calendar["weeks"]:
                for day in week["contributionDays"]:
                    level = self._parse_level(day["contributionLevel"])
                    date = day["date"]
                    count = day["contributionCount"]
                    calendar[date] = {"level": level, "count": count}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"RequestException: {e}")
            return

    def _parse_level(self, level):
        match level:
            case "NONE":
                return 0
            case "FIRST_QUARTILE":
                return 1
            case "SECOND_QUARTILE":
                return 2
            case "THIRD_QUARTILE":
                return 3
            case "FOURTH_QUARTILE":
                return 4
        return 0

    def get_all_contributions(self):
        contributions = 0
        this_year = datetime.now().year
        for year in range(2022, this_year + 1):
            try:
                query = f"""
                    query {{
                        user(login: "{self.username}") {{
                            contributionsCollection(to: "{year}-12-31T00:00:00Z") {{
                                restrictedContributionsCount
                                contributionCalendar {{
                                    totalContributions
                                }}
                            }}
                        }}
                    }}
                    """
                response = requests.post(
                    "https://api.github.com/graphql",
                    headers=self.auth_header,
                    json={"query": query},
                )
                data = response.json()
                contributions_collection = data["data"]["user"][
                    "contributionsCollection"
                ]

                yearly_contributions = (
                    contributions_collection["contributionCalendar"][
                        "totalContributions"
                    ]
                    + contributions_collection["restrictedContributionsCount"]
                )

                contributions += yearly_contributions

            except requests.exceptions.RequestException as e:
                self.logger.error(f"RequestException: {e}")
                return

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
    dotenv.load_dotenv()
    USERNAME = os.getenv("USERNAME")
    TOKEN = os.getenv("GITHUB_PAT")
    DB = "db"  # will deal with this later

    scraper = Scraper(USERNAME, TOKEN, "db")
    scraper.get_all_contributions()

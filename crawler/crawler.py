import requests
import dotenv
import os
import subprocess
import logging
from datetime import datetime
from db.core import get_db
from db.models import (
    DBTotalContributions,
    DBLanguageUsage,
    DBTotalLines,
    DBLastYearContributions,
)
from sqlalchemy.orm import Session

ACCEPTABLE_EXTENSIONS = acceptable_extensions = [
    ".py",
    ".js",
    "jsx",
    ".ts",
    "tsx",
    ".html",
    ".css",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".rs",
    ".pl",
    ".m",
    ".r",
    ".lua",
    ".scala",
    ".dart",
    ".groovy",
    ".tsv",
    ".md",
    ".sh",
]


class Crawler:
    def __init__(self, username: str, token: str, db: Session):
        self.username = username
        self.auth_header = {"Authorization": f"token {token}"}
        self.session = db
        self.repos = []
        self.total_lines = 0

        self.logger = logging.getLogger("CrawlerLogger")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _fetch_repos(self):
        response = requests.get(
            f"https://api.github.com/users/{self.username}/repos",
            headers=self.auth_header,
        )
        if not response.ok:
            self.logger.error("Failed to get repos")
            raise requests.exceptions.RequestException(response.text)

        return response.json()

    def get_repos(self):
        try:
            repos_dict = self._fetch_repos()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"RequestException: {e}")
            return

        for repo in repos_dict:
            self.repos.append(repo["name"])

        self.logger.info("Successfully retrieved repos")

    def _fetch_last_year_contributions(self):
        query = f"""
                query {{
                    user(login: "{self.username}") {{
                        name
                        contributionsCollection {{
                            contributionCalendar {{
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
        return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

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

    def _parse_calendar(self, response_calendar):
        calendar = []
        for week in response_calendar["weeks"]:
            for day in week["contributionDays"]:
                level = self._parse_level(day["contributionLevel"])
                date = datetime.strptime(day["date"], "%Y-%m-%d")
                count = day["contributionCount"]
                calendar.append({"date": date, "level": level, "count": count})
        return calendar

    def get_last_year_contributions(self):
        try:
            response_calendar = self._fetch_last_year_contributions()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"RequestException: {e}")
            return

        calendar = self._parse_calendar(response_calendar)

        self.logger.info("Successfully retrieved last years contributions")

        with self.session as session:
            session.query(DBLastYearContributions).delete()
            for day in calendar:
                last_year_contributions = DBLastYearContributions(
                    date=day["date"], count=day["count"], level=day["level"]
                )
                session.add(last_year_contributions)
            session.commit()
            self.logger.info("Successfully saved last year contributions to database")

    def _fetch_yearly_contributions(self, year):
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
        return data["data"]["user"]["contributionsCollection"]

    def get_total_contributions(self):
        contributions = 0
        this_year = datetime.now().year
        for year in range(2022, this_year + 1):
            try:
                contributions_collection = self._fetch_yearly_contributions(year)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"RequestException: {str(e)}")
                continue

            contributions += contributions_collection["contributionCalendar"][
                "totalContributions"
            ]

            contributions += contributions_collection["restrictedContributionsCount"]

            self.logger.info(f"Successfully retrieved contributions for {year}")

        if contributions == 0:
            self.logger.error("No contributions found")
            return

        with self.session as session:
            session.query(DBTotalContributions).delete()
            total_contributions = DBTotalContributions(
                total_contributions=contributions
            )
            session.add(total_contributions)
            session.commit()
            self.logger.info("Successfully saved total contributions to database")

    def _get_repo_languages(self, repo):
        response = requests.get(
            f"https://api.github.com/repos/{self.username}/{repo}/languages",
            headers=self.auth_header,
        )
        if not response.ok:
            self.logger.error(f"Failed to get languages for repository {repo}")
            return

        return response.json()

    def _parse_languages(self, languages, repo_languages):
        for language, bytes in repo_languages.items():
            if language in languages:
                languages[language] += bytes
            else:
                languages[language] = bytes

        return languages

    def get_language_usage(self):
        if not self.repos:
            self.logger.error("No repos found")
            return

        languages = {}

        for i, repo in enumerate(self.repos):
            try:
                repo_languages = self._get_repo_languages(repo)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"RequestException: {str(e)}")
                continue

            languages = self._parse_languages(languages, repo_languages)

            self.logger.info(f"Successfully retrieved languages for repository {i}")

        self.logger.info("Successfully retrieved languages")

        with self.session as session:
            session.query(DBLanguageUsage).delete()

            for language, count in languages.items():
                language_usage = DBLanguageUsage(language=language, count=count)
                session.add(language_usage)
            session.commit()
            self.logger.info("Successfully saved languages to database")

    def _clone_repo(self, repo, i):
        repo_path = f"./repos/{repo}"
        self.logger.info(f"Cloning repository {i}")
        subprocess.run(
            [
                "git",
                "clone",
                f"https://github.com/{self.username}/{repo}",
                repo_path,
            ],
            check=True,
        )

    def _pull_repo(self, repo_path):
        self.logger.info("Pulling latest changes")
        subprocess.run(["git", "-C", repo_path, "pull"], check=True)

    def _count_lines(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                self.total_lines += sum(1 for _ in f)
            except Exception as e:
                self.logger.error(f"Failed to read file {file_path}: {str(e)}")

    def _walk_files(self, repo):
        for root, _, files in os.walk(f"./repos/{repo}"):
            for file in files:
                if file.endswith(tuple(ACCEPTABLE_EXTENSIONS)):
                    file_path = os.path.join(root, file)
                    self._count_lines(file_path)

    def get_total_lines(self):
        for i, repo in enumerate(self.repos):
            repo_path = f"./repos/{repo}"
            if not os.path.exists(repo_path):
                self._clone_repo(repo, i)
            else:
                self._pull_repo(repo_path)

            self._walk_files(repo)

            self.logger.info(f"Successfully counted total lines for repository {i}")

        with self.session as session:
            session.query(DBTotalLines).delete()
            total_lines = DBTotalLines(total_lines=self.total_lines)
            session.add(total_lines)
            session.commit()
            self.logger.info("Successfully saved total lines to database")

    def run(self):
        self.logger.info("Starting crawler")
        self.get_repos()
        self.get_last_year_contributions()
        self.get_total_contributions()
        self.get_language_usage()
        self.get_total_lines()
        self.logger.info("Crawler finished")


if __name__ == "__main__":
    dotenv.load_dotenv()
    USERNAME = os.getenv("USERNAME")
    TOKEN = os.getenv("GITHUB_PAT")

    db_session = next(get_db())
    Crawler = Crawler(username=USERNAME, token=TOKEN, db=db_session)
    Crawler.run()

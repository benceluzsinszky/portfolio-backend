# Portfolio Backend

The aim of the project is to provide data that is visualized on my [portfolio website](https://benceluzsinszky.com).

The frontend is written in React TypeScript and can be found [here](https://github.com/benceluzsinszky/portfolio).

The backend consists of two parts:

1. **DataCrawler** that fetches data from GitHub and stores it in a database
2. **RESTful API** built with FastAPI

## Installation

```bash
pip install -r requirements.txt
```

## Features

### DataCrawler

The DataCrawler fetches 4 types of data from GitHub:

1. **Last year's contributions**: used for the GitHub contribution chart
2. **Total contributions**: counts the total number of GitHub contributions
3. **Language usage**: counts the number of bytes written in each language, used for a language usage pie chart
4. **Total lines**: counts the lines of code pushed to GitHub

The contributions are fetched from the GitHub GraphQL API.
The language usage and total lines are fetched from the GitHub REST API.

### API

The API provides 4 endpoints:

1. `/last_years_contributions`: returns the last year's contributions
2. `/total_contributions`: returns the total number of contributions
3. `/language_usage`: returns the language usage
4. `/total_lines`: returns the total number of lines

The documentation for the API is automatically generated by FastAPI and can be found at `/docs` endpoint.

## Usage

### Configuration

The configuration is done through environment variables.
The following environment variables are required:

**USERNAME**: GitHub username for the DataCrawler
**GITHUB_PAT**: [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for the DataCrawler
**API_KEY**: API key to authenticate the FastAPI app
**DATABASE_URL**: Database connection string for the DataCrawler and the API

### Running the DataCrawler

```bash
python crawler/crawler.py
```

### Running the API

Development:

```bash
uvicorn api.main:app --reload
```

Production:

```bash
docker build -t portfolio-backend .
docker run -d -p [PORT]:[PORT] portfolio-backend
```

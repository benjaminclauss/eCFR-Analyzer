# eCFR Analyzer

## Project Description

> The goal of this project is to create a simple website to analyze Federal Regulations.
> The eCFR is available at https://www.ecfr.gov/. There is a public API for it.
>
> Please write code to download the current eCFR and analyze it for items such as word count per agency and historical
> changes over time.
> Feel free to add your own custom metrics.
>
> There should be a front end visualization for the content where we can click around and ideally query items.
> Additionally, there should be a public GitHub project with the code.

## Architecture

- **Web Application**: [Streamlit](https://github.com/streamlit/streamlit)
  on [Streamlit Community Cloud](https://streamlit.io/cloud)
    - **Analytics
      **: [Streamlit App Analytics](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-analytics)
- **Metrics Backend**: [Redis](https://redis.io/) on [Upstash](https://upstash.com/)

## Getting Started

### Prerequisites

Ensure [Python](https://www.python.org/downloads/) in installed.

### Setup

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

### Configuration

Define `secrets.toml` and/or the following environment variables.

```toml
REDIS_URL = "hostname"
REDIS_PORT = 6379
REDIS_PASSWORD = "password"
```

### Run Application

```shell
streamlit run app.py
```

### Generate Metrics

Generate metrics for all Agencies and persist to Redis:

```shell
 python -m scripts.calculate_agency_metrics
```

## Metrics

- **Word Count** - Total word count for Federal Agency associated CFR content.

### [Readability](https://pypi.org/project/py-readability-metrics/)

- **Flesch-Kincaid Grade Level** - Estimates the US school grade required to understand the text. A higher score is
  easier to read.
- **Flesch Reading Ease** – A score from 0 to 100; higher is easier to read. A higher score is easier ot read.
- **SMOG Index** – Best for regulatory/legal documents, estimating the number of years of education needed. A higher
  score indicates worse readability. 

## Wishlist

- [ ] Add proper [testing](https://docs.streamlit.io/develop/api-reference/app-testing).
- [ ] Create properly scheduled, deployed batch job for data processing.
- [ ] Add proper Python linting (e.g., quote consistency).
- [ ] Allow different periodicity for various graphs.
- [ ] Add first-class date filtering (i.e., beyond DataFrame possible) in more places.
- [ ] Add readability metrics for Titles.
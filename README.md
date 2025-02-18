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
  - **Analytics**: [Streamlit App Analytics](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-analytics)
- **Metrics Backend**: [Redis](https://redis.io/) on [Upstash](https://upstash.com/)

## Setup

Ensure [Python](https://www.python.org/downloads/) in installed.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

Run application:

```
streamlit run app.py
```

Generate metrics for all Agencies and persist to Redis:

```shell
 python -m scripts.calculate_word_counts
```

## Metrics

- **Word Count** - Total word count for Federal Agency associated CFR content. 
 
### [Readability](https://pypi.org/project/py-readability-metrics/)
- **Flesch-Kincaid Grade Level** - Estimates the US school grade required to understand the text.
- **Flesch Reading Ease** – A score from 0 to 100; higher is easier to read.
- **SMOG Index** – Best for regulatory/legal documents, estimating the number of years of education needed.

## Wishlist

- [ ] Create properly scheduled batch job for data processing.
- [ ] Add proper Python linting (e.g., quote consistency).
- [ ] Allow different periodicity for Corrections graph.
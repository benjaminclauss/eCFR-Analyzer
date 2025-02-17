# eCFR Analyzer

## Project Description

The goal of this project is to create a simple website to analyze Federal Regulations. 
The eCFR is available at https://www.ecfr.gov/. There is a public API for it.

Please write code to download the current eCFR and analyze it for items such as word count per agency and historical
changes over time.
Feel free to add your own custom metrics.

There should be a front end visualization for the content where we can click around and ideally query items. 
Additionally, there should be a public GitHub project with the code.

## Architecture

- **Web Application**: [Streamlit](https://github.com/streamlit/streamlit) on [Streamlit Community Cloud](https://streamlit.io/cloud)
- **Metrics Backend**: [Redis](https://redis.io/) on [Upstash](https://upstash.com/)

## Run

Generate word counts for all agencies.

```shell
 python -m scripts.calculate_word_counts
```
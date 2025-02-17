import requests
import streamlit as st


@st.cache_data
def fetch_agencies():
    response = requests.get("https://www.ecfr.gov/api/admin/v1/agencies.json")
    if response.status_code == 200:
        return response.json().get("agencies", [])
    return None


ANCESTRY_API_URL = "https://www.ecfr.gov/api/versioner/v1/ancestry/{date}/title-{title}.json"


@st.cache_data
def fetch_ancestry_for_title(date, title, subtitle=None, chapter=None, subchapter=None, part=None, section=None):
    """Fetches the full ancestry for a given CFR reference."""
    url = ANCESTRY_API_URL.format(date=date, title=title)
    params = {}

    if subtitle: params["subtitle"] = subtitle
    if chapter: params["chapter"] = chapter
    if subchapter: params["subchapter"] = subchapter
    if part: params["part"] = part
    if section: params["section"] = section

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


@st.cache_data
def fetch_xml_for_title(date, title, subtitle=None, chapter=None, subchapter=None, part=None):
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"

    params = {}
    if subtitle:
        params["subtitle"] = subtitle
    if chapter:
        params["chapter"] = chapter
    if subchapter:
        params["subchapter"] = subchapter
    if part:
        params["part"] = part

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.text
    return None


@st.cache_data
def fetch_titles():
    response = requests.get("https://www.ecfr.gov/api/versioner/v1/titles.json")
    if response.status_code == 200:
        return response.json().get("titles", [])
    else:
        return None


@st.cache_data
def fetch_versions_for_title(title, gte=None, lte=None, on=None):
    base_url = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title}.json"

    params = {}
    if on:
        params["on"] = on
    elif gte:
        params["gte"] = gte
    elif lte:
        params["lte"] = lte

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

import requests
import streamlit as st


@st.cache_data
def fetch_agencies():
    response = requests.get("https://www.ecfr.gov/api/admin/v1/agencies.json")
    if response.status_code == 200:
        return response.json().get("agencies", [])
    return None


@st.cache_data
def fetch_titles():
    response = requests.get("https://www.ecfr.gov/api/versioner/v1/titles.json")
    if response.status_code == 200:
        return response.json().get("titles", [])
    else:
        return None


@st.cache_data
def get_versions(title, gte=None, lte=None, on=None):
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

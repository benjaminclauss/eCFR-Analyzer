import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("Titles")

@st.cache_data
def fetch_titles():
    response = requests.get("https://www.ecfr.gov/api/versioner/v1/titles.json")
    if response.status_code == 200:
        return response.json().get("titles", [])
    else:
        return None


@st.cache_data
def get_versions(title, gte=None, lte=None, on=None):
    """Fetches content versions from the eCFR API for a given title and date filters."""
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


titles_data = fetch_titles()

if titles_data:
    df = pd.DataFrame(titles_data).rename(columns={
        "number": "Title Number",
        "name": "Title Name",
        "latest_amended_on": "Last Amended",
        "latest_issue_date": "Last Issued",
        "up_to_date_as_of": "Up to Date As Of",
        "reserved": "Reserved"
    })

    df = df.drop(columns=["Reserved"])

    st.dataframe(df.set_index("Title Number"), use_container_width=True)
else:
    st.error("Failed to fetch eCFR titles. Try again later.")


titles_dict = {t['number']: t for t in titles_data}

# In the response, the date field is identical to amendment_date and is deprecated.
if titles_data:
    st.subheader("Title Versions")

    selected_title = st.selectbox(
        "Choose a CFR Title:",
        list(titles_dict.keys()),
        format_func=lambda t: str(t) + ": " + titles_dict[t]['name'],
    )

    versions = get_versions(selected_title)
    print(versions['meta'])

    df = pd.DataFrame(versions['content_versions'])

    st.dataframe(df, use_container_width=True)

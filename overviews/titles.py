import streamlit as st
import requests
import pandas as pd

st.title("Titles")
st.subheader("Summary information about each title")
st.text("The Title service can be used to determine the status of each individual title and of the overall status of title imports and reprocessings. It returns an array of all titles containing a hash for each with the name of the title, the latest amended date, latest issue date, up-to-date date, reserved status, and if applicable, processing in progress status. The meta data returned indicates the latest issue date and whether titles are currently being reprocessed.")

API_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"

# TODO: Download this data.

@st.cache_data
def fetch_titles():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json().get("titles", [])
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

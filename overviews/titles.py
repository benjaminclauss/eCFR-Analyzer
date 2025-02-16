import streamlit as st
import requests
import pandas as pd

st.title("Titles")
st.text("""The Code of Federal Regulations (CFR) is the codification of the general and permanent rules published in the Federal Register by the departments and agencies of the Federal Government. The Electronic Code of Federal Regulations (eCFR) is a point-in-time system that allows you to browse the Code of Federal Regulations as they existed at any point in time (since January 2017).

It is divided into 50 titles that represent broad areas subject to Federal regulation. Each title is divided into chapters, which usually bear the name of the issuing agency. Each chapter is further subdivided into parts that cover specific regulatory areas. Large parts may be subdivided into subparts. All parts are organized in sections, and most citations to the CFR refer to material at the section level.""")

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

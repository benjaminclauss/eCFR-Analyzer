import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("Agencies")

@st.cache_data
def fetch_agencies():
    response = requests.get("https://www.ecfr.gov/api/admin/v1/agencies.json")
    if response.status_code == 200:
        return response.json().get("agencies", [])
    else:
        return None

agencies_data = fetch_agencies()

if agencies_data:
    agencies = pd.DataFrame(agencies_data).set_index("sortable_name")
    st.metric("Total Agencies", len(agencies))

    overview = agencies.drop(columns=["display_name", "slug", "cfr_references", "children"])
    overview = overview.rename(columns={"name": "Name", "short_name": "Short Name"})
    st.dataframe(overview, hide_index=True, use_container_width=True)
else:
    st.error("Failed to fetch agencies. Try again later.")

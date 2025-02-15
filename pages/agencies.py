import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Agencies", page_icon="🏛", layout="wide")

st.title("Agencies")
st.text("All top-level agencies in name order with children also in name order")

API_URL = "https://www.ecfr.gov/api/admin/v1/agencies.json"

# TODO: Download this data.

@st.cache_data
def fetch_agencies():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json().get("agencies", [])
    else:
        return None

agencies_data = fetch_agencies()

if agencies_data:
    df = pd.DataFrame(agencies_data).set_index("sortable_name")

    df.head()
    print(df)

    st.dataframe(
        df,
        use_container_width=True
    )

else:
    st.error("Failed to fetch agencies. Try again later.")
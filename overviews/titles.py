import pandas as pd
import streamlit as st

from utils import ecfr

st.set_page_config(layout="wide")

titles_data = ecfr.fetch_titles()

st.title("Titles")

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

    st.subheader("Title Versions")

    titles_dict = {t['number']: t for t in titles_data}
    selected_title = st.selectbox(
        "Choose a CFR Title:",
        list(titles_dict.keys()),
        format_func=lambda t: str(t) + ": " + titles_dict[t]['name'],
    )

    versions_data = ecfr.fetch_versions_for_title(selected_title)

    meta = versions_data["meta"]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Latest Amendment Date", value=meta['latest_amendment_date'])
    with col2:
        st.metric(label="Latest Issue Date", value=meta['latest_issue_date'])
    with col3:
        st.header("An owl")


    st.text("The selected Title has the following Sections and Appendices.")
    content_versions = pd.DataFrame(versions_data['content_versions']).drop(columns=["date", "title"])
    content_versions = content_versions.set_index("identifier")
    st.dataframe(content_versions, use_container_width=True)

else:
    st.error("Failed to fetch Titles. Try again later.")

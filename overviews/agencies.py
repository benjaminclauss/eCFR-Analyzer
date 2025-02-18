import altair as alt
import json
import pandas as pd
import redis
import streamlit as st

from utils import ecfr

st.set_page_config(layout="wide")

st.title("Federal Agencies 🏛️")


@st.cache_resource
def get_redis_client():
    return redis.Redis(
        host=st.secrets["REDIS_URL"],
        port=st.secrets["REDIS_PORT"],
        password=st.secrets["REDIS_PASSWORD"],
        ssl=True
    )


r = get_redis_client()


@st.cache_data
def fetch_agencies():
    return ecfr.fetch_agencies()


def fetch_word_counts(agencies):
    slugs = agencies["slug"].tolist()
    agency_metrics = [json.loads(s) if s is not None else None for s in r.mget(slugs)]
    return [agency.get("total_word_count") if agency is not None else None for agency in agency_metrics]


with st.spinner("Fetching Agencies..."):
    agencies_data = fetch_agencies()

if agencies_data:
    agencies = pd.DataFrame(agencies_data["agencies"]).set_index("sortable_name")

    with st.spinner("Fetching word counts..."):
        agencies["Word Count"] = fetch_word_counts(agencies)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Agencies", len(agencies))
    with col2:
        st.metric("Average Word Count", round(agencies["Word Count"].mean(), 2))

    calculating_count = agencies["Word Count"].isnull().sum()
    if calculating_count > 0:
        st.progress(1 - (calculating_count / len(agencies)), text="Calculating Agency Word Counts...")

    overview = agencies.drop(columns=["display_name", "slug", "cfr_references", "children"], errors="ignore")
    overview = overview.rename(columns={"name": "Name", "short_name": "Short Name"})

    st.dataframe(overview, hide_index=True, use_container_width=True)

    with st.expander("Distribution of Word Counts", expanded=False):
        excluded_agencies = st.multiselect(
            "Exclude Agencies",
            options=overview["Name"],
            placeholder="Select Agencies to Exclude"
        )
        filtered_overview = overview[~overview["Name"].isin(excluded_agencies)].reset_index()

        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        with tab1:
            chart = alt.Chart(filtered_overview).mark_bar().encode(
                y=alt.Y("Name:N", sort="-x", axis=alt.Axis(title=None, labelLimit=500)),
                x=alt.X("Word Count:Q", title="Word Count")
            ).properties(width=1000, height=6000).configure_axis(labelFontSize=12, titleFontSize=14)
            st.altair_chart(chart, use_container_width=False)

        with tab2:
            chart = alt.Chart(filtered_overview).mark_arc().encode(
                theta=alt.Theta("Word Count:Q", title="Word Count"),
                color=alt.Color("Name:N", legend=None),  # Different colors for agencies
                tooltip=["Name", "Word Count"]  # Show details on hover
            ).properties(width=1000, height=1000)
            st.altair_chart(chart, use_container_width=False)
else:
    st.error("Failed to fetch Agencies. Try again later.")

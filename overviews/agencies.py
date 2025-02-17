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
else:
    st.error("Failed to fetch Agencies. Try again later.")

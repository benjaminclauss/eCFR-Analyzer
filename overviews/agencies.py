import altair as alt
import json
import pandas as pd
import redis
import streamlit as st

from utils import ecfr

st.set_page_config(layout="wide")

st.title("Federal Agencies 🏛️")
st.link_button("Readability Metrics", "https://pypi.org/project/py-readability-metrics/", type="secondary", icon="📚",
               disabled=False, use_container_width=False)


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


def fetch_aggregate_agency_metrics(slugs):
    agency_metrics = [json.loads(s) if s is not None else None for s in r.mget(slugs)]
    extracted_data = {
        "Word Count": [],
        "Average Flesch-Kincaid": [],
        "Average Flesch Reading Ease": [],
        "Average SMOG": [],
    }

    for agency in agency_metrics:
        if agency is not None:
            extracted_data["Word Count"].append(agency.get("total_word_count"))
            extracted_data["Average Flesch-Kincaid"].append(agency.get("average_flesch_kincaid"))
            extracted_data["Average Flesch Reading Ease"].append(agency.get("average_flesch_reading_ease"))
            extracted_data["Average SMOG"].append(agency.get("average_smog"))
        else:
            extracted_data["Word Count"].append(None)
            extracted_data["Average Flesch-Kincaid"].append(None)
            extracted_data["Average Flesch Reading Ease"].append(None)
            extracted_data["Average SMOG"].append(None)

    return extracted_data


def fetch_metrics_for_agency(slug):
    agency_metrics = r.get(slug)
    return json.loads(agency_metrics) if agency_metrics is not None else None


with st.spinner("Fetching Agencies..."):
    agencies_data = fetch_agencies()

if agencies_data:
    agencies = pd.DataFrame(agencies_data["agencies"]).set_index("sortable_name")

    with st.spinner("Fetching Agency metrics..."):
        slugs = agencies["slug"].tolist()
        agency_metrics = fetch_aggregate_agency_metrics(slugs)
        for key, values in agency_metrics.items():
            agencies[key] = values

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Agencies", len(agencies))
    with col2:
        st.metric("Word Count", round(agencies["Word Count"].mean(), 2))
    with col3:
        st.metric(
            "Average Flesch-Kincaid",
            round(agencies["Average Flesch-Kincaid"].mean(), 2),
            help="A higher Flesch-Kincaid score indicates that the text is easier to read."
        )
    with col4:
        st.metric(
            "Average Flesch Reading Ease",
            round(agencies["Average Flesch Reading Ease"].mean(), 2),
            help="A higher Flesch readability score indicates that a text is easier to read."
        )
    with col5:
        st.metric(
            "Average SMOG",
            round(agencies["Average SMOG"].mean(), 2),
            help="A higher SMOG score indicates worse readability.",
        )

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
                color=alt.Color("Name:N", legend=None),
                tooltip=["Name", "Word Count"]
            ).properties(width=1000, height=1000)
            st.altair_chart(chart, use_container_width=False)

    st.divider()
    st.header("Agency Overview")
    selected_agency = st.selectbox(
        "Agency",
        agencies_data["agencies"],
        index=None,
        format_func=lambda a: a["name"],
        placeholder="Select Agency",
    )

    if selected_agency:
        st.subheader("CFR References")
        reference_data = fetch_metrics_for_agency(selected_agency["slug"])["references"]
        if reference_data:
            references = pd.DataFrame(reference_data)
            # Expand the dictionary
            reference = references["reference"].apply(pd.Series)
            references = pd.concat([reference, references.drop(columns=["reference"])], axis=1)

            references.columns = [col.replace("_", " ").title() for col in references.columns]

            st.dataframe(references, hide_index=True, use_container_width=True)

else:
    st.error("Failed to fetch Agencies. Try again later.")

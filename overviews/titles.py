import natsort
import pandas as pd
import streamlit as st

from utils import ecfr

st.set_page_config(layout="wide")


@st.cache_data
def fetch_titles():
    return ecfr.fetch_titles()


st.title("Code of Federal Regulations Titles")

with st.spinner("Fetching Titles..."):
    titles_data = fetch_titles()

if titles_data:
    df = pd.DataFrame(titles_data).rename(columns={
        "number": "Number",
        "name": "Name",
        "latest_amended_on": "Last Amended",
        "latest_issue_date": "Last Issued",
        "up_to_date_as_of": "Up to Date As Of",
        "reserved": "Reserved"
    })

    df = df.drop(columns=["Reserved"])

    for col in ["Last Amended", "Last Issued", "Up to Date As Of"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    st.dataframe(df.set_index("Number"), use_container_width=True)

    st.subheader("Title Content")

    titles_dict = {t["number"]: t for t in titles_data}
    selected_title = st.selectbox(
        "Select a CFR Title:",
        list(titles_dict.keys()),
        format_func=lambda t: f"{t}: {titles_dict[t]["name"]}",
    )
    st.link_button(
        "View in CFR",
        f"https://www.ecfr.gov/current/title-{selected_title}",
        icon="📕",
    )

    with st.spinner("Fetching Title Content Versions..."):
        versions_data = ecfr.fetch_versions_for_title(selected_title)

    meta = versions_data["meta"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Content Versions", value=meta["result_count"])
    with col2:
        st.metric(label="Latest Amendment Date", value=meta["latest_amendment_date"])
    with col3:
        st.metric(label="Latest Issue Date", value=meta["latest_issue_date"])

    content_versions = pd.DataFrame(versions_data["content_versions"]).drop(columns=["date", "title"])

    if not content_versions.empty:
        content_versions["amendment_date"] = pd.to_datetime(content_versions["amendment_date"],
                                                            errors="coerce").dt.strftime("%Y-%m-%d")
        content_versions["issue_date"] = pd.to_datetime(content_versions["issue_date"], errors="coerce").dt.strftime(
            "%Y-%m-%d")

        content_versions = content_versions.sort_values(by="identifier", key=natsort.natsort_keygen())
        content_versions = content_versions.rename(columns={"identifier": "Identifier"})
        content_versions = content_versions.set_index("Identifier")

        content_versions["substantive"] = content_versions["substantive"].replace({True: "✅ Yes", False: "❌ No"})
        content_versions["removed"] = content_versions["removed"].replace({True: "✅ Yes", False: "❌ No"})
        content_versions["type"] = content_versions["type"].replace({"section": "Section", "appendix": "Appendix"})

        content_versions = content_versions.rename(columns={
            "amendment_date": "Amendment Date",
            "issue_date": "Issue Date",
            "name": "Name",
            "part": "Part",
            "substantive": "Substantive",
            "removed": "Removed",
            "subpart": "Subpart",
            "type": "Type",
        })

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Sections", value=(content_versions["Type"].eq("Section").sum()))
        with col2:
            st.metric(label="Appendices", value=(content_versions["Type"].eq("Appendix").sum()))

        st.dataframe(
            content_versions,
            use_container_width=True,
            hide_index=False,
        )
    else:
        st.warning("No content versions available for the selected Title.")

else:
    st.error("Failed to fetch Titles. Try again later.")

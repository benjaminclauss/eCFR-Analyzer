import pandas as pd
import streamlit as st

from datetime import datetime
from utils import ecfr

st.set_page_config(layout="wide")

st.title("Corrections 📝")


@st.cache_data
def fetch_corrections(date=None, title=None):
    return ecfr.fetch_corrections(date=date, title=title)


@st.cache_data
def fetch_titles():
    return ecfr.fetch_titles()


def graph_corrections_over_time(corrections):
    if len(corrections) == 0:
        return

    corrections["Error Corrected"] = pd.to_datetime(corrections["Error Corrected"], errors="coerce")

    corrections_by_date = (
        corrections.dropna(subset=["Error Corrected"])
        .groupby(corrections["Error Corrected"].dt.to_period("M"))
        .size()
        .rename("Correction Count")
        .reset_index()
    )

    corrections_by_date["Error Corrected"] = corrections_by_date["Error Corrected"].astype(str)

    full_date_range = pd.date_range(
        start=corrections["Error Corrected"].min(),
        end=datetime.today().strftime("%Y-%m-%d"),
        freq="ME"
    )

    full_range_df = pd.DataFrame(full_date_range, columns=["Error Corrected"])
    full_range_df["Error Corrected"] = full_range_df["Error Corrected"].dt.strftime("%Y-%m")
    full_range_df["Correction Count"] = 0

    corrections_by_date = full_range_df.merge(corrections_by_date, on="Error Corrected", how="left").fillna(0)

    corrections_by_date["Correction Count"] = corrections_by_date["Correction Count_y"].astype(int)
    corrections_by_date = corrections_by_date[["Error Corrected", "Correction Count"]]

    st.line_chart(corrections_by_date.set_index("Error Corrected"))


titles_data = fetch_titles()
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input(
        "Date",
        None,
        help="Restrict results to eCFR corrections that occurred on or before the specified date and that were corrected on or after the specified date.",
    )

with col2:
    if titles_data:
        titles_dict = {t["number"]: t for t in titles_data}
        selected_title = st.selectbox(
            "Title",
            list(titles_dict.keys()),
            index=None,
            format_func=lambda t: f"{t}: {titles_dict[t]['name']}",
            help="Restricts results to the given Title",
            placeholder="Select a Title",
        )
    else:
        st.error("Failed to fetch Titles", icon="🚨")

with st.spinner("Fetching Corrections..."):
    corrections_data = fetch_corrections(
        date=str(selected_date) if selected_date is not None else None,
        title=selected_title,
    )

if corrections_data and len(corrections_data["ecfr_corrections"]) > 0:
    corrections = pd.DataFrame(corrections_data["ecfr_corrections"])

    corrections = corrections.rename(columns={
        "id": "ID",
        "cfr_references": "CFR References",
        "corrective_action": "Corrective Action",
        "error_corrected": "Error Corrected",
        "error_occurred": "Error Occurred",
        "fr_citation": "FR Citation",
        "position": "Position",
        "display_in_toc": "Display in TOC",
        "title": "Title",
        "year": "Year",
        "last_modified": "Last Modified",
    })

    order = [
        "ID", "CFR References", "Corrective Action", "Error Occurred", "Error Corrected",
        "Year", "FR Citation", "Title", "Position", "Display in TOC", "Last Modified"
    ]
    corrections = corrections[[col for col in order if col in corrections.columns]]
    corrections = corrections.drop(columns=["CFR References"])

    for col in ["Error Corrected", "Error Occurred", "Last Modified"]:
        corrections[col] = pd.to_datetime(corrections[col], errors="coerce").dt.date
    corrections["Year"] = corrections["Year"].astype(str)

    st.metric("Total Corrections", len(corrections))
    st.dataframe(corrections.set_index("ID"), use_container_width=True)

    st.subheader("Corrections over Time")
    graph_corrections_over_time(corrections)

elif len(corrections_data["ecfr_corrections"]) == 0:
    st.metric("Total Corrections", 0)
else:
    st.error("Failed to fetch Corrections. Try again later.")

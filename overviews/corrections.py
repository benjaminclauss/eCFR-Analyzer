import pandas as pd
import streamlit as st

from utils import ecfr

st.set_page_config(layout="wide")

st.title("Corrections")


@st.cache_data
def fetch_corrections(date=None):
    return ecfr.fetch_corrections(date=date)


date = st.date_input(
    "Date",
    None,
    help="Restrict results to eCFR corrections that occurred on or before the specified date and that were corrected on or after the specified date.",
)

with st.spinner("Fetching Corrections..."):
    corrections_data = fetch_corrections(date=str(date) if date is not None else None)

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
        "ID",
        "CFR References",
        "Corrective Action",
        "Error Occurred",
        "Error Corrected",
        "Year",
        "FR Citation",
        "Position",
        "Display in TOC",
        "Title",
        "Last Modified",
    ]
    corrections = corrections[[col for col in order if col in corrections.columns]]

    for col in ["Error Corrected", "Error Occurred", "Last Modified"]:
        corrections[col] = pd.to_datetime(corrections[col], errors="coerce").dt.strftime("%Y-%m-%d")
    corrections["Year"] = corrections["Year"].astype(str)

    st.metric("Total Corrections", len(corrections))
    st.dataframe(corrections.set_index("ID"), use_container_width=True)
elif len(corrections_data["ecfr_corrections"]) == 0:
    st.metric("Total Corrections", 0)
else:
    st.error("Failed to fetch Corrections. Try again later.")

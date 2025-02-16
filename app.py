import streamlit as st

# TODO: Remove if unused.
# st.sidebar.header("About")

pg = st.navigation(
    {
        "Home": [
            (st.Page("home.py", title="Home", default=True, icon=":material/home:")),
        ],
        "Overview": [
            (st.Page("overviews/agencies.py", title="Agencies", icon=":material/account_balance:")),
            (st.Page("overviews/titles.py", title="Titles", icon=":material/book:"))
        ],
        "Metrics": [
            (st.Page("metrics/agency_metrics.py", title="Agency Metrics"))
        ],
    }
)

pg.run()


import streamlit as st

pg = st.navigation(
    {
        "Home": [
            (st.Page("home/home.py", title="Home", default=True, icon=":material/home:")),
        ],
        "Overview": [
            (st.Page("overviews/agencies.py", title="Agencies", icon=":material/account_balance:")),
            (st.Page("overviews/titles.py", title="Titles", icon=":material/book:")),
        ],
    }
)

pg.run()

import streamlit as st

st.title("Welcome to the eCFR Analyzer 📜")
st.write("The goal of this project is to create a simple website to analyze Federal Regulations.")

st.markdown("""
Per the [eCFR](https://www.ecfr.gov/):

> The *Code of Federal Regulations* (CFR) is the official legal print publication containing the codification of the 
> general and permanent rules published in the *Federal Register* by the departments and agencies of the Federal 
> Government. The Electronic Code of Federal Regulations (eCFR) is a continuously updated online version of the CFR. 
> It is not an official legal edition of the CFR.
> 
> [Learn more](https://www.ecfr.gov/reader-aids/understanding-the-ecfr/what-is-the-ecfr) about the eCFR, its status, 
> and the editorial process.
""")

st.subheader("Need a Break? Have Some Fun! 🎉")
col1, col2 = st.columns(2)
with col1:
    if st.button("Have a party! 🎈"):
        st.balloons()
with col2:
    if st.button("Let it snow! ❄️"):
        st.snow()


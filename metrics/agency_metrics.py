import streamlit as st
import requests
import pandas as pd
import xml.etree.ElementTree as ET
# TODO: Presumably, we can consolidate usage of XML libraries.
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

AGENCIES_API_URL = "https://www.ecfr.gov/api/admin/v1/agencies.json"

@st.cache_data
def fetch_agencies():
    """Fetches the list of agencies and their CFR references."""
    response = requests.get(AGENCIES_API_URL)
    if response.status_code == 200:
        return response.json().get("agencies", [])
    return None


TITLE_API_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"

@st.cache_data
def fetch_titles():
    """Fetches metadata for all titles, including the latest issue date."""
    response = requests.get(TITLE_API_URL)
    if response.status_code == 200:
        return {str(t["number"]): t["latest_issue_date"] for t in response.json().get("titles", [])}
    return {}


def format_cfr_reference(ref):
    """Formats CFR references consistently for display."""
    text = f"Title {ref['title']}"

    if ref.get("subtitle"):
        text += f", Subtitle {ref.get('subtitle')}"
    if ref.get("chapter"):
        text += f", Chapter {ref.get('chapter')}"
    if ref.get("subchapter"):
        text += f", Subchapter {ref.get('subchapter')}"
    if ref.get("part"):
        text += f", Part {ref.get('part')}"

    return text


ANCESTRY_API_URL = "https://www.ecfr.gov/api/versioner/v1/ancestry/{date}/title-{title}.json"
CFR_TEXT_API_URL = "https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"

@st.cache_data
def fetch_ancestry(date, title, subtitle=None, chapter=None, subchapter=None, part=None, section=None):
    """Fetches the full ancestry for a given CFR reference."""
    url = ANCESTRY_API_URL.format(date=date, title=title)
    params = {}

    if subtitle: params["subtitle"] = subtitle
    if chapter: params["chapter"] = chapter
    if subchapter: params["subchapter"] = subchapter
    if part: params["part"] = part
    if section: params["section"] = section

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data
def fetch_cfr_text(date, title):
    """Fetches the full CFR XML text for a given title and date."""
    url = CFR_TEXT_API_URL.format(date=date, title=title)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None


def extract_section_from_xml(xml_content, ancestry_data):
    """Parses CFR XML and extracts only the requested section using ancestry data."""

    root = ET.fromstring(xml_content)

    # Extract identifiers from ancestry data
    hierarchy = {item["type"]: item["identifier"] for item in ancestry_data}

    # Start at the Title Level
    title_elem = root.find(f".//DIV1[@TYPE='TITLE'][@N='{hierarchy.get('title')}']")
    if not title_elem:
        return f"Title {hierarchy.get('title')} not found."

    # Check Subtitle (if applicable)
    if "subtitle" in hierarchy:
        subtitle_elem = title_elem.find(f".//DIV2[@TYPE='SUBTITLE'][@N='{hierarchy['subtitle']}']")
        if not subtitle_elem:
            return f"Subtitle {hierarchy['subtitle']} not found."
    else:
        subtitle_elem = title_elem

    # Check Chapter (if applicable)
    if "chapter" in hierarchy:
        chapter_elem = subtitle_elem.find(f".//DIV3[@TYPE='CHAPTER'][@N='{hierarchy['chapter']}']")
        if not chapter_elem:
            return f"Chapter {hierarchy['chapter']} not found."
    else:
        chapter_elem = subtitle_elem

    # Check Subchapter (if applicable)
    if "subchapter" in hierarchy:
        subchapter_elem = chapter_elem.find(f".//DIV4[@TYPE='SUBCHAP'][@N='{hierarchy['subchapter']}']")
        if not subchapter_elem:
            return f"Subchapter {hierarchy['subchapter']} not found."
    else:
        subchapter_elem = chapter_elem

    # Check Part (if applicable)
    if "part" in hierarchy:
        part_elem = subchapter_elem.find(f".//DIV5[@TYPE='PART'][@N='{hierarchy['part']}']")
        if not part_elem:
            return f"Part {hierarchy['part']} not found."
    else:
        part_elem = subchapter_elem

    # Check Section (Final Level)
    if "section" in hierarchy:
        section_elem = part_elem.find(f".//DIV8[@TYPE='SECTION'][@N='{hierarchy['section']}']")
        return section_elem if section_elem else f"Section {hierarchy['section']} not found."

    return part_elem


def get_cfr_section(date, title, subtitle=None, chapter=None, subchapter=None, part=None, section=None):
    """Retrieves and extracts a specific CFR section using Ancestry API and Full XML data."""

    ancestry_data = fetch_ancestry(date, title, subtitle, chapter, subchapter, part, section)
    if not ancestry_data:
        return "Failed to fetch ancestry data."

    cfr_text = fetch_cfr_text(date, title)
    if not cfr_text:
        return "Failed to fetch CFR text."

    return extract_section_from_xml(cfr_text, ancestry_data['ancestors'])


st.title("Agency Metrics")

agencies_data = fetch_agencies()
title_metadata = fetch_titles()

if agencies_data:
    df = pd.DataFrame(agencies_data).rename(columns={"name": "Agency Name"}).sort_values(by="sortable_name")

    selected_agency = st.selectbox("Agency", df["Agency Name"])

    agency_info = df[df["Agency Name"] == selected_agency].iloc[0]
    cfr_references = agency_info.get("cfr_references", [])

    st.subheader(f"CFR References")

    if cfr_references:
        cfr_df = pd.DataFrame(cfr_references)

        for col in ["title", "subtitle", "chapter", "subchapter", "part"]:
            if col not in cfr_df.columns:
                cfr_df[col] = None

        cfr_df = cfr_df[["title", "subtitle", "chapter", "subchapter", "part"]]
        cfr_df = cfr_df.rename(columns={
            "title": "Title",
            "subtitle": "Subtitle",
            "chapter": "Chapter",
            "subchapter": "Subchapter",
            "part": "Part"
        })

        st.dataframe(cfr_df.set_index("Title"), use_container_width=True)

        selected_reference = st.selectbox(
            "Select a CFR Reference",
            cfr_references,
            index=None,
            format_func=format_cfr_reference
        )

        if selected_reference:
            title_number = str(selected_reference["title"])
            subtitle = selected_reference.get("subtitle", None)
            chapter = selected_reference.get("chapter", None)
            subchapter = selected_reference.get("subchapter", None)
            part = selected_reference.get("part", None)

            # Get latest issue date for that Title
            latest_issue_date = title_metadata.get(title_number, None)

            st.subheader(f"Latest Issue Date for Title {title_number}: **{latest_issue_date}**")

            # Fetch CFR text if we have a valid issue date
            if latest_issue_date is not None:
                reference_content = get_cfr_section(latest_issue_date, title_number, subtitle=subtitle, chapter=chapter,
                                                    subchapter=subchapter, part=part, section=None)

                if reference_content:
                    st.subheader(format_cfr_reference(selected_reference))

                    # Pass it to BeautifulSoup for parsing
                    soup = BeautifulSoup(ET.tostring(reference_content, encoding="unicode", method="xml"), "xml")
                    # Extract all <P> elements and get the text content as a list
                    p_texts = [p.get_text(strip=True) for p in soup.find_all("P")]

                    st.text("This CFR section has the following word count excluding section headers (e.g., Chapter, Part):")
                    st.text(sum(len(text.split()) for text in p_texts))

                    st.text_area("CFR Content", ET.tostring(reference_content, encoding="unicode", method="text"), height=400)
                else:
                    st.warning(f"Failed to fetch CFR text for Title {title_number} on {latest_issue_date}.")
    else:
        st.warning(f"No CFR references found for {selected_agency}.")
else:
    st.error("Failed to fetch agencies. Try again later.")
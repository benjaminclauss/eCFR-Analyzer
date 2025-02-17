import streamlit as st
import pandas as pd

from bs4 import BeautifulSoup
from utils import ecfr
import xml.etree.ElementTree as ET

st.set_page_config(layout="wide")


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


def calculate_word_count_for_reference(date, reference):
    title_number = reference["title"]
    subtitle = reference.get("subtitle", None)
    chapter = reference.get("chapter", None)
    subchapter = reference.get("subchapter", None)
    part = reference.get("part", None)

    # TODO: Remove if unneeded. When I was initially playing with this, the API returned all XML despite specifying a subset.
    title_xml = ecfr.fetch_xml_for_title(date, title_number, subtitle=subtitle, chapter=chapter, subchapter=subchapter,
                                         part=part)
    ancestry_data = ecfr.fetch_ancestry_for_title(date, title_number, subtitle, chapter, subchapter, part, None)
    reference_content = extract_section_from_xml(title_xml, ancestry_data['ancestors'])

    soup = BeautifulSoup(ET.tostring(reference_content, encoding="unicode", method="xml"), "xml")
    p_texts = [p.get_text(strip=True) for p in soup.find_all("P")]
    return sum(len(text.split()) for text in p_texts)


titles_data = ecfr.fetch_titles()


def get_word_count_for_cfr_references(references):
    total = 0
    for reference in references:
        latest_issue_date = {t["number"]: t["latest_issue_date"] for t in titles_data}[reference["title"]]
        total += calculate_word_count_for_reference(latest_issue_date, reference)
    return total


st.title("Agencies")

agencies_data = ecfr.fetch_agencies()

if titles_data and agencies_data:
    agencies = pd.DataFrame(agencies_data).set_index("sortable_name").head(n=5)
    st.metric("Total Agencies", len(agencies))
    agencies['Word Count'] = agencies['cfr_references'].apply(get_word_count_for_cfr_references)
    overview = agencies.drop(columns=["display_name", "slug", "cfr_references", "children"])
    overview = overview.rename(columns={"name": "Name", "short_name": "Short Name"})
    st.dataframe(overview, hide_index=True, use_container_width=True)
else:
    st.error("Failed to fetch Agencies. Try again later.")

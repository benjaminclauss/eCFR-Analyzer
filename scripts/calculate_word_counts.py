import logging
import os

import redis
import threading
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from utils import ecfr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [Thread %(threadName)s] - %(message)s",
)

MAX_CONCURRENT_CALCULATIONS = 1

r = redis.Redis(
    host=os.getenv("REDIS_URL"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True
)


def calculate_word_counts():
    agencies_data = ecfr.fetch_agencies()
    if not agencies_data:
        logging.error("No Agency data found.")
        return

    logging.info("Starting word count calculation...")
    logging.info(f"Total agencies to process: {len(agencies_data)}")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CALCULATIONS) as executor:
        results = list(executor.map(process_agency, agencies_data))  # Ensure results are fully consumed

    logging.info("Word count calculation completed.")
    return dict(results)


semaphore = threading.Semaphore(MAX_CONCURRENT_CALCULATIONS)


def process_agency(agency):
    with semaphore:  # Ensures only `MAX_CONCURRENT_CALCULATIONS` run at a time
        logging.info(f"🚀 Starting processing: {agency['name']}")
        agency_word_count = get_word_count_for_cfr_references(agency["cfr_references"])
        logging.info(
            f"✅ Completed: {agency['name']} - Word count: {agency_word_count}")
        r.set(agency["slug"], agency_word_count)
        return agency["slug"], agency_word_count


titles_data = ecfr.fetch_titles()


def get_word_count_for_cfr_references(references):
    total = 0
    for reference in references:
        latest_issue_date = {t["number"]: t["latest_issue_date"] for t in titles_data}[reference["title"]]
        total += calculate_word_count_for_reference(latest_issue_date, reference)
    return total


def calculate_word_count_for_reference(date, reference):
    title_number = reference["title"]
    subtitle = reference.get("subtitle", None)
    chapter = reference.get("chapter", None)
    subchapter = reference.get("subchapter", None)
    part = reference.get("part", None)

    title_xml = ecfr.fetch_xml_for_title(date, title_number, subtitle=subtitle, chapter=chapter, subchapter=subchapter,
                                         part=part)

    if part is not None:
        reference_xml = title_xml
    else:
        ancestry_data = ecfr.fetch_ancestry_for_title(date, title_number, subtitle, chapter, subchapter, part, None)
        extracted_reference = extract_from_xml(title_xml, ancestry_data['ancestors'])
        reference_xml = ET.tostring(extracted_reference, encoding="unicode", method="xml")

    soup = BeautifulSoup(reference_xml, "xml")
    p_texts = [p.get_text(strip=True) for p in soup.find_all("P")]
    return sum(len(text.split()) for text in p_texts)


def extract_from_xml(xml_content, ancestry_data):
    """Parses CFR XML and extracts only the requested section using ancestry data."""
    root = ET.fromstring(xml_content)

    # Extract identifiers from ancestry data
    hierarchy = {item["type"]: item["identifier"] for item in ancestry_data}

    # Start at the Title level
    title_elem = root.find(f".//DIV1[@TYPE='TITLE'][@N='{hierarchy.get('title')}']")
    if title_elem is None:
        return None

    # Check Subtitle (if applicable)
    if "subtitle" in hierarchy:
        subtitle_elem = title_elem.find(f".//DIV2[@TYPE='SUBTITLE'][@N='{hierarchy['subtitle']}']")
        if subtitle_elem is None:
            return None
    else:
        subtitle_elem = title_elem

    # Check Chapter (if applicable)
    if "chapter" in hierarchy:
        chapter_elem = subtitle_elem.find(f".//DIV3[@TYPE='CHAPTER'][@N='{hierarchy['chapter']}']")
        if chapter_elem is None:
            return None
    else:
        chapter_elem = subtitle_elem

    # Check Subchapter (if applicable)
    if "subchapter" in hierarchy:
        subchapter_elem = chapter_elem.find(f".//DIV4[@TYPE='SUBCHAP'][@N='{hierarchy['subchapter']}']")
        if subchapter_elem is None:
            return None
    else:
        subchapter_elem = chapter_elem

    # Check Part (if applicable)
    if "part" in hierarchy:
        part_elem = subchapter_elem.find(f".//DIV5[@TYPE='PART'][@N='{hierarchy['part']}']")
        if part_elem is None:
            return None
    else:
        part_elem = subchapter_elem

    # Check Section (final level)
    if "section" in hierarchy:
        section_elem = part_elem.find(f".//DIV8[@TYPE='SECTION'][@N='{hierarchy['section']}']")
        return section_elem if section_elem is not None else None

    return part_elem


if __name__ == "__main__":
    calculate_word_counts()

import logging
import requests


def fetch_agencies():
    try:
        response = requests.get("https://www.ecfr.gov/api/admin/v1/agencies.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f"Failed to fetch Agencies: {error}")
        return None


def fetch_corrections(date=None, title=None):
    url = "https://www.ecfr.gov/api/admin/v1/corrections.json"

    params = {}
    if date is not None:
        params["date"] = date
    if title is not None:
        params["title"] = str(title)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f"Failed to fetch Corrections: {error}")
        return None


def fetch_ancestry_for_title(date, title, subtitle=None, chapter=None, subchapter=None, part=None, section=None):
    """Fetches the full ancestry for a given CFR reference."""
    url = f"https://www.ecfr.gov/api/versioner/v1/ancestry/{date}/title-{title}.json"
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


def fetch_xml_for_title(date, title, subtitle=None, chapter=None, subchapter=None, part=None):
    """
    Source XML for a title or subset of a title.

    Requests can be for entire titles or part level and below.
    - Downloadable XML document is returned for title requests.
    - Processed XML is returned if part, subpart, section, or appendix is requested.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"

    params = {}
    if subtitle:
        params["subtitle"] = subtitle
    if chapter:
        params["chapter"] = chapter
    if subchapter:
        params["subchapter"] = subchapter
    if part:
        params["part"] = part

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as error:
        logging.error(f"Failed to fetch XML for title {title} on {date}: {error}")
        return None


def fetch_titles():
    response = requests.get("https://www.ecfr.gov/api/versioner/v1/titles.json")
    if response.status_code == 200:
        return response.json().get("titles", [])
    else:
        return None


def fetch_versions_for_title(title, gte=None, lte=None, on=None):
    params = {}
    if on is not None:
        params["issue_date[on]"] = on
    else:
        if gte is not None:
            params["issue_date[gte]"] = gte
        if lte is not None:
            params["issue_date[lte]"] = lte

    try:
        response = requests.get(f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title}.json", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        logging.error(f"Failed to fetch Content Versions for title {title}: {error}")
        return None

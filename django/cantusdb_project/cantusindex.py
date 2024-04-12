"""
Functions for fetching data from Cantus Index's APIs
"""

import requests
from typing import Optional
from requests.exceptions import ConnectTimeout
from codecs import decode
import ujson

CI_DOMAIN: str = "https://cantusindex.uwaterloo.ca"
DEFAULT_TIMEOUT = 2  # maximum time to wait for a response, in seconds


def get_json_from_ci_api(path: str, timeout: Optional[int] = None) -> dict:
    """Request data from a Cantus Index API at a specified path, decode
    the json in the response, and return the data as a dictionary

    Args:
        path (str): The path where the API is found on Cantus Index's site.
        Must begin with a "/".

    Returns:
        dict: Json from Cantus Index, parsed as a Python dictionary
    """
    if not path.startswith("/"):
        raise ValueError('path must begin with "/"')

    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    url: str = f"{CI_DOMAIN}{path}"
    try:
        request = requests.get(url, timeout=timeout)
    except ConnectTimeout:
        return {}

    # ujson.loads requires a string, while request.content is of type bytes.
    # decode converts to string
    decoded_content: str = decode(
        request.content,
        encoding="utf-8-sig",
    )
    json_content: dict = ujson.loads(decoded_content)

    return json_content


def get_expected_fulltext(cantus_id: str) -> str:
    """Given a Cantus ID, get the canonical fulltext for
    that Cantus ID from a Cantus Index API and return it.

    Args:
        cantus_id (str): The Cantus ID.

    Returns:
        str: The canonical/expected fulltext for the Cantus ID.
    """
    path = f"/json-cid/{cantus_id}"
    data = get_json_from_ci_api(path)
    expected_fulltext = data["info"]["field_full_text"]

    return expected_fulltext

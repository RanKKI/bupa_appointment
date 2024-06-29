import time
import urllib.parse
from typing import List

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from bupa.logger import logger

header = Headers(headers=True)
session = requests.Session()

HEADERS = {
    **header.generate(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


def extract_form_data(root: BeautifulSoup, keep: List[str] = None, extra: dict = None):
    form = root.find("form")
    data = {}
    for field in form.find_all("input"):
        key = field.get("name")
        if not key:
            continue
        value = field.get("value")
        if not keep or key in keep:
            data[key] = value
    if extra:
        data.update(extra)
    return data


def make_request(url, method="GET", data=None, headers=None, wait=1):
    time.sleep(wait)
    logger.debug("Making request [%s] to %s", method, url)
    if data:
        logger.debug("Request data: %s", data)

    _header = HEADERS.copy()
    _header.update(headers or {})

    html = session.request(method, url, data=data, headers=_header)

    logger.debug("Response url: [%s] %s", html.status_code, html.url)

    _url = urllib.parse.urlparse(html.url)
    _endpoint = _url.path.split("/")[-1]

    if html.status_code != 200 or _endpoint == "Error.aspx":
        raise Exception(f"Failed to make request to {url}")

    logger.debug("-" * 80)
    return BeautifulSoup(html.text, "html.parser"), html


from hashlib import sha256
from http.cookiejar import MozillaCookieJar
from json import loads
from lxml.etree import HTML
from os import path as ospath
from re import findall, match, search
from requests import Session, post, get
from requests.adapters import HTTPAdapter
from time import sleep
from urllib.parse import parse_qs, urlparse
from urllib3.util.retry import Retry
from uuid import uuid4
from base64 import b64decode



def direct_link_generator(link):
    """direct links generator"""
    domain = urlparse(link).hostname
    if not domain:
        return "ERROR: Invalid URL"

    elif "krakenfiles.com" in domain:
        return krakenfiles(link)


def krakenfiles(url):
    with Session() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            return f"ERROR: {e.__class__.__name__}"
        html = HTML(_res.text)
        if post_url := html.xpath('//form[@id="dl-form"]/@action'):
            post_url = f"https://krakenfiles.com{post_url[0]}"
        else:
            return "ERROR: Unable to find post link."
        if token := html.xpath('//input[@id="dl-token"]/@value'):
            data = {"token": token[0]}
        else:
            return "ERROR: Unable to find token for post."
        try:
            _json = session.post(post_url, data=data).json()
        except Exception as e:
            return f"ERROR: {e.__class__.__name__} While send post request"

    if _json["status"] != "ok":
        return "ERROR: Unable to find download after post request"
    return _json["url"]


# print(direct_link_generator('https://krakenfiles.com/view/tbWE0VDh8y/file.html'))


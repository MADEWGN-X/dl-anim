
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
    elif "mediafire.com" in domain:
        return mediafire(link)


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

def mediafire(url, session=None):
    if "/folder/" in url:
        return mediafireFolder(url)
    if final_link := findall(
        r"https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+", url
    ):
        return final_link[0]
    if session is None:
        session = Session()
        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    try:
        html = HTML(session.get(url).text)
    except Exception as e:
        session.close()
        return f"ERROR: {e.__class__.__name__}"
    if error := html.xpath('//p[@class="notranslate"]/text()'):
        session.close()
        return f"ERROR: {error[0]}"
    if not (final_link := html.xpath("//a[@id='downloadButton']/@href")):
        session.close()
        return "ERROR: No links found in this page Try Again"
    if final_link[0].startswith("//"):
        return mediafire(f"https://{final_link[0][2:]}", session)
    session.close()
    return final_link[0]

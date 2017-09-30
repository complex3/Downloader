
"""Download all files of a certiain file extension from a webpage"""


import re
import urlparse
import os
import urllib
import requests
from lxml import html
from configs import REQ_CRED, LOGIN_URL, LOGIN_FORM_INDEX, USER_FIELD_NAME, \
    USERNAME, PASS_FIELD_NAME, PASSWORD, LOGOUT_URL, TARGET_URL, TARGET_FOLDER, \
    MAX_FILES, EXTS, REQ_CONF


def login(session):
    # TODO: check downloads with creds
    """Login to the website"""
    response = session.get(LOGIN_URL)
    response.raise_for_status()
    login_form = html.fromstring(response.content).forms[login_form_index]
    payload = dict(login_form.fields)
    payload[user_field_name] = USERNAME
    payload[pass_field_name] = PASSWORD
    response = session.post(LOGIN_URL, payload)


def url_enc_non_ascii(b):
    """iri_to_uri auxiliary function"""
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)


def iri_to_uri(iri):
    """Converts an IRI to a URI"""
    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti == 1 else url_enc_non_ascii(
            part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


def file_ext(file_name):
    """returns the file extension"""
    return file_name.split('.')[-1]


def url_file_name(url):
    """returns the url's file name"""
    return url[url.rfind('/') + 1:]


def url_base(url):
    """returns the url's base url"""
    return url[:url.rfind('/')]


def download(session):
    """Download all files in that webpage"""
    file_count = 0
    os.chdir(TARGET_FOLDER)
    response = session.get(TARGET_URL)
    response.raise_for_status()
    page_html = html.fromstring(response.content)
    page_html.make_links_absolute(base_url=url_base(TARGET_URL))
    for (_, link_type, link_url, _) in page_html.iterlinks():
        if link_type == 'href' and file_ext(link_url) in EXTS:
            file_count = file_count + 1
            if file_count > MAX_FILES:
                break
            # TODO: generalize
            file_name = url_file_name(link_url).replace('%20', ' ')
            if not REQ_CONF or raw_input('Download ' + file_name + ' ? (y/n)') == 'y':
                # print 'Downloading ' + file_name + '...'
                urllib.urlretrieve(iri_to_uri(link_url), file_name)


def logout(session):
    """Logout from the website"""
    response = session.get(LOGOUT_URL)
    response.raise_for_status()


SESSION = requests.session()
if REQ_CRED:
    login(SESSION)
download(SESSION)
if REQ_CRED:
    logout(SESSION)

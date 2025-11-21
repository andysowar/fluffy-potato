#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Knowyourmeme.com definitions scraper.
"""

import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

DEFAULT_TIMEOUT = 10


SEARCH_SIMILARITY_THRESHOLD = .4

HEADERS = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')}


def search_meme(text):
    """Return a meme name and url from a meme keywords.
    """
    r = requests.get(
        'http://knowyourmeme.com/search?q=%s' % text,
        headers=HEADERS,
        timeout=DEFAULT_TIMEOUT,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    memes_list = soup.find(class_='entry_list')
    if memes_list:
        meme_path = memes_list.find('a', href=True)['href']
        return meme_path.replace('-', ' '), 'https://knowyourmeme.com%s' % meme_path
    return None, None


def search(text):
    meme_name, url = search_meme(text)
    if not meme_name or SequenceMatcher(None, text, meme_name).ratio() < SEARCH_SIMILARITY_THRESHOLD:
        return None

    r = requests.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    def get_section_text(id_):
        header = soup.find('h2', {'id': id_})
        if header:
            content = []
            for sib in header.find_next_siblings():
                if sib.name == 'h2':
                    break
                content.append(sib.get_text(strip=True))
            return '\n\n'.join(content).strip()
        return None

    return {
        "title": soup.find("title").get_text(strip=True) if soup.find("title") else meme_name,
        "origin": get_section_text("origin"),
        "spread": get_section_text("spread"),
        "analysis": get_section_text("analysis"),
    }






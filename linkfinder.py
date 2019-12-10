# first attempt
# for a given address, gather all the <a> tags

import requests
import sys
import re
from urllib.parse import urlparse

debug = True

def find_links(url):
    res = requests.get(url)
    if res.status_code != requests.codes.ok:
        raise ValueError("Couldn't reach target\n")
    elif debug:
        print("Target reachable. Proceeding to process HTML response")

    html = res.text
    link_syntax = re.compile('<a.*href ?= ?\\"(\\S*)\\".*?>', re.IGNORECASE)

    links = re.findall(link_syntax, html)
    parsed = [urlparse(utemp) for utemp in links]
    return parsed

if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/Sine_wave'
    if len(sys.argv) == 2:
        url = sys.argv[1]

    links_found = find_links(url)
    for link in links_found:
        print(link)

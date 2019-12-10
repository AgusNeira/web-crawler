# first attempt
# for a given address, gather all the <a> tags

import requests
import sys
import re

debug = True

def find_links(url):
    res = requests.get(url)
    if res.status_code != requests.codes.ok:
        raise ValueError("Couldn't reach target\n")
    elif debug:
        print("Target reachable. Proceeding to process HTML response")

    html = res.text
    link_syntax = re.compile('<a.*href ?= ?\\"(\\S*)\\".*?>')

    links = re.findall(link_syntax, html)
    return links

if __name__ == '__main__':
    links_found = find_links('https://en.wikipedia.org/wiki/Sine_wave')
    for link in links_found:
        print(link)

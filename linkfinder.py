# first attempt
# for a given address, gather all the <a> tags

import requests
import sys
import re
from urllib.parse import urlparse

debug = True

def complete_url(url, base_url = None):
    if url.scheme == '':
        url = url._replace(scheme = 'http')

    if url.netloc == '':
        if base_url:
             url = url._replace(netloc = base_url.netloc)
        else:
            raise ValueError('domain required to connect')
    if url.path == '' and base_url:
        url = url._replace(path = base_url.path)

    return url

def find_links(url):
    nurl = url
    if isinstance(url, basestring):
        nurl = urlparse(url)

    res = requests.get(url.geturl())
    if res.status_code != requests.codes.ok:
        raise ValueError("Couldn't reach target\n")
    elif debug:
        print("Target reachable. Proceeding to process HTML response")

    html = res.text
    link_syntax = re.compile('<a.*href ?= ?[\\\'\\"]([^\\"\\\'\\s]*)[\\"\\\'].*?>', re.IGNORECASE)

    links = re.findall(link_syntax, html)
    result = {
            "local": [],
            "extern": []
    }
    for link in links:
        if link == '#': continue

        parsed = urlparse(link, scheme = 'http')
        complete_url(parsed, url)

        if parsed.netloc == url.netloc:
            result["local"].append(parsed)
        else:
            result["extern"].append(parsed)

    return result

if __name__ == '__main__':
    txturl = 'https://en.wikipedia.org/wiki/Sine_wave'
    if len(sys.argv) == 2:
        txturl = sys.argv[1]

    url = urlparse(txturl, scheme = 'http')
    try:
        url = complete_url(url)
    except ValueError:
        try:
            url = urlparse("//" + txturl)
            url = complete_url(url)
        except ValueError:
            print("Couldn't read URL properly")

    res = find_links(url)
    print('Analized %s'%url.geturl())
    print('Found %d local links and %d extern ones' % (len(res['local']), len(res['extern'])))
    print('Local links:')
    #if debug:
    #    print(res['local'])
    [print("%d: %s"%(index, lin.geturl())) for index, lin in enumerate(res['local'])]
    print('Extern links:')
    #if debug:
    #    print(res['extern'])
    [print("%d: %s"%(index, lin.geturl())) for index, lin in enumerate(res['extern'])]

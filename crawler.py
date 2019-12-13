# Crawler Cmd
# Handles the lookup of links inside web sites and
# the recordings to the domains database

# There are two main crawlers: the inner crawler and the outer crawler.
# The former gathers data from within one single domain, structuring a site tree.
# Whereas the latter focuses on the extern links, and tries to find relationships
# between different sites.

# Lastly, the 'crawl' command is a manual tool to crawl the web, capable of
# saving the analyzed sites to domains

import cmd, requests, re, json
from urllib.parse import urlparse
from load_config import load_config

config = load_config()

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


class Crawler(cmd.Cmd):
    
    def __init__(self, url):
        cmd.Cmd.__init__(self)
        self.prompt = '(Manual crawler) '
        print('You\'ve entered the manual crawler,')
        print('and chose to start from %s'%url)
        
        try:
            self.url = complete_url(urlparse(url, scheme = 'http')).geturl()
        except ValueError:
            try:
                self.url = complete_url(urlparse('//' + url, scheme = 'http')).geturl()
            except ValueError:
                print('Couldn\'t read URL properly. Exiting crawler')
                raise ValueError('Couldn\'t initialize manual crawler')

        res = requests.get(self.url)
        if res.status_code != requests.codes.ok:
            print('I\'m sorry, but the target you chose isn\'t reachable')
            raise ValueError('Couldn\'t initialize manual crawler')

        print('The target is reachable! You may now start crawling')
        print('Type \'help\' for details')
        
        self.links = {}

    def do_links(self, args):
        local, extern = True, True
        if args != '':
            if args == 'local':
                extern = False
            elif args == 'extern':
                local = False
            else:
                print('links: option not recognized. Type \'help links\' to see usage.')
            

        if self.url in self.links:
            print('There is data about the links of this URL already')
            yn = input('Do you want to analyze again? [y/N]: ').lower()
            if yn.lower() == 'y':
                del self.links[self.url]
                self.do_links(args)
            else:
                self.do_show('links')

        lurl = urlparse(self.url, scheme = 'http')
        
        res = requests.get(lurl.geturl())
        html = res.text
        link_syntax = re.compile('<a.*href ?= ?[\\\'\\"]([^\\"\\\'\\s]*)[\\"\\\'].*?>', re.IGNORECASE)

        links = re.findall(link_syntax, html)

        self.links[self.url] = {}
        if local: self.links[self.url]['local'] = []
        if extern: self.links[self.url]['extern'] = []

        for link in links:
            if link == '#': continue

            parsed = urlparse(link, scheme = 'http')
            complete_url(parsed, lurl)

            if parsed.netloc == lurl.netloc:
                if local: 
                    self.links[self.url]["local"].append(parsed)
            else:
                if extern:
                    self.links[self.url]["extern"].append(parsed)
    def help_links(self):
        print('it searches for all of the links in the current site')
        print('to visualize them, see the \'show\' command')
        print('usage:')
        print('\tlinks [local|extern]   --- searches for all links, only locals, or only extern ones')
    
    def __print_links_local(self):
        try:
            print('There are %d local links in this site'%len(self.links[self.url]['local']))
            if len(self.links[self.url]['local']) != 0:
                for index, local in enumerate(self.links[self.url]['local']):
                    print(local.geturl())
                    if index % config['page-size'] == config['page-size'] - 1:
                        continiu = input('Show next %d? (X or Q to stop): ' % config['page-size']).lower()
                        if continiu == 'q' or continiu == 'x':
                            break
        except KeyError:
            print('There are no links associated to this site')
    def __print_links_extern(self):
        try:
            llinks = len(self.links[self.url]['extern'])
            print('There are %d extern links in this site'%llinks)
            if llinks != 0:
                for index, extern in enumerate(self.links[self.url]['extern']):
                    print('%d: %s' % (index, extern.geturl()))
                    if index % config['page-size'] == config['page-size'] - 1:
                        continiu = input('Show next %d? (X or Q to stop): ' % config['page-size']).lower()
                        if continiu == 'q' or continiu == 'x':
                            break
        except KeyError:
            print('There are no links associated to this site')

    def do_show(self, args):
        if args == '':
            print('On this site:')
            if self.url not in self.links:
                print('\tLinks were not serched for')
                return
            if 'local' in self.links[self.url]:
                print('\t%d local links were found' % len(self.links[self.url]['local']))
            else:
                print('\tlocal links were not searched for')
            if 'extern' in self.links[self.url]:
                print('\t%d extern links were found' % len(self.links[self.url]['extern']))
            else:
                print('\textern links were not searched for')

            return

        largs = args.split(' ')
        if largs[0] == 'links':
            if self.url not in self.links:
                print('There are no links stored for this site')
            else:
                if len(largs) == 2:
                    if largs[1] == 'local':
                        self.__print_links_local()
                    elif largs[1] == 'extern':
                        self.__print_links_extern()
                    else:
                        print('show: sub-command not found. Type \'help show\' to see usage')
                        return
                else:
                    self.__print_links_local()
                    self.__print_links_extern()
        else:
            print('show: sub-command not found. Type \'help show\' to see usage')

    def help_show(self):
        print('prints information about the currente site')
        print('usage:')
        print('\tshow                       --- Shows a general overview of the site')
        print('\tshow links [local|extern]  --- Shows the links found on the site, if any. \n')
        print('More functionality is pending implementation')

    def do_delete(self, args):
        try:
            if args == 'links':
                yn = input('Do you really want to delete all the links of this site? [y|N]: ').lower()
                if yn == 'y':
                    del self.links[self.url]
            elif args == 'links local':
                yn = input('Do you really want to delete all local links of this site [y|N]: ').lower()
                if yn == 'y':
                    del self.links[self.url]['local']
            elif args == 'links extern':
                yn = input('Do you really want to delete all extern links of this site [y|N]: ').lower()
                if yn == 'y':
                    del self.links[self.url]['extern']
            if self.links.get(self.url, None) == {}:
                del self.links[self.url]
        except KeyError:
            print('Turns out there were no links to delete after all')


    def do_exit(self, args):
        return True

    def precmd(self, args):
        return args.lower()


if __name__ == '__main__':
    import sys

    crw = Crawler(sys.argv[1])
    crw.cmdloop()

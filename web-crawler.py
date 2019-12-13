import requests, sys, json, cmd
from urllib.parse import urlparse

import crawler

class WebCrawler(cmd.Cmd):
    prompt = '(Web crawler) '

    def do_crawl(self, args):
        largs = args.split(' ')
        if len(largs) == 1:
            try:
                cr = crawler.Crawler(largs[0])
                cr.cmdloop()
            except ValueError:
                print('Failed to initialize manual crawler')
                return

        elif len(largs) == 2:
            if largs[0] == 'inner':
                cr = crawler.InnerCrawler(' '.join(largs[1:]))
                cr.cmdloop()
            elif largs[0] == 'outer':
                cr = crawler.OuterCrawler(' '.join(largs[1:]))
                cr.cmdloop()
            else:
                print('Unknown crawler. Type \'help crawl\' for details')
                return
        else:
            print('Wrong number of arguments. Type \'help crawl\' for details')


    def do_save(self, args):
        print(args)

    def do_exit(self, args):
        return True

    def precmd(self, args):
        return args.lower()

WebCrawler().cmdloop()

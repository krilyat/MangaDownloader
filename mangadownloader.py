import argparse
import logging as log

from mangadownloader.Starkana import Starkana
from mangadownloader.Eatmanga import Eatmanga
from mangadownloader.Mangastream import Mangastream

parser = argparse.ArgumentParser(
    description='Download mangas from online reading sites')

sitearg = parser.add_argument_group('Site (One required)')\
    .add_mutually_exclusive_group()
sitearg.add_argument('--starkana', action='store_const', const='starkana',
                     dest='site', help='Download from https://starkana.jp/')
sitearg.add_argument('--mangastream', action='store_const',
                     const='mangastream',
                     dest='site', help='Download from http://mangastream.com/')
sitearg.add_argument('--eatmanga', action='store_const',
                     const='eatmanga',
                     dest='site', help='Download from http://eatmanga.com/')

mangaarg = parser.add_argument_group('Manga')
mangaarg.add_argument('title', help='Manga Title')
mangaarg.add_argument('directory', help='Download directory')
mangaarg.add_argument('-c', '--chapter', default='all',
                      help='Download just the specified chapter')

parser.add_argument('--append', action='store_const', const='append',
                    dest='action', default='append',
                    help='Download the new chapter')
parser.add_argument('--complete', action='store_const', const='complete',
                    dest='action',
                    help='Check if all chapter where downloaded properly')
parser.add_argument('--force', action='store_const', const='force',
                    dest='action', help='Download all chapter')
parser.add_argument('--test', action='store_const', const='dry-run',
                    dest='action', help='like --force but without download')

parser.add_argument('-v', '--verbosity', action='count',
                    help='increase output verbosity')

args = parser.parse_args()

if not args.verbosity:
    log.basicConfig(level=log.WARNING)
elif args.verbosity == 1:
    log.basicConfig(level=log.INFO)
else:
    log.basicConfig(level=log.DEBUG)

if not args.site:
    parser.print_help()
elif args.site == 'starkana':
    manga = Starkana(args)
elif args.site == 'mangastream':
    manga = Mangastream(args)
elif args.site == 'eatmanga':
    manga = Eatmanga(args)
manga.download()

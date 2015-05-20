import manga
import utils
import re
import logging as log

from sys import exit
from bs4 import BeautifulSoup as BS


class Mangastream(manga.Book):
    def __init__(self, args):
        manga.Book.__init__(self, args.title,
                            args.directory,
                            args.chapter,
                            args.action)
        self.baseurl = "http://mangastream.com"
        self.addLookup(self.baseurl)
        self.mangauri = "/manga/%s" % self.title

    def download(self):
        """
        List all book/chapter to download
        Starkana use what they call 'scroll mode' to put all pages
        of a chapter in 1 page
        """
        log.debug("download")
        tmp_chapters = []
        soup = BS(utils.get_url("%s%s" % (self.baseurl, self.mangauri),
                                self.lookups).read())
        if self.what_chapter == 'all':
            for chapter in soup.find_all('a'):
                if chapter.get('href') and\
                   re.match('http://readms.com/r/%s/.*'
                            % self.title, chapter.get('href')):
                    log.debug(chapter)
                    url = chapter.get('href')
                    number = chapter.get_text().split(" ", 1)[0]
                    chap = manga.Chapter(utils.unifyNumber(number), url)
                    log.debug("%s\n%s" % (chap.url, chap.number))
                    if chap.number is not None:
                        self.chapters.append(chap)
        elif self.what_chapter == 'last':
            for chapter in soup.find_all('a'):
                if chapter.get('href') and\
                   re.match('http://readms.com/r/%s/.*'
                            % self.title, chapter.get('href')):
                    log.debug(chapter)
                    url = chapter.get('href')
                    number = chapter.get_text().split(" ", 1)[0]
                    chap = manga.Chapter(utils.unifyNumber(number), url)
                    log.debug("%s\n%s" % (chap.url, chap.number))
                    tmp_chapters.append(chap)
            self.chapters.append(max(tmp_chapters, key=lambda x: x.number))
        elif self.what_chapter.isdigit():
            for chapter in soup.find_all('a'):
                if chapter.get('href') and\
                   re.match('http://readms.com/r/%s/.*'
                            % self.title, chapter.get('href')):
                    log.debug(chapter)
                    url = chapter.get('href')
                    number = chapter.get_text().split(" ", 1)[0]
                    chap = manga.Chapter(utils.unifyNumber(number), url)
                    log.debug("%s\n%s" % (chap.url, chap.number))
                    if self.what_chapter == number:
                        self.chapters.append(chap)
                        continue
        self.makeChapters()

    def makeChapters(self):
        log.debug("makeChapters")
        for chapter in self.chapters:
            log.debug("make Pages for chapter %s" % chapter.number)
            c = utils.checkChapterDir(self.basedir, self.title, chapter.number)
            if c != 0 and self.action == "append" and \
               self.what_chapter == "all":
                continue
            try:
                soup = BS(utils.get_url(chapter.url, self.lookups).read())
            except KeyError as e:
                log.debug("KeyError %s, adding to lookups" % e)
                self.addLookup(chapter.url)
                log.debug("Retrying...")
                soup = BS(utils.get_url(chapter.url, self.lookups).read())

            for page in soup.find_all('a'):
                if "Last Page" in page.get_text():
                    log.debug(page.get('href'))
                    lastpage = page.get_text().rstrip(')').split('(')[-1]
                    baseurl = page.get('href')
                    for numPage in range(0, int(lastpage)):
                        number = numPage + 1
                        url = "%s/%d" % (baseurl, number)
                        Page = manga.Page(utils.unifyNumber(number), url)
                        chapter.Pages.append(Page)
        self.downloadBook()

    def downloadBook(self):
        log.debug("downloadBook")
        log.debug("prepareDownload")
        if self.action == "dry-run":
            log.warn("DRY-RUN nothing is written on the filesystem")
            exit()
        utils.checkWorkingDir(self.basedir)
        utils.checkMangaDir(self.basedir, self.title)
        for chapter in self.chapters:
            c = utils.makeChapterDir(self.basedir, self.title, chapter.number)
            if c == 0:
                utils.downloadChapter(self.basedir, self.title,
                                      chapter.number, chapter.Images)
            elif c > 0:
                if self.action == 'force' \
                   or (len(chapter.Images) != c
                        and self.action != 'append') \
                   or self.what_chapter.isdigit():
                    log.debug("chapter.Images %s | c %s" %
                              (len(chapter.Images), c))
                    log.debug("action = %s" % self.action)
                    log.debug("isdigit %s" % self.what_chapter.isdigit())
                    utils.cleanChapterDir(self.basedir, self.title,
                                          chapter.number)
                    utils.downloadChapter(self.basedir, self.title,
                                          chapter.number, chapter.Images)
            else:
                log.info("chapter %s already retrive..." % chapter.number)

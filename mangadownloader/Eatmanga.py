import manga
import utils
import logging as log

from sys import exit
from bs4 import BeautifulSoup as BS


class Eatmanga(manga.Book):
    def __init__(self, args):
        manga.Book.__init__(self, args.title,
                            args.directory,
                            args.chapter,
                            args.action)
        self.baseurl = "http://eatmanga.com"
        self.addLookup(self.baseurl)
        self.mangauri = "/Manga-Scan/%s" % self.title

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
                   "%s" % self.mangauri in chapter.get('href'):
                    url = chapter.get('href')
                    number = chapter.get_text().rsplit(" ", 1)[-1]
                    chap = manga.Chapter(utils.unifyNumber(number), url)
                    log.debug("%s\n%s" % (chap.url, chap.number))
                    self.chapters.append(chap)
        elif self.what_chapter == 'last':
            for chapter in soup.find_all('a'):
                if chapter.get('href') and\
                   "%s" % self.mangauri in chapter.get('href'):
                    url = chapter.get('href')
                    number = chapter.get_text().rsplit(" ", 1)[-1]
                    chap = manga.Chapter(utils.unifyNumber(number), url)
                    log.debug("%s\n%s" % (chap.url, chap.number))
                    tmp_chapters.append(chap)
            self.chapters.append(max(tmp_chapters, key=lambda x: x.number))
        elif self.what_chapter.isdigit():
            for chapter in soup.find_all('a'):
                if chapter.get('href') and\
                   "%s" % self.mangauri in chapter.get('href'):
                    url = chapter.get('href')
                    number = chapter.get_text().rsplit(" ", 1)[-1]
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
            soup = BS(utils.get_url("%s%s" % (self.baseurl, chapter.url),
                                    self.lookups).read())

            for page in soup.find_all('option'):
                log.debug(page.get('value'))
                if page.get('value') and\
                   self.mangauri in page.get('value'):
                    url = page.get('value')
                    number = page.get_text()
                    Page = manga.Page(utils.unifyNumber(number), url)
                    chapter.Pages.append(Page)

        self.makePages()

    def makePages(self):
        for page in self.chapter.Pages:
            soup = BS(utils.get_url("%s%s" % (self.baseurl, page.url),
                                    self.lookups).read())
            for img in soup.find_all('img'):
                if img.get('id') and\
                   "eatmanga_image_big" in img.get('id'):
                    img_url = img.get("src")
                    img_host = img_url.split('/', 3)[-2]
                    self.addLookup(img_url)
                    img_url = img_url.replace(img_host, self.lookups[img_host])
                    img_ext = img_url.rsplit('.', 1)[-1]
                    last_page_number = 0
                    if len(page.Images):
                        last_page_number = int(page.Images[-1].number
                                               .split('.')[0]) + 1
                    i = manga.Image(utils.pageNumber(img_url,
                                                     last_page_number),
                                    img_url, img_host, img_ext)
                    page.Images.append(i)
                    sorted(page.Images, key=lambda img: img.number)
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

import manga
import utils
import logging as log

from DNS import dnslookup
from sys import exit
from bs4 import BeautifulSoup as BS


class Starkana(manga.Book):
    def __init__(self, args):
        manga.Book.__init__(self, args.title,
                            args.directory,
                            args.chapter,
                            args.action)
        self.lookups["starkana.com"] = dnslookup("starkana.com", 'A')[0]
        self.baseurl = "http://%s" % self.lookups["starkana.com"]
        self.mangauri = "/manga/%s/%s" % (self.title[0:1], self.title)
        self.suffix = "?mature_confirm=1&scroll"

    def download(self):
        """
        List all book/chapter to download
        Starkana use what they call 'scroll mode' to put all pages
        of a chapter in 1 page
        """
        log.debug("download")
        tmp_chapters = []
        soup = BS(utils.get_url("%s%s%s" % (self.baseurl, self.mangauri,
                                            self.suffix),
                                "starkana.com").read())
        if self.what_chapter == 'all':
            for chapter in soup.find_all('a'):
                if chapter.get('class') and\
                   "download-link" in chapter.get('class'):
                    url = chapter.get('href')
                    number = chapter.get_text().rsplit(" ", 1)[-1]
                    chap = manga.Page(utils.unifyNumber(number), url)
                    self.chapters.append(chap)
        elif self.what_chapter == 'last':
            for chapter in soup.find_all('a'):
                if chapter.get('class') and\
                   "download-link" in chapter.get('class'):
                    url = chapter.get('href')
                    number = chapter.get_text().rsplit(" ", 1)[-1]
                    chap = manga.Page(utils.unifyNumber(number), url)
                    tmp_chapters.append(chap)
            self.chapters.append(max(tmp_chapters, key=lambda x: x.number))
        elif self.what_chapter.isdigit():
            for chapter in soup.find_all('a'):
                if chapter.get('class') and\
                   "download-link" in chapter.get('class'):
                    number = chapter.get_text().rsplit(" ", 1)[-1]
                    url = chapter.get('href')
                    chap = manga.Page(utils.unifyNumber(number), url)
                    if self.what_chapter == number:
                        self.chapters.append(chap)
                        continue
        self.makePages()

    def makePages(self):
        log.debug("makePages")
        for chapter in self.chapters:
            log.debug("make Pages for chapter %s" % chapter.number)
            c = utils.checkChapterDir(self.basedir, self.title, chapter.number)
            if c != 0 and self.action == "append" and \
               self.what_chapter == "all":
                continue
            soup = BS(utils.get_url("%s%s%s" % (self.baseurl, chapter.url,
                                                self.suffix),
                                    "starkana.com").read())

            for image in soup.find_all('img'):
                image_url = image.get('src')
                if "manga-img" in image_url:
                    img_host = image_url.split('/', 3)[-2]
                    if img_host not in self.lookups:
                        self.lookups[img_host] = dnslookup(img_host, 'A')[0]
                    image_url = image_url.replace(img_host,
                                                  self.lookups[img_host])
                    image_ext = image_url.rsplit('.', 1)[-1]
                    last_page_number = 0
                    if len(chapter.Images):
                        last_page_number = int(chapter.Images[-1].number
                                               .split('.')[0]) + 1
                    i = manga.Image(utils.pageNumber(image_url,
                                                     last_page_number),
                                    image_url, img_host, image_ext)
                    chapter.Images.append(i)
                    sorted(chapter.Images, key=lambda img: img.number)

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

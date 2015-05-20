import urllib2
import re
import logging as log
import string
import os

from time import sleep
from sys import exit


def get_url(url, lookups, retry=5):
    log.debug("get_url")
    log.info("try : %s" % url)
    fqdn = ""
    if type(lookups) is dict:
        fqdn = url.split('/')[2]
        url = url.replace(fqdn, lookups[fqdn])
    else:
        fqdn = lookups

    req_headers = {
        'Host': fqdn,
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'http://www.google.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'}

    # create a request object for the URL
    request = urllib2.Request(urllib2.quote(url, ':/?%&'), headers=req_headers)
    # create an opener object
    opener = urllib2.build_opener()

    try:
        # open a connection and receive http the response headers + contents
        response = opener.open(request)
    except (urllib2.HTTPError, urllib2.URLError) as e:
        # Petite gestion des codes 4xx
        log.warning("error (%s) on : %s\n...try again" % (e, url))
        sleep(5)
        if retry >= 0:
            log.info("retry left : %s" % retry)
            get_url(url, retry - 1)
        else:
            log.critical("error (%s) on : %s\n...no try left" % (e, url))
            exit(1)

    except UnicodeEncodeError, e:
        log.critical(str(url))
        exit(1)

    if response:
        return response
    else:
        get_url(url)


def unifyNumber(num):
    log.debug("unifyNumber")
    number = None
    if not num:
        raise TypeError("number cannot be empty")
    else:
        if type(num) is int or num.isdigit():
            number = "%04d" % int(num)
        elif re.search("[.-]", num):
            num.replace('/', '.')
            part = re.split("[.-]", num)
            if len(part) == 2:
                number = "%04d.%04d" % (int(part[0]), int(part[1]))
        log.debug("%s => %s" % (num, number))
        return number


def pageNumber(url, last_page_number):
    raw_number = re.sub('[!\[\]\&]', '', re.split('/|\.', url)[-2])
    log.debug("pageNumber")
    log.debug("raw_number= '%s'" % raw_number)

    try:
        raw_number.decode('ascii')
    except UnicodeEncodeError:
            pagenumber = "%s.9800" % last_page_number
    else:
        if raw_number.isdigit():
            # deal with correctly formated number
            pagenumber = raw_number
        elif re.match('\d+ $', raw_number):
            # deal with name like "58 "
            pagenumber = re.findall("\d+", raw_number)[0]
        elif re.match('\d+ +\d+$', raw_number):
            # deal with name like "58 "
            pagenumber = re.findall("\d+", raw_number)[-1]
        elif re.match('\d+ \(\d+\)$', raw_number):
            # deal with name like "chapter (page)" ex: 58 (1)
            pagenumber = re.findall("\d+", raw_number.split(" ")[1])[0]
        elif re.match('\d+ \([a-zA-Z]+\)$', raw_number):
            # deal with name like "58 (abc)"
            pagenumber = re.findall("\d+", raw_number)[0]
        elif re.search(' - \d+$', raw_number):
            # deal with name like "Ao no Exorcist v01 c02 - 00"
            if raw_number.split(" - ")[-1].isdigit():
                pagenumber = re.findall("\d+", raw_number.split(" - ")[-1])[0]
            else:
                pagenumber = "%s.8000" % last_page_number
        elif re.search('ch\d+[-_ ]\d+$', raw_number):
            # deal with name like "manga-rainbleach-ch123-19"
            pagenumber = re.findall("\d+", raw_number)[-1]
        elif re.search('ch\d+pg\d+$', raw_number):
            # deal with name like "manga-rainbleach-ch123pg19"
            pagenumber = re.findall("\d+", raw_number)[-1]
        elif re.match('.*_\d*(-\d*)?$', raw_number):
            # deal with name like "DEAD_01_0008-0009"
            # deal with name like "DEAD_01_0079"
            pagenumber = re.findall('(\d+|\d+-\d+)$', raw_number)[0]
        elif re.search('_\d+(-\d+)?(_[a-zA-Z]+)?$', raw_number):
            # deal with name like "[MRI]Bakuman_155_02_credits"
            pagenumber = re.findall('(\d+|\d+-\d+)$',
                                    raw_number.rsplit('_', 1)[0])[0]
        elif re.match('\d+-[a-zA-Z]+', raw_number):
            # deal with pagesname like "00-ANECP"
            pagenumber = raw_number.split("-")[0]
        elif re.match('\d+[a-zA-Z]', raw_number):
            # deal with pagesname like "00b"
            subnumber = string.lowercase.index(re.findall('[a-zA-Z]',
                                               raw_number)[0].lower()) + 1000
            pagenumber = "%s.%s" % (re.findall('\d+',
                                    raw_number)[0],
                                    subnumber)
        elif re.search('[-_]\d+[a-zA-Z]', raw_number):
            # deal with pagesname like "Wallman-c1_00b" or "002--003a"
            numberpart = re.split('[-_]', raw_number)[-1]
            letterpart = string.lowercase.index(re.findall('[a-zA-Z]',
                                                numberpart)[0].lower()) + 1000
            pagenumber = "%s.%s" % (re.findall('\d+',
                                    numberpart)[0],
                                    letterpart)
        elif re.match('\d+ ?[a-zA-Z]+', raw_number):
            # deal with pagesname like "00ANECP"
            pagenumber = re.findall('\d+', raw_number)[0]
        elif re.search('\d+(_[a-zA-Z]+)+$', raw_number):
            # deal with pagesname like "00_NS"
            pagenumber = re.findall('\d+', raw_number)[-1]
        elif re.match('\d+ - .{7}$', raw_number):
            # deal with name like "02 - p28StSG"
            if raw_number.split(" - ")[-1].isdigit():
                pagenumber = re.findall("\d+", raw_number.split(" - ")[0])[0]
            else:
                pagenumber = "%s.8000" % last_page_number
        elif re.search('\d+[-_]\d+([-_]\d+)?', raw_number, re.IGNORECASE):
            # deal with pagesnames like "170-01" "170-02-03"
            pagenumber = "%s.9100" % re.findall('\d+', raw_number)[-1]
        elif re.match('.*(credit(s)?|recruit)', raw_number, re.IGNORECASE):
            # deal with pagesnames like credit or other
            pagenumber = "%s.9000" % last_page_number
        elif re.match('[a-z-_]+', raw_number, re.IGNORECASE):
            # deal with pagesnames like credit or other
            pagenumber = "%s.9900" % last_page_number
        else:
            log.warn("What else... %s" % raw_number)
            pagenumber = raw_number

    pagenumber = unifyNumber(str(pagenumber))
    log.debug("pagenumber %s" % pagenumber)
    return pagenumber


def checkWorkingDir(d):
    log.debug("checkWorkingDir %s" % d)
    if os.path.isfile(d):
        raise TypeError("The Working Dir %s is a file" % d)
    elif not os.path.isdir(d):
        raise OSError("No such file or directory: '%s'" % d)


def checkMangaDir(d, t):
    mangadir = os.path.join(d, t)
    if os.path.isfile(mangadir):
        raise TypeError("The Manga Dir %s is a file" % mangadir)
    elif not os.path.isdir(mangadir):
        log.info("creating %s" % mangadir)
        os.mkdir(mangadir)
    else:
        log.info("%s seems to be already here..." % mangadir)


def makeChapterDir(d, t, c):
    chapterdir = os.path.join(d, t, c)
    if not os.path.isdir(chapterdir):
        log.info("creating %s" % chapterdir)
        os.mkdir(chapterdir)
        return 0
    else:
        log.info("[makeChapterDir] %s seems to be already here.." % chapterdir)
        return len(os.listdir(chapterdir))
    return -1


def cleanChapterDir(d, t, c):
    chapterdir = os.path.join(d, t, c)
    log.info("cleaning %s" % chapterdir)
    for root, dirs, files in os.walk(chapterdir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))


def checkChapterDir(d, t, c):
    chapterdir = os.path.join(d, t, c)
    if os.path.isfile(chapterdir):
        raise TypeError("The Chapter Dir %s is a file" % chapterdir)
    elif not os.path.isdir(chapterdir):
        return 0
    else:
        log.info("[checkChapterDir] %s seems to be already here." % chapterdir)
        return len(os.listdir(chapterdir))
    return -1


def downloadChapter(d, t, c, i):
    log.debug("downloadChapter")
    chapterdir = os.path.join(d, t, c)
    for image in i:
        log.debug("page %s %s %s %s" % (image.number, image.ext, image.url,
                                        image.host))
        imgname = os.path.join(chapterdir, "%s.%s" % (image.number, image.ext))
        if os.path.isfile(imgname):
            image.number = "%s.5000" % image.number
            log.debug("New page %s %s %s" % (image.number,
                                             image.ext,
                                             image.url))
            imgname = os.path.join(chapterdir, "%s.%s" % (image.number,
                                                          image.ext))
        with open(imgname, 'wb') as img:
            log.debug("download image %s" % image.url)
            img.write(get_url(image.url, image.host).read())
            log.debug("downloaded %s" % image.url)

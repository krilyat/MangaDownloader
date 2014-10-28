class Book(object):

    def __init__(self, title, basedir, chapter, action):
        (self.title,
            self.what_chapter,
            self.basedir,
            self.action) = title, chapter, basedir, action
        self.lookups = dict()
        self.chapters = []


class Cpi(object):

    def __init__(self, number, url):
        self.number = number
        self.url = url


class Chapter(Cpi):

    def __init__(self, number, url):
        Cpi.__init__(self, number, url)
        self.Pages = []


class Page(Cpi):

    def __init__(self, number, url):
        Cpi.__init__(self, number, url)
        self.Images = []


class Image(Cpi):

    def __init__(self, number, url, host, ext):
        Cpi.__init__(self, number, url)
        self.host = host
        self.ext = ext

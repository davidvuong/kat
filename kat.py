#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bs4
import urllib2
import gzip
import StringIO

BASE_URL = 'https://kat.cr/'


class Category(object):
    ALL = 'all'
    MOVIES = 'movies'
    TV = 'tv'
    ANIME = 'anime'
    MUSIC = 'music'
    BOOKS = 'books'
    APPS = 'applications'
    GAMES = 'games'
    XXX = 'xxx'


class SortType(object):
    SIZE = 'size'
    FILES = 'files_count'
    AGE = 'time_add'
    SEED = 'seeders'
    LEECH = 'leechers'


class SortOrder(object):
    ASC = 'asc'
    DESC = 'desc'


class Request(object):
    """Abstracts the process of searching for torrents on KAT.

    Search results are then stored within Search instances in a Torrent
    abstraction.

    """
    def __init__(self, base_url=BASE_URL):
        self.torrents = []
        self.search_url = base_url + 'usearch/'

        self.term = None
        self.category = None
        self.order = None
        self.sort = None

    def search(self, term=None, category=None, pages=1, sort=None, order=None):
        """Given a `term` search for matching torrents on KAT."""
        search_url = self.get_search_url(term, category)
        sort_url = self.get_sort_url(sort, order)
        for p in xrange(1, pages + 1):
            endpoint = '%s/%s/%s' % (search_url, p, sort_url)
            self.torrents += self.get_torrents(endpoint)
        return self.torrents

    def request_page(self, url):
        """Returns the BeautifulSoup object for given url."""
        response = urllib2.urlopen(url)
        response_data = response.read()
        try:
            compressed = StringIO.StringIO(response_data)
            gzipper = gzip.GzipFile(fileobj=compressed)
            response_data = gzipper.read()
        except IOError:
            pass  # The response was not gzipped.
        return bs4.BeautifulSoup(response_data)

    def get_sort_url(self, sort, order=SortOrder.DESC):
        if not sort:
            return ''
        self.order, self.sort = order, sort
        return '?field=%s&sorder=%s' % (self.sort, self.order)

    def get_search_url(self, term, category):
        self.term = term
        search_url = self.search_url
        search_url = self.search_url + self.term
        if category:
            self.category = category
            search_url += ' category:' + self.category
        return search_url

    def get_torrents(self, page_url):
        """Retrieve torrent results from the search page.

        Iterates over all table row elements, parses each row and returns
        the each torrent's details as list of dictionaries.

        """
        response = self.request_page(page_url)
        torrents = response.find_all('tr', class_=['even', 'odd'])

        results = []
        for i, item in enumerate(torrents):
            title = item.find('a', class_='cellMainLink')
            tds = item.find_all('td', class_='center')
            category = self.get_torrent_category(item)

            download_url = item.find('a', title='Verified Torrent').get('href')
            magnet_url = item.find('a', title='Torrent magnet link').get('href')
            is_verified = item.find('a', title='Download torrent file') is not None

            results.append({
                'title': title.text,
                'url': BASE_URL[:-1] + title.get('href'),
                'size': tds[0].text,
                'files': tds[1].text,
                'age': tds[2].text,
                'seed': tds[3].text,
                'leech': tds[4].text,
                'category': category,
                'is_verified': is_verified,
                'download_url': download_url,
                'magnet_url': magnet_url,
            })
        return results

    def get_torrent_category(self, tag, result=None):
        """Extract the category from `tag`.

        The search page has the torrent category in the url <a href='/tv/'>TV</a>.
        The home page however, does not. Instead, the result number is used to
        decide on the torrent category.

        """
        categories = [
            'movies', 'tv', 'music', 'games', 'applications', 'anime', 'books', 'xxx',
        ]
        for category in categories:
            if tag.select('a[href=/%s/]' % category):
                return category
        return None

    def __iter__(self):
        return iter(self.torrents)

    def __len__(self):
        return len(self.torrents)

    def __getitem__(self, k):
        return self.torrents[k]


def search(term, category=Category.ALL, pages=1, sort=None, order=None):
    """Returns torrents matching `term` in `category`.

    Search results can sorted and span multiple pages.

    """
    request = Request()
    request.search(term=term, category=category, pages=pages, sort=sort, order=order)
    return request

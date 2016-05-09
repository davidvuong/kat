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


class Request(object):
    """Abstracts the process of searching for torrents on KAT."""
    def __init__(self, base_url=BASE_URL):
        self.torrents = []
        self.search_url = base_url + 'usearch/'

        self.term = None
        self.category = None
        self.sort = None

    def search(self, term, category, pages, sort, desc):
        """Given a `term` search for matching torrents on KAT."""
        search_url = self.get_search_url(term, category)
        sort_url = self.get_sort_url(sort, desc)
        for p in xrange(1, pages + 1):
            endpoint = '%s/%s/%s' % (search_url, p, sort_url)
            self.torrents += self.get_torrents(endpoint)
        return self.torrents

    def request_page(self, url):
        """Returns the BeautifulSoup object for given url."""
        try:
            response = urllib2.urlopen(url)
        except (urllib2.URLError, urllib2.HTTPError):
            return None  # Connection error or bad query.

        response_data = response.read()
        try:
            compressed = StringIO.StringIO(response_data)
            gzipper = gzip.GzipFile(fileobj=compressed)
            response_data = gzipper.read()
        except IOError:
            pass  # The response was not gzipped.
        return bs4.BeautifulSoup(response_data)

    def get_sort_url(self, sort, desc):
        if not sort:
            return ''
        self.sort = sort
        return '?field=%s&sorder=%s' % (self.sort, 'desc' if desc else 'asc')

    def get_search_url(self, term, category):
        self.term = term
        search_url = self.search_url + self.term
        if category:
            self.category = category
            search_url += ' category:' + self.category
        return search_url

    def get_torrents(self, page_url):
        """Retrieve torrent results from the search page.

        Iterates over all table row elements, parses each row and returns
        the each torrent's details as list of dictionaries.

        None is returned if a request error occurred. A list of torrents
        is returned otherwise.

        """
        results, response = [], self.request_page(page_url)
        if not response:
            return None

        torrents = response.find_all('tr', class_=['even', 'odd'])
        for torrent in torrents:
            title = torrent.find('a', class_='cellMainLink')
            tds = torrent.find_all('td', class_='center')
            category = self.get_torrent_category(torrent)

            download_url = torrent.find('a', title='Download torrent file').get('href')
            magnet_url = torrent.find('a', title='Torrent magnet link').get('href')
            is_verified = torrent.find('a', title='Verified Torrent') is not None

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

    def get_torrent_category(self, tag):
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


def search(term, category=Category.ALL, pages=1, sort=SortType.SEED, desc=True):
    """Returns a list of torrent dictionaries that matches the search criteria.

    When searching for torrents, results can be sorted. See `SortType` for the
    various ways torrents can be sorted in. By default, torrents are sorted by
    the seed count in descending order.

    Torrents can also be filtered by their category. By default all categories will
    be considered. See `Category` for all torrent categories.

    To fetch more than one page of results, update the `pages` value.

    Args:
        term (str): Torrent search query used to check against torrent titles.
        category (Optional[str]): Filter the results by this category.
        pages (Optional[int]): Total number of pages we want to retrieve.
        sort (Optional[str]): Torrent property to sort based on.
        desc (Optional[bool]): Sort ordering based on `sort`.

    Returns:
        list: A list of torrent dictionaries.

    """
    request = Request()
    request.search(term, category, pages, sort, desc)
    return request

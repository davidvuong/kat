#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bs4
import requests

BASE_URL = 'https://kat.cr/'


def _get_soup(page):
    """Return BeautifulSoup object for given page."""
    request = requests.get(page)
    return bs4.BeautifulSoup(request.text)


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


class Torrent(object):
    """Represents a torrent as found in KAT search results."""

    def __init__(self, title, category, link, size, seed, leech, magnet,
                 download, files, age, is_verified):
        self.title = title
        self.category = category
        self.page = BASE_URL[:-1] + link
        self.size = size
        self.seeders = seed
        self.leechers = leech
        self._magnet = magnet
        self._download = download
        self.files = files
        self.age = age
        self._data = None  # bs4 html for getting download & magnet
        self.is_verified = is_verified

    def print_details(self):
        """Print torrent details."""
        print 'Title:', self.title
        print 'Category:', self.category
        print 'Page:', self.page
        print 'Size:', self.size
        print 'Files:', self.files
        print 'Age:', self.age
        print 'Seeds:', self.seeders
        print 'Leechers:', self.leechers
        print 'Verified:', self.is_verified
        print 'Magnet:', self.magnet
        print 'Download:', self.download

    @property
    def download(self):
        if self._download:
            return self._download

        if self._data:
            self._download = self._data.find(
                'a', class_='siteButton giantButton verifTorrentButton'
            ).get('href')
            return self._download

        # No data. Parse torrent page
        soup = _get_soup(self.page)
        self._download = soup.find(
            'a', class_='siteButton giantButton verifTorrentButton'
        ).get('href')
        self._data = soup
        return self._download

    @property
    def magnet(self):
        if self._magnet:
            return self._magnet
        if self._data:
            self._magnet = self._data.find(
                'a', class_='siteButton giantIcon magnetlinkButton'
            ).get('href')
            return self._magnet

        soup = _get_soup(self.page)
        self._magnet = soup.find(
            'a', class_='siteButton giantIcon magnetlinkButton'
        ).get('href')
        self._data = soup
        return self._magnet


class Search(object):
    """Abstracts the process of searching for torrents on KAT.

    Search results are then stored within Search instances in a Torrent
    abstraction.

    """
    SEARCH_URL = BASE_URL + 'usearch/'
    LATEST_URL = BASE_URL + 'new'

    def __init__(self):
        self.torrents = []
        self._current_page = 1
        self.term = None
        self.category = None
        self.order = None
        self.sort = None
        self.current_url = None

    def search(self, term=None, category=None, pages=1, url=SEARCH_URL,
               sort=None, order=None):
        """Given a `term` search for matching torrents on KAT."""

        if not self.current_url:
            self.current_url = url

        if self.current_url == BASE_URL:
            # Searching home page so no formatting
            results = self._get_results(self.current_url)
            self._add_results(results)
        else:
            search = self._format_search(term, category)
            sorting = self._format_sort(sort, order)

            # Now get the results.
            for i in range(pages):
                results = self._get_results(
                    search + '/' + str(self._current_page) + '/' + sorting
                )
                self._add_results(results)
                self._current_page += 1
            self._current_page -= 1

    def popular(self, category, sort_option='title'):
        self.search(url=BASE_URL)
        if category:
            self._categorize(category)
        self.torrents.sort(key=lambda t: t.__getattribute__(sort_option))

    def recent(self, category, pages, sort, order):
        self.search(pages=pages, url=self.LATEST_URL, sort=sort, order=order)
        if category:
            self._categorize(category)

    def _categorize(self, category):
        """Remove torrents with unwanted category from self.torrents."""
        self.torrents = [
            result for result in self.torrents if result.category == category]

    def _format_sort(self, sort, order):
        sorting = ''
        if sort:
            self.sort = sort
            sorting = '?field=' + self.sort
            if order:
                self.order = order
            else:
                self.order = SortOrder.DESC
            sorting = sorting + '&sorder=' + self.order
        return sorting

    def _format_search(self, term, category):
        search = self.current_url
        if term:
            self.term = term
            search = self.current_url + term
        if category:
            self.category = category
            search = search + ' category:' + category
        return search

    def page(self, i):
        """Get the ith page in the search result using the previously used term."""
        self.torrents = []
        self._current_page = i

        self.search(
            term=self.term,
            category=self.category,
            sort=self.sort,
            order=self.order,
        )

    def next_page(self):
        self.page(self._current_page + 1)

    def _get_results(self, page):
        """
        Find every div tag containing torrent details on given page,
        then parse the results into a list of Torrents and return them.

        """
        soup = _get_soup(page)
        details = soup.find_all('tr', class_='odd')
        even = soup.find_all('tr', class_='even')
        for i in range(len(even)):  # Join the results.
            details.insert((i * 2) + 1, even[i])
        return self._parse_details(details)

    def _parse_details(self, tag_list):
        """
        Given a list of tags from either a search page or the KAT home page,
        parse the details and return a list of Torrent objects.

        """
        results = []
        for i, item in enumerate(tag_list):
            title = item.find('a', class_='cellMainLink')
            title_text = title.text
            link = title.get('href')

            tds = item.find_all('td', class_='center')
            size = tds[0].text
            files = tds[1].text
            age = tds[2].text
            seed = tds[3].text
            leech = tds[4].text

            download = item.find('a', title='Verified Torrent')
            magnet = item.find('a', title='Torrent magnet link')
            is_verified = item.find('a', title='Download torrent file') is not None

            # Home page doesn't have magnet or download links.
            if magnet:
                magnet = magnet.get('href')
            if download:
                download = download.get('href')

            # Get category changes if we're parsing home vs. search page.
            if self.current_url == BASE_URL:
                category = self._get_torrent_category(item, result=i)
            else:
                category = self._get_torrent_category(item)
            torrent = Torrent(
                title_text,
                category,
                link,
                size,
                seed,
                leech,
                magnet,
                download,
                files,
                age,
                is_verified,
            )
            results.append(torrent)
        return results

    def _get_torrent_category(self, tag, result=None):
        """Extract the category from `tag`.

        The search page has the torrent category in the url <a href='/tv/'>TV</a>.
        The home page however, does not. Instead, the result number is used to
        decide on the torrent category.

        """
        hrefs, category = [
            'movies', 'tv', 'music', 'games', 'applications', 'anime', 'books', 'xxx',
        ], None

        # Searching home page, get category from result number.
        if result:  # if result: 0 returns false.
            return hrefs[result / 10]
        for href in hrefs:
            if tag.select('a[href=/%s/]' % href):
                return href
        return None

    def _add_results(self, results):
        for item in results:
            self.torrents.append(item)

    @property
    def current_page(self):
        return self._current_page

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
    s = Search()
    s.search(term=term, category=category, pages=pages, sort=sort, order=order)
    return s


def popular(category=None, sortOption='title'):
    """Returns the torrents appearing on the KAT home page.

    Torrents can be categorized but thye cannot be sorted or contain multiple pages.

    """
    s = Search()
    s.popular(category, sortOption)
    return s


def recent(category=None, pages=1, sort=None, order=None):
    """Returns the most recently added torrents.

    Torrents can be sorted, categorized, and contain multiple pages.

    """
    s = Search()
    s.recent(category, pages, sort, order)
    return s

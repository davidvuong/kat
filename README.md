# KAT - Kickass Torrents

[![Code style: pep8](https://img.shields.io/badge/code%20style-pep8-yellow.svg?style=flat-square)](https://www.python.org/dev/peps/pep-0008/)

**Welcome to KAT!**

kat.py is an incredibly simple Python wrapper over the KAT search functionality. The code was originally taken from [KickassTorrentsAPI](https://github.com/stephan-mclean/KickassTorrentsAPI) however, there hasn't been much activity for almost a year and some features weren't working due to changes to the KAT website.

kat.py uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to scrape data made against `https://kat.cr/usearch/<query>/`. Torrent details are then parsed and stored as a list of dictionaries. You can check out the source to see which fields are extracted. See below for usage examples.

## Installation

```
pip install git+git@github.com:davidvuong/kat.git
```

## Usage

```python
import kat
from pprint import pprint

# Retrieves torrents with "the flash" in their title and displays results.
for torrent in kat.search('the flash'):
    pprint(torrent)

# Retrieves first 5 pages, filtering torrents by category.
torrents = kat.search('arrow', pages=5, category=kat.CATEGORY.TV)

# Retrieves sorted results by the leech count (ascending order).
torrents = kat.search('game of thrones', sort=kat.SortType.LEECH, desc=False)

# Displays the number of torrents found.
print len(torrents)
```

## License

[MIT](LICENSE.md)

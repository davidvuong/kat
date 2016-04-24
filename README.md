# KAT

[![Code style: pep8](https://img.shields.io/badge/code%20style-pep8-yellow.svg?style=flat-square)](https://www.python.org/dev/peps/pep-0008/)

**Welcome to KAT!**

kat.py is an incredibly simple Python wrapper over the KAT search functionality. The code was originally taken from [KickassTorrentsAPI](https://github.com/stephan-mclean/KickassTorrentsAPI) however, there hasn't been much activity for almost a year and some basic features weren't working due to changes to the KAT website. In addition, the interface felt a bit clunky to use.

kat.py uses BeautifulSoup to scrape data from `https://kat.cr/usearch/<query>/` to extract fields such as as title, file size, number of files, magnet and torrent URLs along with many other fields.

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

# Retrieve the first 5 pages, filtering torrents by those in the TV category.
torrents = kat.search('arrow', pages=5, category=kat.CATEGORY.TV)

# Retrieve and sort results by the leech count (ascending order).
torrents = kat.search('game of thrones', sort=kat.SortType.LEECH, desc=False)

# Displays the number of torrents found.
print len(torrents)
```

## License

[MIT](LICENSE.md)

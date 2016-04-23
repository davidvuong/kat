# KAT

**Welcome to KAT!**

kat.py is an incredibly simple Python wrapper over the KAT search functionality. The code was originally taken from [KickassTorrentsAPI](https://github.com/stephan-mclean/KickassTorrentsAPI) however, there hasn't been much activity for almost a year and some basic features weren't working due to changes to the KAT website. In addition, the interface felt a bit clunky to use.

kat.py uses BeautifulSoup to scrape data from `https://kat.cr/usearch/<query>/` to extract fields such as as title, file size, number of files, magnet and torrent URLs along with many other fields.

This project is currently a WIP.

## Installation

```
pip install git+git@github.com:davidvuong/kat.git
```

## Usage

```python
import kat

# Searches for torrents with "the flash" in their title and displays results.
results = kat.search('the flash')
for result in results:
    result.print_details()
    print result.magnet

# Retrieves all torrents currently on the home page.
results = kat.popular()

# Retrieves torrents on the home page which belong to games.
results = kat.popular(category=kat.Categories.GAMES)

# Retrieves the number of torrents found.
print len(results)

# Retrieve torrents matching query that belong in TV, sorting by seeders in desc.
results kat.search(
    'the walking dead',
    category=kat.Category.TV,
    sort=kat.SortType.SEED,
    order=kat.SortOrder.DESC,
)

# They can also span multiple pages
results = kat.search('the walking dead', pages=3)

# And we can keep track of the current page (prints 3)
print results.current_page

# We can go to a particular page.
results.page(7)

# And to the next page.
results.next_page()
```

This is currently the interface however it is subject to change.

## License

[MIT](LICENSE.md)

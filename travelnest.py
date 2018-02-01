import logging
from multiprocessing import Pool

import requests
import sys
from bs4 import BeautifulSoup

from travelnest import airbnb
from travelnest.output import output_listings

log = logging.getLogger("travelnest")


def soup_for_url(url):
    log.info("Downloading URL: {}".format(url))
    response = requests.get(url)
    log.debug("Parsing response from {}".format(url))
    return BeautifulSoup(response.text, "html.parser")


def scrape_airbnb_listing(listing_id):
    url = airbnb.url(listing_id)
    soup = soup_for_url(url)
    base = {"url": url, "id": listing_id, "source": "airbnb"}

    if not airbnb.is_complete(soup):
        log.error(
            "Incomplete result downloaded for listing {}.  "
            "Unable to extract fields for this property.".format(url))
        return base

    log.info("Scraping Airbnb listing {}".format(listing_id))
    properties = airbnb.scrape(soup)
    return dict(properties, **base)


def main():
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv else logging.WARN)
    listing_ids = (
        19278160,  # York Place: Luxurious apartment For Two adults.
        14531512,  # Garden Rooms: Featured in Grand Designs Sept 2017
        19292873,  # Turreted penthouse apartment near Edinburgh Castle
    )

    pool = Pool(len(listing_ids))
    if hasattr(pool, '__exit__'):
        # python3
        with pool as p:
            listings = p.map(scrape_airbnb_listing, listing_ids)
    else:
        # python2.7
        listings = pool.map(scrape_airbnb_listing, listing_ids)

    output_listings(listings)


if __name__ == '__main__':
    main()

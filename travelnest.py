import json
import logging
from multiprocessing import Pool

import requests
import sys
from bs4 import BeautifulSoup

import airbnb

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


def listing_to_json(listing):
    properties = []
    data = {
        "id": listing["id"],
        "url": listing["url"],
        "source": listing["source"],
        "properties": properties,
    }
    for k, v in listing.items():
        if k not in ("id", "url", "source"):
            properties.append({"key": k, "value": v})
    return data


def output_listings(listings, out=sys.stdout):
    json_dict = {
        "listings": list(map(listing_to_json, listings))
    }
    json.dump(json_dict, out, indent=2, sort_keys=True)


def main():
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv else logging.WARN)
    listing_ids = (
        19278160,  # York Place: Luxurious apartment For Two adults.
        14531512,  # Garden Rooms: Featured in Grand Designs Sept 2017
        19292873,  # Turreted penthouse apartment near Edinburgh Castle
    )

    with Pool(len(listing_ids)) as p:
        listings = p.map(scrape_airbnb_listing, listing_ids)

    output_listings(listings)


if __name__ == '__main__':
    main()

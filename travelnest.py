import functools
import logging
import re
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup

from exceptions import TravelnestException, FieldNotFound, MultipleFieldMatches

log = logging.getLogger("travelnest")


SECTION_MARKERS = {
    "summary": {"id": "summary"},
    "amenities": {"class": "amenities"},
}
AIRBNB_FIELDS = {}


def airbnb_field(key, section=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(soup):
            if section is not None:
                section_marker = SECTION_MARKERS[section]
                soup = soup.find("div", attrs=section_marker)

            try:
                return fn(soup)
            except TravelnestException:
                return "<Unknown>"
            except Exception as e:
                log.error("Unexpected error for field {} : {}".format(key, e), exc_info=True)
                return "<Error>"

        wrapper.key = key
        AIRBNB_FIELDS[key] = wrapper
        return wrapper

    return decorator


@airbnb_field("Title", section="summary")
def title(soup):
    matches = soup.find("div", attrs={"itemprop": "name"})
    if not matches:
        raise FieldNotFound("No title field found")
    return re.sub('\s+', ' ', matches.text)


@airbnb_field("Property Type", section="summary")
def property_type(soup):
    matches = soup.find_all("small", text=re.compile("[a-zA-Z\s]+"))
    if not matches:
        raise FieldNotFound("No property type field found")
    if len(matches) > 1:
        raise MultipleFieldMatches("Property type criteria matches multiple entities")
    return matches[0].text


@airbnb_field("Bedrooms", section="summary")
def bedrooms(soup):
    regex = re.compile("\d+\s+bed")
    matches = soup.find_all(text=regex)
    if not matches:
        raise FieldNotFound("No bedroom(s) field found")

    text = matches[0]
    return int(text.split()[0])


@airbnb_field("Bathrooms", section="summary")
def bathrooms(soup):
    regex = re.compile("\d+\s+bath")
    matches = soup.find_all(text=regex)
    if not matches:
        raise FieldNotFound("No bath(s) field found")

    text = matches[0]
    return int(text.split()[0])


@airbnb_field("Amenities", section="amenities")
def amenities(soup):
    matches = soup.find_all("span", text=re.compile("[a-zA-Z\s]+"))
    return sorted({m.text for m in matches if 'menities' not in m.text})


def airbnb_url(listing_id):
    return "https://www.airbnb.co.uk/rooms/{}?s=51".format(listing_id)


def scrape_airbnb(soup):
    return {
        key: scrape_property(soup)
        for key, scrape_property in AIRBNB_FIELDS.items()
    }


def soup_for_url(url):
    log.info("Downloading URL: {}".format(url))
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def scrape_airbnb_listing(listing_id):
    url = airbnb_url(listing_id)
    soup = soup_for_url(url)
    properties = scrape_airbnb(soup)
    return properties


def main():
    logging.basicConfig(level=logging.DEBUG)
    listing_ids = (
        19278160,  # York Place: Luxurious apartment For Two adults.
        14531512,  # Garden Rooms: Featured in Grand Designs Sept 2017
        19292873,  # Turreted penthouse apartment near Edinburgh Castle
        # 13945425,  # Others for testing
        # 819535,
    )

    with Pool(len(listing_ids)) as p:
        records = p.map(scrape_airbnb_listing, listing_ids)

    records = dict(zip(listing_ids, records))

    print(records)


if __name__ == '__main__':
    main()

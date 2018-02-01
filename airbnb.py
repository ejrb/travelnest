"""This module contains functionality for scraping a listing from airbnb.co.uk
New fields may be added by decorating a function with the @airbnb_field decorator."""
import functools
import logging
import re

from exceptions import TravelnestException, FieldNotFound, MultipleFieldMatches


log = logging.getLogger(__name__)

REGEX_PTYPE = re.compile("([A-Za-z]+\s+room|Entire\s+[A-za-z]+)")
REGEX_BEDS = re.compile("\d+\s+beds?$")
REGEX_BATHS = re.compile("\d+\s+baths?$")
REGEX_ANY_TEXT = re.compile("^[a-zA-Z\s]+$")

SECTION_MARKERS = {
    "summary": {"id": "summary"},
    "amenities": {"class": "amenities"},
}
REGISTERED_FIELDS = {}


def _register_field(key, fn):
    fn.key = key
    REGISTERED_FIELDS[key] = fn


def _cleanup_whitespace(text):
    return re.sub('\s+', ' ', text)


def select_section(soup, section_key):
    """Select only a section of the full soup, to simplify later searches """
    section_marker = SECTION_MARKERS[section_key]
    section_soup = soup.find("div", attrs=section_marker)
    if section_soup is None:
        raise FieldNotFound("Unable to find section {}".format(section_key))
    return section_soup


def airbnb_field(key, section=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(soup):
            try:
                if section is not None:
                    soup = select_section(soup, section)
                return fn(soup)
            except TravelnestException:
                log.warning("Unable to find field '{}'".format(key), exc_info=True)
                return "<Unknown>"
            except Exception as e:
                log.error("Unexpected error for field {} : {}".format(key, e), exc_info=True)
                return "<Error>"

        _register_field(key, wrapper)
        return wrapper

    return decorator


@airbnb_field("Title", section="summary")
def title(soup):
    """Listing title is identified by the itemprop=name tag property"""
    matches = soup.find("div", attrs={"itemprop": "name"})
    if not matches:
        raise FieldNotFound("No title field found")
    return _cleanup_whitespace(matches.text)


@airbnb_field("Property Type", section="summary")
def property_type(soup):
    """Airbnb property types may be 'Entire home', 'Entire flat', 'Single room' or 'Shared room'"""
    matches = soup.find_all("small", text=REGEX_PTYPE)
    if not matches:
        raise FieldNotFound("No property type field found")
    if len(matches) > 1:
        raise MultipleFieldMatches("Property type criteria matches multiple entities")
    return matches[0].text


@airbnb_field("Bedrooms", section="summary")
def bedrooms(soup):
    """Airbnb always lists number of beds, but sometimes number of
    bedrooms if property is not a studio. This uses number of beds """
    matches = soup.find_all(text=REGEX_BEDS)
    if not matches:
        raise FieldNotFound("No bedroom(s) field found")

    text = matches[0]
    return int(text.split()[0])


@airbnb_field("Bathrooms", section="summary")
def bathrooms(soup):
    """Looks for number of baths"""
    matches = soup.find_all(text=REGEX_BATHS)
    if not matches:
        raise FieldNotFound("No bath(s) field found")

    text = matches[0]
    return int(text.split()[0])


@airbnb_field("Amenities", section="amenities")
def amenities(soup):
    """Some amenities are hidden by the Javascript.  Future iteration could click on
    the "Show all amenities" button before downloading. """
    matches = soup.find_all("span", text=REGEX_ANY_TEXT)
    return sorted({m.text for m in matches if 'amenities' not in m.text.lower()})


def url(listing_id):
    return "https://www.airbnb.co.uk/rooms/{}?s=51".format(listing_id)


def is_complete(soup):
    """Does soup contain all expected Airbnb sections"""
    for section in SECTION_MARKERS:
        try:
            select_section(soup, section)
        except TravelnestException:
            return False
    return True


def scrape(soup):
    return {
        key: scrape_property(soup)
        for key, scrape_property in REGISTERED_FIELDS.items()
    }

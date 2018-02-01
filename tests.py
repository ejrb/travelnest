import os
import pytest
from bs4 import BeautifulSoup

from travelnest.airbnb import title, property_type, bedrooms, bathrooms, amenities, scrape
from travelnest.output import listing_to_json


@pytest.fixture(scope='module')
def soup():
    path = os.path.join(os.path.dirname(__file__), "TestPage.htm")
    with open(path, "r") as fp:
        html = fp.read()

    return BeautifulSoup(html, "html.parser")


def test_title(soup):
    result = title(soup)
    assert result == "York Place: Luxurious apartment For Two adults."


def test_property_type(soup):
    result = property_type(soup)
    assert result == 'Entire flat'


def test_bedroom_count(soup):
    result = bedrooms(soup)
    assert result == 1


def test_bathroom_count(soup):
    result = bathrooms(soup)
    assert result == 1


def test_amenities(soup):
    result = amenities(soup)
    assert len(result) == 6
    assert result == [
        'Hair dryer',
        'Iron',
        'Kitchen',
        'Laptop friendly workspace',
        'TV',
        'Wireless Internet',
    ]


def test_scrape_airbnb(soup):
    result = scrape(soup)

    assert result == {
        "Title": "York Place: Luxurious apartment For Two adults.",
        "Property Type": "Entire flat",
        "Bathrooms": 1,
        "Bedrooms": 1,
        "Amenities": [
            'Hair dryer',
            'Iron',
            'Kitchen',
            'Laptop friendly workspace',
            'TV',
            'Wireless Internet',
        ]
    }


def test_listing_to_json():
    data = {
        "id": 1245,
        "url": "https://www.airbnb.co.uk/rooms/19278160?s=51",
        "source": "airbnb",
        "Customer rating": 4.3,
        "Other field": ["something"]
    }

    result = listing_to_json(data)

    assert result == {
        "id": 1245,
        "url": "https://www.airbnb.co.uk/rooms/19278160?s=51",
        "source": "airbnb",
        "properties": [
            {"key": "Customer rating", "value": 4.3},
            {"key": "Other field", "value": ["something"]},
        ]
    }

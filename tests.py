import pytest
from bs4 import BeautifulSoup

from travelnest import property_type, bedrooms, title, bathrooms, amenities, scrape_airbnb


@pytest.fixture(scope='module')
def soup():
    with open("TestPage.htm") as fp:
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
    result = scrape_airbnb(soup)

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

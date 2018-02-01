import json
import sys


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

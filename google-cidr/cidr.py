"""
Updates a customer managed VPC prefix list with the valid Google service CIDR
ranges.  These are determined by retrieving Google"s service CIDR range and
subtracting the Google Cloud Platform CIDR ranges.

Adapted from Google"s CIDR tool:
https://github.com/GoogleCloudPlatform/networking-tools-python/tree/main/tools/cidr
"""
import json
import logging
from os import environ
from urllib.request import urlopen
from urllib.error import HTTPError

import boto3

IPRANGE_URLS = {
    "goog": environ.get(
        "GOOGLE_SERVICE_CIDR_URL", "https://www.gstatic.com/ipranges/goog.json"
    ),
    "cloud": environ.get(
        "GOOGLE_CLOUD_CIDR_URL", "https://www.gstatic.com/ipranges/cloud.json"
    ),
}

PREFIX_LIST_ID = environ.get("PREFIX_LIST_ID")


def read_url(url):
    """Reads data from a URL and returns a JSON object."""
    try:
        return json.loads(urlopen(url).read())
    except (IOError, HTTPError):
        logging.error("ERROR: Invalid HTTP response from %s", url)
    except json.decoder.JSONDecodeError:
        logging.error("ERROR: Could not parse HTTP response from %s", url)

    return {}


def get_data(link):
    """Returns a list of CIDRs from a Google IP ranges JSON object."""
    cidrs = set([])
    data = read_url(link)

    if data:
        logging.info("%s published: %s", link, data.get("creationTime"))
        for elem in data["prefixes"]:
            if "ipv4Prefix" in elem:
                cidrs.add(elem.get("ipv4Prefix"))

    return cidrs


def get_google_cidrs(iprange_urls):
    """Returns a list of Google service CIDR ranges"""
    cidrs = {group: get_data(link) for group, link in iprange_urls.items()}
    return cidrs["goog"] - cidrs["cloud"]


def get_prefix_list_version(ec2_client, prefix_list_id):
    """Returns the version of the prefix list"""
    response = ec2_client.describe_managed_prefix_lists(
        PrefixListIds=[
            prefix_list_id,
        ]
    )
    return response["PrefixLists"][0]["Version"]


def get_prefix_list_entries(ec2_client, prefix_list_id, version):
    """Returns the entries of the prefix list"""
    response = ec2_client.get_managed_prefix_list_entries(
        MaxResults=100, PrefixListId=prefix_list_id, TargetVersion=version
    )
    return [e["Cidr"] for e in response["Entries"]]


def modify_managed_prefix_list(
    ec2_client, prefix_list_id, version, google_cidrs, entries
):
    """Updates the prefix list with the Google service CIDR ranges"""
    entries_to_add = set(google_cidrs) - set(entries)
    entries_to_remove = set(entries) - set(google_cidrs)
    if entries_to_add or entries_to_remove:
        logging.info("Adding entries: %s", entries_to_add)
        logging.info("Removing entries: %s", entries_to_remove)
        ec2_client.modify_managed_prefix_list(
            PrefixListId=prefix_list_id,
            CurrentVersion=version,
            AddEntries=[{"Cidr": e} for e in entries_to_add],
            RemoveEntries=[{"Cidr": e} for e in entries_to_remove],
        )
    else:
        logging.info("No changes to prefix list")


def get_boto_client(client_type):
    """Returns a boto3 client of the given type"""
    return boto3.client(client_type)


def handler():
    """Retrieves the list of public Google service CIDR ranges"""
    google_cidrs = get_google_cidrs(IPRANGE_URLS)

    if len(google_cidrs) == 0:
        logging.error("ERROR: No Google service CIDR ranges found")
        return {"statusCode": 404, "body": "No Google CIDRs found"}

    ec2_client = get_boto_client("ec2")
    version = get_prefix_list_version(ec2_client, PREFIX_LIST_ID)
    entries = get_prefix_list_entries(ec2_client, PREFIX_LIST_ID, version)
    modify_managed_prefix_list(
        ec2_client, PREFIX_LIST_ID, version, google_cidrs, entries
    )

    return {"statusCode": 200, "body": "Prefix list updated"}


if __name__ == "__main__":
    handler()

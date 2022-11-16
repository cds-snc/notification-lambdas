import pytest
import cidr
import sys

from unittest.mock import call, MagicMock, patch


@patch("cidr.read_url")
def test_get_data(mock_read_url):
    mock_read_url.return_value = {
        "creationTime": "2021-10-15T10:00:00Z",
        "prefixes": [
            {
                "ipv4Prefix": "1.2.3.4/32",
            },
            {
                "ipv4Prefix": "2.3.4.5/16",
            },
        ],
    }
    assert cidr.get_data("https://hobbits.com") == {"1.2.3.4/32", "2.3.4.5/16"}
    mock_read_url.assert_called_once_with("https://hobbits.com")


@patch("cidr.read_url")
def test_get_data_nothing(mock_read_url):
    mock_read_url.return_value = {
        "creationTime": "2021-10-15T10:00:00Z",
        "prefixes": [],
    }
    assert cidr.get_data("https://hobbits.com") == set()
    mock_read_url.assert_called_once_with("https://hobbits.com")


@patch("cidr.read_url")
def test_get_google_cidrs(mock_read_url):
    mock_read_url.side_effect = [
        {
            "creationTime": "2021-10-15T10:00:00Z",
            "prefixes": [
                {
                    "ipv4Prefix": "1.2.3.4/32",
                },
                {
                    "ipv4Prefix": "2.3.4.5/16",
                },
                {
                    "ipv4Prefix": "1.3.3.8/24",
                },
            ],
        },
        {
            "creationTime": "2021-10-15T10:00:00Z",
            "prefixes": [
                {
                    "ipv4Prefix": "1.3.3.8/24",
                },
                {
                    "ipv4Prefix": "5.6.7.8/16",
                },
            ],
        },
    ]
    iprange_urls = {"goog": "https://goog.com", "cloud": "https://cloud.com"}
    assert cidr.get_google_cidrs(iprange_urls) == {"1.2.3.4/32", "2.3.4.5/16"}
    mock_read_url.assert_has_calls(
        [
            call("https://goog.com"),
            call("https://cloud.com"),
        ]
    )


@patch("cidr.boto3")
def test_get_boto_client(mock_boto3):
    mock_boto3.client.return_value = "client"
    assert cidr.get_boto_client("ec2") == "client"
    mock_boto3.client.assert_called_once_with("ec2")

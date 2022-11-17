import pytest
import cidr

from unittest.mock import call, MagicMock, patch


@patch("cidr.urlopen")
def test_read_url(mock_urlopen):
    mock_urlopen.return_value.read.return_value = b'{"foo": "bar"}'
    assert cidr.read_url("http://example.com") == {"foo": "bar"}
    mock_urlopen.assert_called_once_with("http://example.com")


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


def test_get_prefix_list_version():
    ec2_client = MagicMock(return_value={"PrefixLists": [{"Version": 1}]})
    ec2_client.describe_managed_prefix_lists.return_value = {
        "PrefixLists": [{"Version": 42}]
    }
    assert cidr.get_prefix_list_version(ec2_client, "pl-12345678") == 42
    ec2_client.describe_managed_prefix_lists.assert_called_once_with(
        PrefixListIds=["pl-12345678"]
    )


def test_get_prefix_list_entries():
    ec2_client = MagicMock()
    ec2_client.get_managed_prefix_list_entries.return_value = {
        "Entries": [
            {
                "Cidr": "1.2.3.4/32",
            },
            {
                "Cidr": "66.55.44.33/32",
            },
        ]
    }
    assert cidr.get_prefix_list_entries(ec2_client, "pl-12345678", "42") == [
        "1.2.3.4/32",
        "66.55.44.33/32",
    ]
    ec2_client.get_managed_prefix_list_entries.assert_called_once_with(
        MaxResults=100, PrefixListId="pl-12345678", TargetVersion="42"
    )


def test_modify_managed_prefix_list():
    ec2_client = MagicMock()
    ec2_client.modify_managed_prefix_list.return_value = "success"
    cidr.modify_managed_prefix_list(
        ec2_client,
        "pl-12345678",
        "42",
        ["9.8.7.6/32", "8.7.6.5/16"],
        ["9.8.7.6/32", "1.2.3.4/24"],
    )

    ec2_client.modify_managed_prefix_list.assert_called_once_with(
        PrefixListId="pl-12345678",
        CurrentVersion="42",
        AddEntries=[{"Cidr": "8.7.6.5/16"}],
        RemoveEntries=[{"Cidr": "1.2.3.4/24"}],
    )


@patch("cidr.get_google_cidrs")
@patch("cidr.get_boto_client")
@patch("cidr.get_prefix_list_version")
@patch("cidr.get_prefix_list_entries")
@patch("cidr.modify_managed_prefix_list")
@patch("cidr.PREFIX_LIST_ID", "pl-1234567890")
def test_handler(
    mock_modify_managed_prefix_list,
    mock_get_prefix_list_entries,
    mock_get_prefix_list_version,
    mock_get_boto_client,
    mock_get_google_cidrs,
):
    mock_get_google_cidrs.return_value = set(["1.2.3.4/32"])
    mock_get_boto_client.return_value = "client"
    mock_get_prefix_list_version.return_value = "42"
    mock_get_prefix_list_entries.return_value = ["2.3.4.5/32"]

    assert cidr.handler() == {"statusCode": 200, "body": "Prefix list updated"}

    mock_get_boto_client.assert_called_once_with("ec2")
    mock_get_prefix_list_version.assert_called_once_with("client", "pl-1234567890")
    mock_get_prefix_list_entries.assert_called_once_with(
        "client", "pl-1234567890", "42"
    )
    mock_modify_managed_prefix_list.assert_called_once_with(
        "client", "pl-1234567890", "42", set(["1.2.3.4/32"]), ["2.3.4.5/32"]
    )


@patch("cidr.get_google_cidrs")
def test_handler_no_cidrs(mock_get_google_cidrs):
    mock_get_google_cidrs.return_value = set()
    assert cidr.handler() == {"statusCode": 404, "body": "No Google CIDRs found"}


@patch("cidr.boto3")
def test_get_boto_client(mock_boto3):
    mock_boto3.client.return_value = "client"
    assert cidr.get_boto_client("ec2") == "client"
    mock_boto3.client.assert_called_once_with("ec2")

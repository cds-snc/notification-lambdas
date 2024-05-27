import pytest
import requests
from system_status.determine_web_status import determine_site_status


class TestSiteStatus:

    @pytest.mark.parametrize("site, threshold", [("http://site-1.example.com", 400)])
    @pytest.mark.parametrize(
        "response_time, expected_status", [(100, "up"), (500, "degraded")]
    )
    def test_determine_site_status(
        self, mocker, site, threshold, response_time, expected_status
    ):
        # mock the call to check_response_time()
        mocker.patch(
            "system_status.determine_web_status.check_response_time",
            return_value=response_time,
        )

        result = determine_site_status(site, threshold)

        assert result == expected_status

    def test_determine_site_status_down(self, mocker):
        mocker.patch(
            "system_status.determine_web_status.check_response_time",
            side_effect=requests.exceptions.ConnectionError,
        )
        result = determine_site_status("http://site-1.example.com", 400)

        assert result == "down"

    @pytest.mark.parametrize("site, threshold", [("http://site-1.example.com", 400)])
    @pytest.mark.parametrize("response_time", (401, 500))
    def test_logging_determine_site_status_logs_on_site_degraded(
        self, mocker, site, threshold, response_time, caplog
    ):
        # mock the call to check_response_time()
        mocker.patch(
            "system_status.determine_web_status.check_response_time",
            return_value=response_time,
        )

        caplog.set_level("INFO")
        determine_site_status(site, threshold)

        assert "[system_status_site]: site {} is degraded".format(site) in caplog.text

    @pytest.mark.parametrize("site, threshold", [("http://site-1.example.com", 400)])
    def test_logging_determine_site_status_logs_on_site_down_connection_error(
        self, mocker, site, threshold, caplog
    ):
        mocker.patch(
            "system_status.determine_web_status.check_response_time",
            side_effect=requests.exceptions.ConnectionError,
        )

        caplog.set_level("ERROR")
        determine_site_status(site, threshold)

        assert (
            "[system_status_site]: site {} is down: Error connecting to url".format(
                site
            )
            in caplog.text
        )

    @pytest.mark.parametrize("site, threshold", [("http://site-1.example.com", 400)])
    def test_logging_determine_site_status_logs_on_site_down_other_error(
        self, mocker, site, threshold, caplog
    ):
        mocker.patch(
            "system_status.determine_web_status.check_response_time",
            side_effect=requests.exceptions.TooManyRedirects,
        )

        caplog.set_level("ERROR")
        determine_site_status(site, threshold)

        assert (
            "[system_status_site]: site {} is down: unexpected error".format(site)
            in caplog.text
        )

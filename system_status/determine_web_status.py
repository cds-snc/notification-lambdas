import logging
import requests


def determine_site_status(url, threshold):
    try:
        api_response_time = check_response_time(url)
        site_status = "up" if api_response_time <= threshold else "degraded"

        if site_status == "degraded":
            logging.info(
                "[system_status_site]: site {} is degraded: {}".format(
                    url, api_response_time
                )
            )

    except requests.exceptions.ConnectionError as e:
        logging.error(
            "[system_status_site]: site {} is down: Error connecting to url: {}".format(
                url, e
            )
        )
        site_status = "down"

    except Exception as e:
        logging.error(
            "[system_status_site]: site {} is down: unexpected error: {}".format(url, e)
        )
        site_status = "down"

    return site_status


def check_response_time(url):
    response = requests.get(url)
    return response.elapsed.total_seconds() * 1000

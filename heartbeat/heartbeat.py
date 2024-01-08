"""
Code to keep the lambda API alive.
"""
import ast
import os
from typing import List

from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_utils.system_status import TEMPLATES

API_KEY: str = os.getenv("heartbeat_api_key", "")
# As we can't pass in a list to env var, we pass a str and convert it.
BASE_URL: List[str] = ast.literal_eval(os.getenv("heartbeat_base_url"))  # type: ignore
EMAIL_ADDRESS = "success@simulator.amazonses.com"
# AWS Success test number:
# https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-simulator.html
PHONE_NUMBER = os.getenv("heartbeat_sms_number", "")


def handler(event, context):  # pylint: disable=unused-argument
    """
    Parses a dict of templates from notifications_utils and
    sends Bulk, Normal and Priority Email and SMS notifications.
    In addition to simply being a heartbeat, it provides data
    used to determine the up/down status of Notify.
    """
    if not API_KEY:
        print("Variable API_KEY is missing")
    if not BASE_URL:
        print("Variable BASE_URL is missing")

    for base_url in BASE_URL:
        notifications_client = NotificationsAPIClient(API_KEY, base_url=base_url)
        try:
            tidy_nest = (
                (template_type, priority, template_id)
                for template_type, templates in TEMPLATES.items()
                for priority, template_id in templates.items()
            )

            for template_type, priority, template_id in tidy_nest:
                if template_type and priority and template_id:
                    if template_type == "email":
                        notifications_client.send_email_notification(
                            email_address=EMAIL_ADDRESS, template_id=template_id
                        )
                        print(
                            f"{template_type.capitalize()} has been sent by {base_url}!"
                        )
                    elif template_type == "sms":
                        notifications_client.send_sms_notification(
                            phone_number=PHONE_NUMBER, template_id=template_id
                        )
                        print(f"{template_type.upper()} has been sent by {base_url}!")
                else:
                    print(
                        f"""Required parameters missing:
                        template_type: {template_type},
                        priority: {priority},
                        template_id: {template_id}
                        """
                    )
        except HTTPError as http_e:
            print(
                f"Could not send heartbeat: status={http_e.status_code}, msg={http_e.message}"
            )
            raise

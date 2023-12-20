"""
Code to keep the lambda API alive.
"""
import ast
import os
import uuid
from typing import List

from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient

API_KEY: str = os.getenv("heartbeat_api_key", "")
# As we can't pass in a list to env var, we pass a str and convert it.
BASE_URL: List[str] = ast.literal_eval(os.getenv("heartbeat_base_url"))  # type: ignore
EMAIL_ADDRESS = "success@simulator.amazonses.com"
PHONE_NUMBER = "+14254147755" # AWS Success test number: https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-simulator.html
EMAIL_BULK_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_email_bulk_template_id") # type: ignore
EMAIL_NORMAL_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_email_normal_template_id") # type: ignore
EMAIL_PRIORITY_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_email_priority_template_id") # type: ignore
SMS_BULK_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_sms_bulk_template_id") # type: ignore
SMS_NORMAL_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_sms_normal_template_id") # type: ignore
SMS_PRIORITY_TEMPLATE_ID: uuid.UUID = os.getenv("heartbeat_sms_priority_template_id") # type: ignore

def handler(event, context):
    if not BASE_URL:
        print("Variable BASE_URL is missing")
    if not API_KEY:
        print("Variable API_KEY is missing")
    if not EMAIL_BULK_TEMPLATE_ID:
        print("Variable EMAIL_BULK_TEMPLATE_ID is missing")
    if not EMAIL_NORMAL_TEMPLATE_ID:
        print("Variable EMAIL_NORMAL_TEMPLATE_ID is missing")
    if not EMAIL_PRIORITY_TEMPLATE_ID:
        print("Variable EMAIL_PRIORITY_TEMPLATE_ID is missing")
    if not SMS_BULK_TEMPLATE_ID:
        print("Variable SMS_BULK_TEMPLATE_ID is missing")
    if not SMS_NORMAL_TEMPLATE_ID:
        print("Variable SMS_NORMAL_TEMPLATE_ID is missing")
    if not SMS_PRIORITY_TEMPLATE_ID:
        print("Variable SMS_PRIORITY_TEMPLATE_ID is missing")
    for base_url in BASE_URL:
        notifications_client = NotificationsAPIClient(API_KEY, base_url=base_url)
        try:
            notifications_client.send_email_notification(email_address=EMAIL_ADDRESS, template_id=EMAIL_BULK_TEMPLATE_ID)
            notifications_client.send_email_notification(email_address=EMAIL_ADDRESS, template_id=EMAIL_NORMAL_TEMPLATE_ID)
            notifications_client.send_email_notification(email_address=EMAIL_ADDRESS, template_id=EMAIL_PRIOIRTY_TEMPLATE_ID)
            notifications_client.send_sms_notification(phone_nummber=PHONE_NUMBER, template_id=SMS_BULK_TEMPLATE_ID)
            notifications_client.send_sms_notification(phone_nummber=PHONE_NUMBER, template_id=SMS_NORMAL_TEMPLATE_ID)
            notifications_client.send_sms_notification(phone_nummber=PHONE_NUMBER, template_id=SMS_PRIOIRTY_TEMPLATE_ID)
            print("Email has been sent by {}!".format(base_url))
        except HTTPError as e:
            print(f"Could not send heartbeat: status={e.status_code}, msg={e.message}")
            raise

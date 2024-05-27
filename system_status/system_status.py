import boto3
import json
import logging
import os
import sqlalchemy
from botocore.exceptions import ClientError

from database_queries import (
    low_template_result_group1,
    low_template_result_group2,
    medium_template_result_group1,
    medium_template_result_group2,
    high_template_result,
)
from determine_db_status import determine_status
from determine_web_status import determine_site_status

THRESHOLDS = {
    "api": 400,  # 400ms
    "admin": 400,  # 400ms
}

logging.getLogger().setLevel("INFO")

URL_API = os.getenv("system_status_api_url")
URL_ADMIN = os.getenv("system_status_admin_url")
DB_CONN_STRING = os.getenv("sqlalchemy_database_reader_uri")
BUCKET_NAME = os.getenv("system_status_bucket_name")


def handler(event, context):
    logging.info("Starting system-status lambda")
    logging.info("Received event: {}".format(event))

    ## Section 1: Get Email and SMS status information from the database
    try:
        # connect to postgres db
        db = sqlalchemy.create_engine(DB_CONN_STRING, future=True)
        logging.info("connected to db")
        with db.connect() as conn:
            high = high_template_result(conn)
            medium1 = medium_template_result_group1(conn)
            medium2 = medium_template_result_group2(conn)
            low1 = low_template_result_group1(conn)
            low2 = low_template_result_group2(conn)
            email_data = {
                "high": high["email"]["status"] if "email" in high else {},
                "medium1": medium1["email"]["status"] if "email" in medium1 else {},
                "medium2": medium2["email"]["status"] if "email" in medium2 else {},
                "low1": low1["email"]["status"] if "email" in low1 else {},
                "low2": low2["email"]["status"] if "email" in low2 else {},
            }
            sms_data = {
                "high": high["sms"]["status"] if "sms" in high else {},
                "medium1": medium1["sms"]["status"] if "sms" in medium1 else {},
                "medium2": medium2["sms"]["status"] if "sms" in medium2 else {},
                "low1": low1["sms"]["status"] if "sms" in low1 else {},
                "low2": low2["sms"]["status"] if "sms" in low2 else {},
            }
            logging.info(
                "Data from db: {}".format({"email": email_data, "sms": sms_data})
            )

    except sqlalchemy.exc.OperationalError as e:
        logging.error("System-status lambda (db connection): {}".format(e))

        return {"statusCode": 500}
    except Exception as e:
        logging.error(
            "System-status lambda (db connection): unknown error: {}".format(e)
        )

        return {"statusCode": 500}

    ## Section 2: Determine the status of the email and sms services based on the data from the database
    try:
        email_status = determine_status(
            email_data["high"],
            email_data["medium1"],
            email_data["medium2"],
            email_data["low1"],
            email_data["low2"],
        )
        sms_status = determine_status(
            sms_data["high"],
            sms_data["medium1"],
            sms_data["medium2"],
            sms_data["low1"],
            sms_data["low2"],
        )
        logging.info("Email status: {}".format(email_status))
        logging.info("SMS status: {}".format(sms_status))
    except Exception as e:
        logging.error(
            "System-status lambda error (determine_notification_status): {}".format(e)
        )
        return {"statusCode": 500}

    # Section 3: Check api and admin response times

    api_status = determine_site_status(URL_API, THRESHOLDS["api"])
    admin_status = determine_site_status(URL_ADMIN, THRESHOLDS["admin"])
    logging.info("API status: {}".format(api_status))
    logging.info("Admin status: {}".format(admin_status))

    # Section 4: Push statuses to s3 bucket
    try:
        s3_client = boto3.client("s3")
        bucket_name = BUCKET_NAME
        object_key = "response.json"
        status_data = [
            {"id": "api", "status": api_status},
            {"id": "admin", "status": admin_status},
            {"id": "email", "status": email_status},
            {"id": "sms", "status": sms_status},
        ]
        s3_client.put_object(
            Body=json.dumps(status_data), Bucket=bucket_name, Key=object_key
        )
    except ClientError as e:
        logging.error("Error uploading status data to s3: {}".format(e))
    else:
        logging.info(
            "Pushed status data to s3: {}".format(
                {
                    "api": api_status,
                    "admin": admin_status,
                    "email": email_status,
                    "sms": sms_status,
                }
            )
        )
    finally:
        return {
            "body": {
                "api": api_status,
                "admin": admin_status,
                "email": email_status,
                "sms": sms_status,
            },
            "statusCode": 200,
        }

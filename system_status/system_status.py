import boto3
import json
import logging
import os
import sqlalchemy

from notifications_utils.system_status import determine_notification_status, determine_site_status, TEMPLATES, THRESHOLDS

URL_API = os.getenv("system_status_api_url")
URL_ADMIN = os.getenv("system_status_admin_url")
DB_CONN_STRING = os.getenv("sqlalchemy_database_reader_uri")
BUCKET_NAME = os.getenv("system_status_bucket_name")

# get list of UUIDS from TEMPLATES
TEMPLATE_IDS = ",".join(["'{}'".format(x) for x in [template_id for notification_type in TEMPLATES for template_id in TEMPLATES[notification_type].values()]])


# Build SQL query
SQL = ("SELECT      template_id,  AVG(extract(epoch from (n.sent_at - n.created_at)))*1000  as time_to_send "
        "FROM       notifications n "
        "WHERE      JOB_ID is null "
        "AND        template_id in ({}) "
        "AND        created_at >= NOW() - INTERVAL '5 MINUTES' "
        "GROUP BY   template_id ".format(TEMPLATE_IDS))

def handler(event, context):
    logging.getLogger().setLevel('INFO')
    try:
        # connect to postgres db
        db = sqlalchemy.create_engine(DB_CONN_STRING, future=True)
        with db.connect() as conn:
            dbresults = conn.execute(sqlalchemy.sql.text(SQL))
            conn.commit()    

    except sqlalchemy.exc.OperationalError as e:
        logging.error("System-status lambda (db connection): {}".format(e))

        return {
            'statusCode': 500
        }
    except Exception as e:
        logging.error("System-status lambda (db connection): unknown error: {}".format(e))

        return {
            'statusCode': 500
        }
    
    try:
        (email_status, sms_status) = determine_notification_status(dbresults)
    except Exception as e:
        logging.error("System-status lambda error (determine_notification_status): {}".format(e))
        return {
            'statusCode': 500
        }

    # check api and admin response times
    api_status = determine_site_status(URL_API, THRESHOLDS['api'])
    admin_status = determine_site_status(URL_ADMIN, THRESHOLDS['admin'])
    
    # push statuses to s3 bucket
    s3_client = boto3.client('s3')
    bucket_name = BUCKET_NAME
    object_key = 'response.json'
    status_data = [
        {
            'id': 'api',
            'status': api_status
        },
        {
            'id': 'admin',
            'status': admin_status
        },
        {
            'id': 'email',
            'status': email_status
        },
        {
            'id': 'sms',
            'status': sms_status
        }
    ]
    s3_client.put_object(
        Body=json.dumps(status_data),
        Bucket=bucket_name,
        Key=object_key
    )

    return {
        'body': {
            'api': api_status,
            'admin': admin_status,
            'email': email_status,
            'sms': sms_status
        },
        'statusCode': 200
    }

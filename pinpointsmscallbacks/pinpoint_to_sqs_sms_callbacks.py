import gzip
import json
import base64
import boto3
import uuid
import os
from urllib.parse import urlparse
from botocore.exceptions import BotoCoreError, ClientError, ParamValidationError


def to_queue(queue, message):
    task = {
        "task": "process-pinpoint-result",
        "id": str(uuid.uuid4()),
        "args": [
            {
                "Message": message
            }
        ],
        "kwargs": {},
        "retries": 0,
        "eta": None,
        "expires": None,
        "utc": True,
        "callbacks": None,
        "errbacks": None,
        "timelimit": [
            None,
            None
        ],
        "taskset": None,
        "chord": None
    }
    print(f'Sending task {task}')
    envelope = {
        "body": base64.b64encode(bytes(json.dumps(task), 'utf-8')).decode("utf-8"),
        "content-encoding": "utf-8",
        "content-type": "application/json",
        "headers": {},
        "properties": {
            "reply_to": str(uuid.uuid4()),
            "correlation_id": str(uuid.uuid4()),
            "delivery_mode": 2,
            "delivery_info": {
                "priority": 0,
                "exchange": "default",
                "routing_key": "delivery-receipts"
            },
            "body_encoding": "base64",
            "delivery_tag": str(uuid.uuid4())
        }
    }
    msg = base64.b64encode(bytes(json.dumps(envelope), 'utf-8')).decode("utf-8")
    queue.send_message(MessageBody=msg)


def get_queue_url():
    return os.environ.get("SQS_QUEUE_URL", "").strip()


def get_sqs_resource(queue_url):
    if queue_url:
        hostname = urlparse(queue_url).hostname or ""
        hostname_parts = hostname.split('.')

        if len(hostname_parts) >= 4 and hostname_parts[0] == "sqs":
            return boto3.resource('sqs', region_name=hostname_parts[1])

    return boto3.resource('sqs')


def get_queue(sqs, sqs_queue_url):

    if sqs_queue_url:
        try:
            queue = sqs.Queue(sqs_queue_url)
            queue.attributes
            return queue
        except (BotoCoreError, ClientError, ParamValidationError, ValueError) as error:
            print(f"Falling back to default SQS queue name because SQS_QUEUE_URL is unusable: {error}")

    return sqs.get_queue_by_name(QueueName="eks-notification-canada-cadelivery-receipts")


def lambda_handler(event, context):
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)

    log_events = payload['logEvents']

    sqs_queue_url = get_queue_url()
    sqs = get_sqs_resource(sqs_queue_url)
    queue = get_queue(sqs, sqs_queue_url)

    for log_event in log_events:
        print(f'LogEvent: {log_event}')
        to_queue(queue, log_event['message'])

    return {
        'statusCode': 200
    }

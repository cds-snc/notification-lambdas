import time
import base64
import json
import boto3
import uuid

from botocore.client import Config


config = Config(connect_timeout=15, retries={'max_attempts': 3})
sqs = boto3.client('sqs', config=config)
queue_url = sqs.get_queue_url(QueueName='eks-notification-canada-cadelivery-receipts')['QueueUrl']

def lambda_handler(event, context):
    start_time = time.time()
    records = event.get("Records", [])

    if not records:
        print("No SES receipt records found in the SQS event message.")
        return {
            "statusCode": 200
        }
    print(f"[batch-lambda] - records: {records}")
    print(f"Task has begun, batch processing {len(records)} receipts.")

    task = {
        "task": "process-ses-result",
        "id": str(uuid.uuid4()),
        "args": [
            {
                "Messages": [receipt["body"] for receipt in records]
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
    msg = json.dumps(envelope)
    print(f"[batch-lambda] - Message to queue: {msg}")
    sqs.send_message(QueueUrl=queue_url, MessageBody=msg)
    print(f"{len(records)} records have moved to call process-ses-result")

    print("Task has ended")
    print(f"[batch-lambda] - Execution time: {time.time() - start_time} seconds")

    return {
        'statusCode': 200
    }
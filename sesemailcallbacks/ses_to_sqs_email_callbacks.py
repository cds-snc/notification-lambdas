import os
import base64
import json
import boto3
import uuid

from botocore.client import Config

BATCH_INSERTION_CHUNK_SIZE = os.getenv("BATCH_INSERTION_CHUNK_SIZE", 10)

def lambda_handler(event, context):
    config = Config(connect_timeout=15, retries={'max_attempts': 3})
    sqs = boto3.resource('sqs', config=config)
    queue = sqs.get_queue_by_name(
        QueueName='eks-notification-canada-cadelivery-receipts'
    )
    receipt_chunks = list(chunked(event["Records"], BATCH_INSERTION_CHUNK_SIZE))
    print("Queue {}".format(queue))
    print(f"Task has begun, processing {len(event['Records'])} receipts in chunks of {BATCH_INSERTION_CHUNK_SIZE}. Total chunks: {len(receipt_chunks)}")

    for i, receipt_chunk in receipt_chunks:
        task = {
            "task": "process-ses-result",
            "id": str(uuid.uuid4()),
            "args": [
                {
                    "Messages": [receipt["Sns"]["Message"] for receipt in receipt_chunk]
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
        print(f"[DEBUG] - Task: {json.dumps(task)}")
        print(f"[DEBUG] - Message sent to call process-ses-result: {msg}")
        queue.send_message(MessageBody=msg)
        print(f"Batch #{i} - {BATCH_INSERTION_CHUNK_SIZE} records have moved to call process-ses-result")
    print("Task has ended")

    return {
        'statusCode': 200
    }

def chunked(items, chunk_size):
    """Break a list into chunks of the specified size."""
    for i in range(0, len(items), chunk_size):
        yield i//chunk_size, items[i:i + chunk_size]
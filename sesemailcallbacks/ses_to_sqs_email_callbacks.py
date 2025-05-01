"""
Code to process SES receipt messages from SQS and send them to a Celery task queue.
"""

import base64
import json
import uuid
import boto3

from botocore.client import Config


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """
    Prepares a batch of SES receipt messages received from an SQS buffer queue and
    packages them into a Celery task envelope and sends them to the delivery-receipts
    queue for process_ses_results to consume.
    """
    config = Config(connect_timeout=15, retries={"max_attempts": 3})
    sqs = boto3.resource("sqs", config=config)
    queue = sqs.get_queue_by_name(
        QueueName="eks-notification-canada-cadelivery-receipts"
    )

    records = event.get("Records", [])

    if not records:
        print("No SES receipt records found in the SQS event message.")
        return {"statusCode": 200}
    print(f"[batch-lambda] - records: {records}")
    print(
        f"[batch-lambda] - Raw receipt bodies: {[receipt["body"] for receipt in records]}"
    )
    print(
        f"[batch-lambda] - Json receipt bodies: {[json.loads(receipt["body"]) for receipt in records]}"
    )  # pylint: disable=line-too-long
    receipt_messages = [json.loads(receipt["body"]) for receipt in records]

    print(f"Task has begun, batch processing {len(records)} receipts.")

    task = {
        "task": "process-ses-result",
        "id": str(uuid.uuid4()),
        "args": [{"Messages": receipt_messages}],
        "kwargs": {},
        "retries": 0,
        "eta": None,
        "expires": None,
        "utc": True,
        "callbacks": None,
        "errbacks": None,
        "timelimit": [None, None],
        "taskset": None,
        "chord": None,
    }
    envelope = {
        "body": base64.b64encode(bytes(json.dumps(task), "utf-8")).decode("utf-8"),
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
                "routing_key": "delivery-receipts",
            },
            "body_encoding": "base64",
            "delivery_tag": str(uuid.uuid4()),
        },
    }
    msg = json.dumps(envelope)
    print(f"[batch-lambda] - Message to queue: {msg}")
    queue.send_message(MessageBody=msg)
    print(f"{len(receipt_messages)} records have moved to call process-ses-result")

    print("Task has ended")

    return {"statusCode": 200}

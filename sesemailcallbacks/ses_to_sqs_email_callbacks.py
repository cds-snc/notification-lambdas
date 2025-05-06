import base64
import json
import boto3
import uuid

from botocore.client import Config


def lambda_handler(event, context):
    config = Config(connect_timeout=15, retries={'max_attempts': 3})
    sqs = boto3.resource('sqs', config=config)
    queue = sqs.get_queue_by_name(
        QueueName='eks-notification-canada-cadelivery-receipts'
    )
    print("Queue {}".format(queue))
    print("Task has begun")
    for record in event["Records"]:
        task = {
            "task": "process-ses-result",
            "id": str(uuid.uuid4()),
            "args": [
                {
                    "Message": record["Sns"]["Message"]
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
        msg = base64.b64encode(bytes(json.dumps(envelope), 'utf-8')).decode("utf-8")
        queue.send_message(MessageBody=msg)
        print("Record has moved to call process-ses-result")
    print("Task has ended")


    return {
        'statusCode': 200
    }

import os
import json
import base64
import uuid
import boto3
import pytest
from moto import mock_sqs
from ses_to_sqs_email_callbacks import lambda_handler  # Import your Lambda function


def sns_event(num_records=10):
    """Generate a mock SQS event message with the specified number of records."""

    record = {
        "messageId": str(uuid.uuid4()),
        "Timestamp" : "2025-04-15T15:55:22.211Z",
        "body": json.dumps({"Type" : "Notification","MessageId": "uuid", "Message": {"notificationType": "Delivery", "mail": {"timestamp":"2025-04-15T15:55:21.620Z","messageId":"010d01963a298494-470d5161-a44d-4a3e-9582-e0fa18a886fc-000000"},"delivery":{"timestamp":"2025-04-15T15:55:22.176Z"}}})
    }
    messages = {
        "Records": [record for _ in range(num_records)] if num_records > 0 else []
    }

    return messages


def test_lambda_handles_no_records():

    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    # Use mock_sqs as a context manager
    with mock_sqs() as sqs:
        event = sns_event(0)
        # Create the queue before calling lambda
        sqs = boto3.resource("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="eks-notification-canada-cadelivery-receipts")

        # Call lambda handler
        response = lambda_handler(event, sqs)

        # Ensure Lambda executed successfully
        assert response["statusCode"] == 200

        # Check that no messages were sent to SQS
        messages = queue.receive_messages()
        assert len(messages) == 0


@pytest.mark.parametrize("num_records", [1, 5, 10, 11])
def test_lambda_batches_correctly(num_records):
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    # Use mock_sqs as a context manager
    with mock_sqs() as sqs:
        event = sns_event(num_records)
        # Create the queue before calling lambda
        sqs = boto3.resource("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="eks-notification-canada-cadelivery-receipts")

        # Call lambda handler
        response = lambda_handler(event, sqs)

        # Ensure Lambda executed successfully
        assert response["statusCode"] == 200

        # Retrieve messages from the queue
        messages = queue.receive_messages()

        # Verify message structure
        for msg in messages:
            body_content = json.loads(msg.body)
            assert "body" in body_content
            decoded_body = json.loads(base64.b64decode(body_content["body"]))
            assert "args" in decoded_body
            assert len(json.loads(base64.b64decode(body_content["body"]))["args"][0]["Messages"]) == num_records


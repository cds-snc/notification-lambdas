import os
import json
import base64
import uuid
import boto3
import pytest
from moto import mock_sqs
from ses_to_sqs_email_callbacks import lambda_handler  # Import your Lambda function

@pytest.fixture
def sns_event():
    """Generate a mock SNS event with 25 records"""

    record = {
        "messageId": str(uuid.uuid4()),
        "Timestamp" : "2025-04-15T15:55:22.211Z",
        "body": json.dumps({"Type" : "Notification","MessageId": "uuid", "Message": {"notificationType": "Delivery", "mail": {"timestamp":"2025-04-15T15:55:21.620Z","messageId":"010d01963a298494-470d5161-a44d-4a3e-9582-e0fa18a886fc-000000"},"delivery":{"timestamp":"2025-04-15T15:55:22.176Z"}}})
    }
    messages = {
        "Records": [record for _ in range(10)]
    }

    return messages


def test_lambda_batches_correctly(sns_event):
    """Test that Lambda batches messages and sends them to SQS"""
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    # Use mock_sqs as a context manager
    with mock_sqs() as sqs:
        # Create the queue before calling lambda
        sqs = boto3.resource("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="eks-notification-canada-cadelivery-receipts")

        # Call lambda handler
        response = lambda_handler(sns_event, sqs)

        # Ensure Lambda executed successfully
        assert response["statusCode"] == 200

        # Retrieve messages from the queue
        messages = []
        while response and len(messages) < 3:
            response = queue.receive_messages(MaxNumberOfMessages=10)
            messages.extend(response)

        # Check that messages were sent to SQS
        assert len(messages) == 1

        # Verify message structure
        for msg in messages:
            body_content = json.loads(msg.body)
            assert "body" in body_content
            decoded_body = json.loads(base64.b64decode(body_content["body"]))
            assert "args" in decoded_body
            assert len(json.loads(base64.b64decode(body_content["body"]))["args"][0]["Messages"]) == 10


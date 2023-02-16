# Purpose

This lambda gets the email receipt from AWS and then calls a task to update the notification in Notify's DB.

## Lambda Invocation

1. Email gets sent through Notify
2. The email receipt gets published to an SNS topic `ses-callback`
3. The ses_to_sqs_email_callbacks lambda has a receiver on the above SNS topic
4. The lambda takes the email receipt and sends it to a celery queue `eks-notification-canada-cadelivery-receipts` with a task `process-ses-result`

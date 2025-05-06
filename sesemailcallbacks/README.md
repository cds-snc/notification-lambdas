# Purpose

This lambda gets the email receipt from AWS and then calls a task to update the notification in Notify's DB.

## Lambda Invocation

1. Email gets sent through Notify
2. The email receipt gets published to an SNS topic `ses-callback`
3. The ses_to_sqs_email_callbacks lambda has a receiver on the above SNS topic
4. The lambda takes the email receipt and sends it to a celery queue `eks-notification-canada-cadelivery-receipts` with a task `process-ses-result`

## How it works
![PlantUML model](./ses-callback.png)

<!--
@startuml

title GC Notify SES Callbacks
:**SES** Delivers an email;
:**SES** publishes a delivery receipt notification to **ses-callback** SNS topic;
:**SNS** subscription invokes **ses_to_sqs_email_callbacks** lambda;
-> \n\n;
partition #Technology "ses_receiving_emails_inbound-to-lambda" {
  :Invokes Celery task **process-ses-result**;
}
-> \n;
partition #Technology "process-ses-result" {
  :Calls user-specified API endpoint with result;
  stop
}
@enduml
-->
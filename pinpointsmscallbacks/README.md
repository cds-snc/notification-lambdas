# Purpose

This lambda gets the Pinpoint receipt from AWS and then calls a task to update the notification in Notify's DB.

## Lambda Invocation

1. SMS gets sent through Notify
1. The SMS receipt written to 2 different cloudwatch log-groups: PinpointDirectPublishToPhoneNumber and PinpointDirectPublishToPhoneNumber/Failure
1. The pinpoint_to_sqs_sms_callbacks lambda is a subscription-filter on the above two log-groups.
1. The lambda takes the sms receipt and sends it to a celery queue `eks-notification-canada-cadelivery-receipts` with a task `process-pinpoint-result`


## How it works
![PlantUML model](./sms-callback.png)

<!--
@startuml

title GC Notify SMS Callbacks
:**Pinpoint** Delivers an SMS;
:SMS receipt is written to a **Cloudwatch** log;
:Cloudwatch subscription filter triggers  the **pinpoint-to-sqs-sms-callbacks** lambda;
-> \n\n;
partition #Technology "pinpoint-to-sqs-sms-callbacks" {
  :Invokes Celery task **process-pinpoint-result**;
}
-> \n;
partition #Technology "process-pinpoint-result" {
  :Calls user-specified API endpoint with result;
  stop
}
@enduml
-->
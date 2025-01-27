# Docker image for the SNS to SQS SMS callback the lambda API.

FROM public.ecr.aws/lambda/python:3.12

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY pinpointsmscallbacks/requirements_for_pinpoint_sms.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_pinpoint_sms.txt

# Copy function code
COPY pinpointsmscallbacks/pinpoint_to_sqs_sms_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "pinpoint_to_sqs_sms_callbacks.lambda_handler" ]

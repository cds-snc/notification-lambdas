# Docker image for the SNS to SQS SMS callback the lambda API.

FROM public.ecr.aws/lambda/python:3.9

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY snssmscallbacks/requirements_for_sns_sms.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_sns_sms.txt

# Copy function code
COPY snssmscallbacks/sns_to_sqs_sms_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "sns_to_sqs_sms_callbacks.lambda_handler" ]

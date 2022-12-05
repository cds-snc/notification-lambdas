# Docker image for the SES email callback the lambda API.

FROM public.ecr.aws/lambda/python:3.9

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY sesemailcallbacks/requirements_for_sqs_email.py ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_sqs_email.txt

# Copy function code
COPY sesemailcallbacks/ses_to_sqs_email_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_to_sqs_email_callbacks.lambda_handler" ]

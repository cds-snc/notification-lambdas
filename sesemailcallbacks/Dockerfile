# Docker image for the SES email callback the lambda API.
FROM public.ecr.aws/lambda/python:3.12
ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY requirements_for_sqs_email.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_sqs_email.txt

# Copy function code
COPY ses_to_sqs_email_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_to_sqs_email_callbacks.lambda_handler" ]
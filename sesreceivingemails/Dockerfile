# Docker image for the SES recieving emails hitting the lambda API.

FROM public.ecr.aws/lambda/python:3.12

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY sesreceivingemails/requirements_for_ses.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_ses.txt

# Copy function code
COPY sesreceivingemails/ses_receiving_emails.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_receiving_emails.lambda_handler" ]

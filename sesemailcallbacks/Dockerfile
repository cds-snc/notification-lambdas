# Docker image for the SES email callback the lambda API.
FROM public.ecr.aws/lambda/python:3.12

RUN apk add --no-cache ca-certificates && \
    sed -i \
      -e 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!&|' \
      /etc/ca-certificates.conf && \
    update-ca-certificates

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY requirements_for_sqs_email.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_sqs_email.txt

# Copy function code
COPY ses_to_sqs_email_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_to_sqs_email_callbacks.lambda_handler" ]
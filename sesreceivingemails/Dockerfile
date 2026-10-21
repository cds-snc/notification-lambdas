# Docker image for the SES recieving emails hitting the lambda API.

FROM public.ecr.aws/lambda/python:3.12

RUN dnf -y install ca-certificates p11-kit-trust && \
    trust extract --format=pem-bundle \
      --filter="pkcs11:object=emSign%20ECC%20Root%20CA%20-%20G3" \
      /etc/pki/ca-trust/source/blocklist/emSign_ECC_Root_CA_-_G3.pem && \
    update-ca-trust extract && \
    dnf clean all

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY requirements_for_ses.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r ${LAMBDA_TASK_ROOT}/requirements_for_ses.txt

# Copy function code
COPY ses_receiving_emails.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_receiving_emails.lambda_handler" ]

# Docker image for the SES recieving emails hitting the lambda API.

FROM public.ecr.aws/lambda/python:3.12

RUN dnf -y install ca-certificates p11-kit-trust && \
    d=/etc/pki/ca-trust/source/blocklist; [ -d $d ] || d=/etc/pki/ca-trust/source/blacklist; \
    trust extract --overwrite --format=pem-bundle \
      --filter='pkcs11:object=Comodo%20AAA%20Services%20root;type=cert' \
      $d/Comodo_AAA_Services_root.pem && \
    trust extract --overwrite --format=pem-bundle \
      --filter='pkcs11:object=emSign%20ECC%20Root%20CA%20-%20G3;type=cert' \
      $d/emSign_ECC_Root_CA_-_G3.pem && \
    update-ca-trust && \
    dnf clean all

ENV SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt \
    REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt \
    AWS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY requirements_for_ses.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r ${LAMBDA_TASK_ROOT}/requirements_for_ses.txt

# Copy function code
COPY ses_receiving_emails.py ${LAMBDA_TASK_ROOT}

CMD [ "ses_receiving_emails.lambda_handler" ]

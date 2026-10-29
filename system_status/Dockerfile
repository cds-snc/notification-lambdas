# Docker image for the system status lambda API.

FROM public.ecr.aws/lambda/python:3.12@sha256:3c249526505c4bf83ab74be5d4749b7705798b03effcd34c205c6a77d149c77e

RUN dnf -y install ca-certificates p11-kit-trust && \
    d=/etc/pki/ca-trust/source/blocklist; [ -d $d ] || d=/etc/pki/ca-trust/source/blacklist; \
    trust extract --overwrite --format=pem-bundle \
      --filter='pkcs11:object=Comodo%20AAA%20Services%20root;type=cert' \
      $d/Comodo_AAA_Services_root.pem && \
    update-ca-trust && \
    dnf clean all

ENV SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt \
    REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt \
    AWS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

ENV PYTHONDONTWRITEBYTECODE 1

RUN dnf -y install git
RUN dnf -y install libpq-devel
RUN dnf -y install gcc

# Install the function's dependencies
RUN ls -la
COPY requirements_for_system_status.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_system_status.txt

# Copy function code
COPY system_status.py ${LAMBDA_TASK_ROOT}
COPY database_queries.py ${LAMBDA_TASK_ROOT}
COPY determine_db_status.py ${LAMBDA_TASK_ROOT}
COPY determine_web_status.py ${LAMBDA_TASK_ROOT}

CMD [ "system_status.handler" ]

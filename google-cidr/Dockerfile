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

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY cidr.py ${LAMBDA_TASK_ROOT}

CMD [ "cidr.handler" ]

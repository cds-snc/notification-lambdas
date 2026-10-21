FROM public.ecr.aws/lambda/python:3.12

RUN apk add --no-cache ca-certificates && \
    sed -i \
      -e 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!&|' \
      /etc/ca-certificates.conf && \
    update-ca-certificates

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY cidr.py ${LAMBDA_TASK_ROOT}

CMD [ "cidr.handler" ]

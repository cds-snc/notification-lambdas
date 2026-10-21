# Docker image for the heartbeat hitting the lambda API.

FROM public.ecr.aws/lambda/python:3.12

RUN apk add --no-cache ca-certificates && \
    sed -i \
      -e 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!&|' \
      /etc/ca-certificates.conf && \
    update-ca-certificates

ENV PYTHONDONTWRITEBYTECODE 1

RUN dnf -y install git

# Install the function's dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements.txt

# Copy function code
COPY heartbeat.py ${LAMBDA_TASK_ROOT}

CMD [ "heartbeat.handler" ]

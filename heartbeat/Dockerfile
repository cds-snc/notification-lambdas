# Docker image for the heartbeat hitting the lambda API.

FROM public.ecr.aws/lambda/python:3.10

ENV PYTHONDONTWRITEBYTECODE 1

RUN yum -y install git

# Install the function's dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements.txt

# Copy function code
COPY heartbeat.py ${LAMBDA_TASK_ROOT}

CMD [ "heartbeat.handler" ]

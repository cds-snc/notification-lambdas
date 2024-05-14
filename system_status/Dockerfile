# Docker image for the system status lambda API.

FROM public.ecr.aws/lambda/python:3.10

ENV PYTHONDONTWRITEBYTECODE 1

RUN yum -y install git

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

# Docker image for the SES email callback the lambda API.
FROM public.ecr.aws/lambda/python:3.12
ENV PYTHONDONTWRITEBYTECODE 1

# Install the function's dependencies
COPY requirements_for_file_scan_verdict_callbacks.txt ${LAMBDA_TASK_ROOT}
RUN python -m pip install -r requirements_for_file_scan_verdict_callbacks.txt

# Copy function code
COPY file_scan_verdict_callbacks.py ${LAMBDA_TASK_ROOT}

CMD [ "file_scan_verdict_callbacks.lambda_handler" ]

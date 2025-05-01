docker:
	docker build -t notify/ses_to_sqs_email_callbacks .

fmt:
	black . $(ARGS)

install:
	pip install --user -r requirements_for_sqs_email.txt
	pip install --user -r requirements-dev.txt

lint:
	pylint ses_to_sqs_email_callbacks.py

test:
	python3 -m pytest -s -vv test_ses_to_sqs_email_callbacks.py

.PHONY: \
	docker \
	fmt \
	install \
	lint \
	test
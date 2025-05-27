docker:
	docker build -t notify/sns_to_sqs_sms_callbacks .

fmt:
	black . $(ARGS)

install:
	pip install --user -r requirements_for_sns_sms.txt

lint:
	pylint sns_to_sqs_sms_callbacks.py

.PHONY: \
	docker \
	fmt \
	install \
	lint

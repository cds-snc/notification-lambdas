docker:
	docker build -t notify/pinpoint_to_sqs_sms_callbacks .

fmt:
	black . $(ARGS)

install:
	pip install --user -r requirements_for_pinpoint_sms.txt

lint:
	pylint pinpoint_to_sqs_sms_callbacks.py

.PHONY: \
	docker \
	fmt \
	install \
	lint

docker:
	docker build -t notify/ses_receiving_emails .

fmt:
	black . $(ARGS)

install:
	pip install --user -r requirements_for_ses.txt

lint:
	pylint ses_receiving_emails.py

.PHONY: \
	docker \
	fmt \
	install \
	lint

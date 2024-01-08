default:
	python heartbeat.py

docker:
	docker build -t notify/heartbeat .

fmt:
	black . $(ARGS)

install:
	pip install --user -r requirements-dev.txt \
	pip install --user -r requirements.txt

lint:
	pylint heartbeat.py

test:
	python3 -m pytest -s -vv test_heartbeat.py

.PHONY: \
	default \
	docker \
	fmt \
	install	\
	lint \
	test

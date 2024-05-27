# default: 
# 	python3 cidr.py

docker:
	docker build --no-cache -t notify/system_status .

fmt:
	black . $(ARGS)

# install:
# 	pip3 install --user -r requirements-dev.txt &&\
# 	pip3 install --user -r requirements.txt

# lint:
# 	pylint cidr.py

.PHONY: test
test:
	pip install -r requirements_for_system_status.txt
	pytest -v tests/*

.PHONY: \
	default \
	docker \
	fmt \
	install	\
	lint \
	test

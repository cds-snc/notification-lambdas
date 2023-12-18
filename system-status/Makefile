# default: 
# 	python3 cidr.py

docker:
	docker build -t notify/system-status .

# fmt:
# 	black . $(ARGS)

# install:
# 	pip3 install --user -r requirements-dev.txt &&\
# 	pip3 install --user -r requirements.txt

# lint:
# 	pylint cidr.py

test:
	python3 -m pytest -s -vv

.PHONY: \
	default \
	docker \
	fmt \
	install	\
	lint \
	test

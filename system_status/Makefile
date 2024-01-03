# default: 
# 	python3 cidr.py

docker:
	docker build --no-cache -t notify/system_status .

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

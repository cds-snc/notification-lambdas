default:
	python heartbeat.py

docker:
	docker build -t notify/heartbeat .

fmt:
	black . $(ARGS)

install:
    if [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    elif [ -f Gemfile ]; then \
        bundle install; \
    else \
        echo "No dependencies to install"; \
    fi

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

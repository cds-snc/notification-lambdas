include .env.example
export $(shell sed 's/=.*//' .env.example)

default:
	puma -C ./config/puma.rb

docker:
	docker build -t database-tools/blazer:latest .

fmt:
	standardrb --fix

install:
	bundle config set --local with 'development test' &&\
	bundle install

lint:
	standardrb

test:
	docker-compose up -d db &&\
		export BLAZER_CHECKS_DATABASE_URL="$${BLAZER_CHECKS_DATABASE_URL:-$${BLAZER_DATABASE_URL:-$${DATABASE_URL}}}" &&\
		rails db:migrate &&\
	rspec --format documentation

.PHONY: \
	default \
	docker \
	fmt \
	install	\
	lint \
	test

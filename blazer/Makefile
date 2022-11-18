default:
	puma -C ./config/puma.rb

docker:
	docker build -t database-tools/blazer:latest .

fmt:
	rufo . $(ARGS)

install:
	bundle config set --local with 'development test' &&\
	bundle install

lint: # todo: fix rubocop errors
	echo "::warning file=blazer/Makefile,line=14,col=1::lint is not setup..."

test: # todo: write controller and user model tests
	echo "::warning file=blazer/Makefile,line=17,col=1::test is not setup..."

.PHONY: \
	default \
	docker \
	fmt \
	install	\
	lint \
	test

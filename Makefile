lambda:
	@./bin/scaffold.sh

matrix:
	grep "matrix:" .github/workflows/*.yml

.PHONY: \
	lambda \
	matrix

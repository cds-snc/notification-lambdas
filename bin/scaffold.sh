#!/bin/bash

echo "🚧 Lambda Scaffold 🚧"

# shellcheck disable=SC2162
read -p "Lambda name: " LAMBDA

mkdir -p "$LAMBDA"

echo "🚧 Creating $LAMBDA"

echo 📝 Creating "$LAMBDA/Makefile"
cat << EOF > "$LAMBDA/Makefile"
default: 

docker:
	docker build -t $LAMBDA .

fmt:
	echo "::warning file=blazer/Makefile,line=14,col=1::fmt is not setup..."

install:
	echo "::warning file=blazer/Makefile,line=14,col=1::install is not setup..."

lint:
	echo "::warning file=blazer/Makefile,line=14,col=1::lint is not setup..."

test:
	echo "::warning file=blazer/Makefile,line=14,col=1::test is not setup..."

.PHONY: default	docker fmt install lint	test
EOF

echo 📝 Creating "$LAMBDA/Dockerfile"
touch "$LAMBDA/Dockerfile"

echo 📝 Creating "$LAMBDA/README.md"
cat << EOF > "$LAMBDA/README.md"
# $LAMBDA

EOF

echo "✅ Done"

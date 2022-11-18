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

install:

lint:

test:

.PHONY: default	docker fmt install lint	test
EOF

echo 📝 Creating "$LAMBDA/Dockerfile"
touch "$LAMBDA/Dockerfile"

echo 📝 Creating "$LAMBDA/README.md"
cat << EOF > "$LAMBDA/README.md"
# $LAMBDA

EOF

echo "✅ Done"

FROM ruby:3.2.0-alpine3.16@sha256:1c80c2b9a501b36f640c972b3cfa0a4d06ec46a168c2061c8c9e1ec4c337a417

LABEL Author="Andrew Kane <andrew@ankane.org>"

ARG INSTALL_PATH=/app
ARG RAILS_ENV=production
ARG DATABASE_URL=postgresql://user:pass@127.0.0.1/dbname
ARG SECRET_TOKEN=dummytoken

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .

RUN apk add --update build-base git libpq-dev mariadb-dev sqlite-dev libpq mariadb-connector-c sqlite-libs unixodbc && \
    gem install bundler && \
    bundle install && \
    bundle exec rails app:update:bin && \
    bundle exec rake assets:precompile && \
    apk del build-base git libpq-dev mariadb-dev sqlite-dev && \
    rm -rf /var/cache/apk/*

ENV PORT 8080

EXPOSE 8080

CMD puma -C /app/config/puma.rb

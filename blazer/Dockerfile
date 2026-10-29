FROM ruby:3.3-alpine3.24@sha256:24ea89e8103548bc02b53ae5212313afaccc79d11c5f93982bd4de298ec0934d

LABEL Author="Andrew Kane <andrew@ankane.org>"

ARG INSTALL_PATH=/app
ARG RAILS_ENV=production
ARG DATABASE_URL=postgresql://user:pass@127.0.0.1/dbname
ARG BLAZER_CHECKS_DATABASE_URL=postgresql://user:pass@127.0.0.1/dbname
ARG SECRET_TOKEN=dummytoken

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .

RUN apk add --update build-base git libpq-dev mariadb-dev sqlite-dev libpq mariadb-connector-c sqlite-libs unixodbc libstdc++ && \
    gem install bundler && \
    bundle install && \
    bundle exec rails app:update:bin && \
    BLAZER_CHECKS_DATABASE_URL=$BLAZER_CHECKS_DATABASE_URL bundle exec rake assets:precompile && \
    apk del build-base git libpq-dev mariadb-dev sqlite-dev && \
    rm -rf /var/cache/apk/*

# ca-certificates >= 20261020 no longer ships emSign ECC Root CA - G3 or Comodo AAA Services root
RUN apk add --no-cache ca-certificates

ENV PORT 8080

EXPOSE 8080

CMD puma -C /app/config/puma.rb

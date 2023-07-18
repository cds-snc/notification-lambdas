require "bundler/setup"
Bundler.require

require "json"
require "rails"

%w[
  active_record/railtie
  action_controller/railtie
  action_mailer/railtie
  action_view/railtie
  sprockets/railtie
].each do |railtie|
  require railtie
rescue LoadError
end

abort "No DATABASE_URL" unless ENV["DATABASE_URL"]

module BlazerSolo
  class Application < Rails::Application
    routes.append do
      # checks app is up and can connect to database
      # does not check data sources
      # not protected by auth, so do not expose data
      get "health", to: ->(env) {
                          if Blazer::Connection.connection.active?
                            [200, {}, ["OK"]]
                          else
                            [503, {}, ["Service Unavailable"]]
                          end
                        }

      devise_for :users, controllers: {
        omniauth_callbacks: "users/omniauth_callbacks"
      }

      authenticate :user, ->(user) { user.present? } do
        mount Blazer::Engine, at: "/"
      end
    end

    config.cache_classes = true
    config.eager_load = true
    config.log_level = ENV["LOG_LEVEL"].present? ? ENV["LOG_LEVEL"].to_sym : :warn
    config.secret_key_base = ENV["SECRET_KEY_BASE"] || SecureRandom.hex(30)
    config.public_file_server.enabled = ENV["RAILS_SERVE_STATIC_FILES"] != "disabled"
    config.action_mailer.default_url_options = {:host => ENV["MAILER_DEFAULT_HOST"] || "localhost:8080"}

    if ENV["RAILS_LOG_TO_STDOUT"] != "disabled"
      logger = ActiveSupport::Logger.new($stdout)
      logger.formatter = proc do |severity, datetime, progname, msg|
        date_format = datetime.strftime("%Y-%m-%d %H:%M:%S %z")
        JSON.dump(date: date_format.to_s, severity: severity.ljust(5).to_s, message: msg) + "\n"
      end
      config.logger = ActiveSupport::TaggedLogging.new(logger)
    end
  end
end

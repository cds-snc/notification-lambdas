# Restrict checks to queries that use the dedicated checks data source.
module BlazerChecksDataSourceGuard
  # Direct calls to Blazer.run_check must not evaluate non-check datasources.
  def run_check(check)
    checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
    return unless check.query&.data_source == checks_data_source

    super
  end

  def run_checks(schedule: nil)
    checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")

    checks = Blazer::Check.includes(:query).joins(:query).where(blazer_queries: {data_source: checks_data_source})
    checks = checks.where(schedule: schedule) if schedule

    checks.find_each do |check|
      next if check.state == "disabled"

      Safely.safely { run_check(check) }
    end
  end
end

# Defense in depth: block state updates even if run_check is reached some other way.
module BlazerChecksExecutionGuard
  def update_state(result)
    checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
    return unless query&.data_source == checks_data_source

    super
  end
end

Rails.application.config.to_prepare do
  unless Blazer::Check.method_defined?(:query_must_use_checks_data_source)
    Blazer::Check.class_eval do
      validate :query_must_use_checks_data_source

      private

      def query_must_use_checks_data_source
        return if query.blank?

        validate_check_query_data_source do
          checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
          return if query.data_source == checks_data_source

          errors.add(:base, "Checks can only use queries configured with the #{checks_data_source} data source")
        end
      end

      # Lock the persisted query row to avoid racing a concurrent datasource change.
      def validate_check_query_data_source
        return yield unless query.persisted?

        query.with_lock { yield }
      end
    end
  end

  unless Blazer::Query.method_defined?(:query_with_checks_must_use_checks_data_source)
    Blazer::Query.class_eval do
      validate :query_with_checks_must_use_checks_data_source

      private

      def query_with_checks_must_use_checks_data_source
        validate_checks_data_source do
          return unless checks.any?

          checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
          return if data_source == checks_data_source

          errors.add(:base, "Queries with checks must use the #{checks_data_source} data source")
        end
      end

      # Lock this query row to avoid racing a concurrent check creation.
      def validate_checks_data_source
        return yield unless persisted?

        with_lock { yield }
      end
    end
  end

  Blazer.singleton_class.prepend(BlazerChecksDataSourceGuard) unless Blazer.singleton_class < BlazerChecksDataSourceGuard
  Blazer::Check.prepend(BlazerChecksExecutionGuard) unless Blazer::Check < BlazerChecksExecutionGuard
end

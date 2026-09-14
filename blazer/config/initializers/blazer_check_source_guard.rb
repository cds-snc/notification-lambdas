# Restrict checks to queries that use the dedicated checks data source.
module BlazerChecksDataSourceGuard
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

module BlazerChecksExecutionGuard
  def perform(statement, options = {})
    result = super
    query = options[:query]
    return result unless query && !result.timed_out? && !result.cached? && !query.variables.any?

    checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
    return result if query.data_source == checks_data_source

    query.checks.each do |check|
      next unless check.query&.data_source == checks_data_source

      check.update_state(result)
    end

    result
  end
end

Rails.application.config.to_prepare do
  unless Blazer::Check.method_defined?(:query_must_use_checks_data_source)
    Blazer::Check.class_eval do
      validate :query_must_use_checks_data_source

      private

      def query_must_use_checks_data_source
        return if query.blank?
        checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
        return if query.data_source == checks_data_source

        errors.add(:base, "Checks can only be created for queries using the #{checks_data_source} data source")
      end
    end
  end

  unless Blazer::Query.method_defined?(:query_with_checks_must_use_checks_data_source)
    Blazer::Query.class_eval do
      validate :query_with_checks_must_use_checks_data_source, if: :data_source_changed?

      private

      def query_with_checks_must_use_checks_data_source
        return unless checks.exists?

        checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")
        return if data_source == checks_data_source

        errors.add(:base, "Queries with checks must use the #{checks_data_source} data source")
      end
    end
  end

  Blazer.singleton_class.prepend(BlazerChecksDataSourceGuard) unless Blazer.singleton_class < BlazerChecksDataSourceGuard
  Blazer::RunStatement.prepend(BlazerChecksExecutionGuard) unless Blazer::RunStatement < BlazerChecksExecutionGuard
end

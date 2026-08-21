# Restrict checks to queries that use the dedicated checks data source.
Rails.application.config.to_prepare do
  checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")

  next if Blazer::Check.method_defined?(:query_must_use_checks_data_source)

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

  module ::BlazerChecksDataSourceGuard
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

  Blazer.singleton_class.prepend(BlazerChecksDataSourceGuard) unless Blazer.singleton_class < BlazerChecksDataSourceGuard
end

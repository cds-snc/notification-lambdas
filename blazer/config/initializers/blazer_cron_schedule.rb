# frozen_string_literal: true

# Lets a check be scheduled by an arbitrary cron expression instead of (or in
# addition to) the fixed "5 minutes"/"1 hour"/"1 day" presets. A separate
# EventBridge rule invokes `rake blazer:run_due_cron_checks` on a short, fixed
# tick; this file decides which checks are actually due on each tick.
require "fugit"

# Exposes :cron_expression as a permitted param and a form field via Blazer's
# existing notifier field mechanism (Blazer.notifiers.flat_map(&:fields)),
# so the checks form/controller never need to be overridden.
module BlazerCronField
  def self.fields
    [:cron_expression]
  end

  # Required because Check#update_state calls state_change on every
  # registered notifier unconditionally.
  def self.state_change(**)
  end

  # Required because Blazer.send_failing_checks calls failing_checks on
  # every registered notifier unconditionally.
  def self.failing_checks(_checks)
  end
end

module BlazerCronChecks
  def run_due_cron_checks
    checks_data_source = ENV.fetch("BLAZER_CHECKS_DATA_SOURCE_NAME", "checks")

    checks = Blazer::Check.includes(:query)
      .joins(:query)
      .where(blazer_queries: {data_source: checks_data_source})
      .where.not(cron_expression: [nil, ""])

    checks.find_each do |check|
      next if check.state == "disabled"
      next unless BlazerCronChecks.due?(check)

      Safely.safely { run_check(check) }
    end
  end

  def self.due?(check)
    cron = Fugit::Cron.parse(check.cron_expression)
    return false unless cron

    last_scheduled_at = cron.previous_time(Time.now).to_t
    check.last_run_at.nil? || check.last_run_at < last_scheduled_at
  end
end

Rails.application.config.to_prepare do
  unless Blazer::Check.method_defined?(:cron_expression_must_be_valid)
    Blazer::Check.class_eval do
      validate :cron_expression_must_be_valid

      private

      def cron_expression_must_be_valid
        return if cron_expression.blank?

        errors.add(:cron_expression, "is not a valid cron expression") unless Fugit::Cron.parse(cron_expression)
      end
    end
  end

  Blazer.register_notifier(BlazerCronField) unless Blazer.notifiers.include?(BlazerCronField)
  Blazer.singleton_class.prepend(BlazerCronChecks) unless Blazer.singleton_class < BlazerCronChecks
end

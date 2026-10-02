# frozen_string_literal: true

require "rails_helper"

RSpec.describe "Blazer cron check scheduling" do
  around do |example|
    original = ENV["BLAZER_CHECKS_DATA_SOURCE_NAME"]
    ENV["BLAZER_CHECKS_DATA_SOURCE_NAME"] = "checks"
    example.run
  ensure
    if original.nil?
      ENV.delete("BLAZER_CHECKS_DATA_SOURCE_NAME")
    else
      ENV["BLAZER_CHECKS_DATA_SOURCE_NAME"] = original
    end
  end

  it "exposes cron_expression as a notifier field, so it's permitted and rendered without a form/controller override" do
    expect(Blazer.notifiers).to include(BlazerCronField)
    expect(BlazerCronField.fields).to eq([:cron_expression])
  end

  it "allows a blank cron_expression" do
    query = Blazer::Query.create!(data_source: "checks", name: "blank-cron-query", statement: "SELECT 1")
    check = Blazer::Check.new(query: query, cron_expression: nil)

    expect(check.valid?).to be(true)
  end

  it "rejects an invalid cron_expression" do
    query = Blazer::Query.new(data_source: "checks", statement: "SELECT 1")
    check = Blazer::Check.new(query: query, cron_expression: "not a cron")

    expect(check.valid?).to be(false)
    expect(check.errors[:cron_expression]).to include("is not a valid cron expression")
  end

  it "accepts a valid cron_expression" do
    query = Blazer::Query.create!(data_source: "checks", name: "valid-cron-query", statement: "SELECT 1")
    check = Blazer::Check.new(query: query, cron_expression: "*/5 * * * *")

    expect(check.valid?).to be(true)
  end

  describe ".due?" do
    it "is due when the check has never run" do
      check = Blazer::Check.new(cron_expression: "*/5 * * * *", last_run_at: nil)

      expect(BlazerCronChecks.due?(check)).to be(true)
    end

    it "is due when the last run predates the most recent scheduled fire time" do
      check = Blazer::Check.new(cron_expression: "* * * * *", last_run_at: 2.minutes.ago)

      expect(BlazerCronChecks.due?(check)).to be(true)
    end

    it "is not due when it already ran at or after the most recent scheduled fire time" do
      check = Blazer::Check.new(cron_expression: "* * * * *", last_run_at: Time.now)

      expect(BlazerCronChecks.due?(check)).to be(false)
    end
  end

  describe "Blazer.run_due_cron_checks" do
    it "only runs due, non-disabled checks on the checks datasource" do
      checks_query = Blazer::Query.create!(data_source: "checks", name: "cron-checks-query", statement: "SELECT 1")

      due_check = Blazer::Check.create!(query: checks_query, check_type: "bad_data", cron_expression: "* * * * *", last_run_at: 2.minutes.ago)
      not_due_check = Blazer::Check.create!(query: checks_query, check_type: "bad_data", cron_expression: "* * * * *", last_run_at: Time.now)
      disabled_check = Blazer::Check.create!(query: checks_query, check_type: "bad_data", cron_expression: "* * * * *", last_run_at: 2.minutes.ago, state: "disabled")

      not_due_last_run_at = not_due_check.last_run_at
      disabled_last_run_at = disabled_check.last_run_at

      Blazer.run_due_cron_checks

      # Only the due check actually executes, which advances its last_run_at.
      expect(due_check.reload.last_run_at).to be > 1.minute.ago
      expect(not_due_check.reload.last_run_at).to be_within(1).of(not_due_last_run_at)
      expect(disabled_check.reload.last_run_at).to be_within(1).of(disabled_last_run_at)
    end

    it "never runs checks on a non-checks datasource, since such a check cannot be created at all" do
      main_query = Blazer::Query.create!(data_source: "main", name: "cron-main-query", statement: "SELECT 1")
      check = Blazer::Check.new(query: main_query, cron_expression: "* * * * *", last_run_at: 2.minutes.ago)

      expect(check.save).to be(false)
      expect(check.errors[:base]).to include("Checks can only use queries configured with the checks data source")
    end
  end
end

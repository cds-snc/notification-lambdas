# frozen_string_literal: true

require "rails_helper"

RSpec.describe "Blazer checks datasource guard" do
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

  it "rejects checks on non-check queries" do
    query = Blazer::Query.new(data_source: "main", statement: "SELECT 1")
    check = Blazer::Check.new(query: query)

    expect(check.valid?).to be(false)
    expect(check.errors[:base]).to include("Checks can only use queries configured with the checks data source")
  end

  it "prevents a query with checks from switching away from the checks datasource" do
    query = Blazer::Query.new(data_source: "checks", statement: "SELECT 1")
    check = Blazer::Check.new(query: query)
    query.checks << check

    query.data_source = "main"

    expect(query.valid?).to be(false)
    expect(query.errors[:base]).to include("Queries with checks must use the checks data source")
  end

  it "prevents a persisted query with checks from switching datasource without raising a locking error" do
    query = Blazer::Query.create!(data_source: "checks", name: "persisted", statement: "SELECT 1")
    Blazer::Check.create!(query: query)

    query.data_source = "main"

    expect { query.valid? }.not_to raise_error
    expect(query.valid?).to be(false)
    expect(query.errors[:base]).to include("Queries with checks must use the checks data source")
  end

  it "skips runtime evaluation for non-check queries" do
    query = Blazer::Query.new(data_source: "main", statement: "SELECT 1")
    check = Blazer::Check.new(query: query)

    result = instance_double(Blazer::Result, timed_out?: false, cached?: false)

    check.update_state(result)

    expect(check.state).to be_nil
  end

  it "skips direct run_check calls for non-check queries" do
    query = Blazer::Query.new(data_source: "main", statement: "SELECT 1")
    check = Blazer::Check.new(query: query)

    expect(Blazer.run_check(check)).to be_nil
  end

  it "defaults blank datasource values to main for legacy saved queries" do
    query = Blazer::Query.new(statement: "SELECT 1")

    expect(query.data_source).to eq("main")
  end

  it "falls back to main for persisted queries with unknown datasource values" do
    query = Blazer::Query.new(data_source: "legacy", statement: "SELECT 1")
    allow(query).to receive(:persisted?).and_return(true)
    allow(Blazer).to receive(:data_sources).and_return({"main" => double("main")})

    expect(query.data_source).to eq("main")
  end

  it "preserves explicit datasource values" do
    query = Blazer::Query.new(data_source: "checks", statement: "SELECT 1")

    expect(query.data_source).to eq("checks")
  end

  describe "Slack notifications via SNS" do
    around do |example|
      original = ENV["BLAZER_SLACK_SNS_TOPIC_ARN"]
      ENV["BLAZER_SLACK_SNS_TOPIC_ARN"] = "arn:aws:sns:ca-central-1:123456789012:alert-general"
      example.run
    ensure
      if original.nil?
        ENV.delete("BLAZER_SLACK_SNS_TOPIC_ARN")
      else
        ENV["BLAZER_SLACK_SNS_TOPIC_ARN"] = original
      end
    end

    it "still routes checks with no slack_channels set, since routing is per-topic" do
      check = Blazer::Check.new(slack_channels: nil)

      expect(Blazer::SlackNotifier.split_slack_channels(check)).to eq(["sns"])
    end

    it "publishes to the configured SNS topic instead of posting to Slack directly" do
      sns_client = instance_double(Aws::SNS::Client, publish: instance_double(Aws::SNS::Types::PublishResponse, message_id: "test-message-id"))
      allow(Aws::SNS::Client).to receive(:new).and_return(sns_client)

      result = Blazer::SlackNotifier.post(attachments: [{title: "Check Failing", text: "boom"}])

      expect(sns_client).to have_received(:publish).with(hash_including(topic_arn: ENV["BLAZER_SLACK_SNS_TOPIC_ARN"]))
      expect(result).to be(true)
    end

    it "does not raise and returns false when SNS publish fails" do
      sns_client = instance_double(Aws::SNS::Client)
      allow(Aws::SNS::Client).to receive(:new).and_return(sns_client)
      allow(sns_client).to receive(:publish).and_raise(Aws::SNS::Errors::ServiceError.new(nil, "boom"))

      expect(Blazer::SlackNotifier.post(attachments: [{title: "Check Failing", text: "boom"}])).to be(false)
    end
  end
end

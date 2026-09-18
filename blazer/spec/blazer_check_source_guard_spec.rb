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

  it "preserves explicit datasource values" do
    query = Blazer::Query.new(data_source: "checks", statement: "SELECT 1")

    expect(query.data_source).to eq("checks")
  end
end

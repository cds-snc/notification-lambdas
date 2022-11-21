# See https://rubydoc.info/gems/rspec-core/RSpec/Core/Configuration
RSpec.configure do |config|
  config.expect_with :rspec do |expectations|
    expectations.include_chain_clauses_in_custom_matcher_descriptions = true
  end

  # Prevents mocking a method that does not exist on a real object.
  config.mock_with :rspec do |mocks|
    mocks.verify_partial_doubles = true
  end

  # Set the Request test host to "localhost"
  config.before(:each, type: :request) do
    host! "localhost"
  end

  config.shared_context_metadata_behavior = :apply_to_host_groups
end

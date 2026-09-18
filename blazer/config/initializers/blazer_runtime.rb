# Blazer async query polling stores run results in cache.
# With multi-worker Puma and non-shared in-memory cache, poll requests can miss results
# and the UI can stay in a loading state. Force synchronous execution for reliability.
Rails.application.config.after_initialize do
  Blazer.async = false
  Rails.logger.info("Blazer async disabled for interactive query reliability")
end

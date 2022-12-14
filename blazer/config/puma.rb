workers Integer(ENV["PUMA_WORKERS"] || 3)
threads Integer(ENV["MIN_THREADS"] || 1), Integer(ENV["MAX_THREADS"] || 16)
worker_timeout Integer(ENV["PUMA_TIMEOUT"] || 60)

preload_app!

rackup DefaultRackup
if ENV["BIND"]
  bind ENV["BIND"]
else
  port ENV["PORT"] || 3000
end
environment ENV["RACK_ENV"] || "production"

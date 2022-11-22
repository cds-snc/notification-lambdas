module Blazer
  class Audit < Record
    belongs_to :user, optional: true, class_name: Blazer.user_class.to_s
    belongs_to :query, optional: true
    after_save :log_user

    private

    def log_user
      logger.info "Audit #{user.email} ran '#{query.name}' query: '#{query.statement}'"
    end
  end
end

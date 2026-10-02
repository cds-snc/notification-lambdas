class AddCronExpressionToBlazerChecks < ActiveRecord::Migration[7.2]
  def change
    add_column :blazer_checks, :cron_expression, :string
  end
end

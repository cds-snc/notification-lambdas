require "rails_helper"

RSpec.describe "OmniauthCallbacks", type: :request do
  describe "Redirect to sign in" do
    it "redirects to /users/sign_in" do
      get "/queries"
      expect(response).to redirect_to "/users/sign_in"
      follow_redirect!

      expect(response.body).to include('data-login_uri="/users/auth/google_oauth2"')
      expect(response.body).to include('data-auto_select="true"')
    end
  end

  describe "Signed in user" do
    it "loads content once signed in" do
      User.create(email: "test@test.com", password: "password", password_confirmation: "password")
      user = User.where(email: "test@test.com").first
      sign_in user

      get "/queries/tables?data_source=main"
      expect(response.header["Content-Type"]).to include "application/json"
      expect(response.body).to include '{"table":"blazer_dashboard_queries","value":"\"blazer_dashboard_queries\""}'
    end
  end
end

# frozen_string_literal: true

class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  def google_oauth2
    @user = User.from_omniauth(request.env["omniauth.auth"])

    if @user.present?
      request.env["omniauth.auth"].except!("extra")
      sign_in_and_redirect @user, event: :authentication
    else
      session["devise.google_data"] = request.env["omniauth.auth"].except("extra")
      set_flash_message :error, "login_failed"
      redirect_to new_user_session_path(auto_login: "false")
    end
  end

  protected

  def after_omniauth_failure_path_for(_scope)
    new_user_session_path
  end

  def after_sign_in_path_for(resource_or_scope)
    blazer.root_path
  end
end

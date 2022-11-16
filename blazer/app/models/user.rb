class User < ActiveRecord::Base
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable,
         :omniauthable, omniauth_providers: [:google_oauth2]

  def self.from_omniauth(access_token)
    data = access_token.info
    user = User.where(email: data["email"]).first

    unless user
      User.create(
        email: data["email"],
        password: Devise.friendly_token[0, 20],
      )
      user = User.where(email: data["email"]).first
    end

    user
  end
end

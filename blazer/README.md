# :Blazer with Google OAuth2 sign in
[Blazer](https://github.com/ankane/blazer-docker) with Google OAuth2 sign in based on [ankane/blazer-docker](https://github.com/ankane/blazer-docker).

## Setup
1. Create a new [OAuth 2.0 Client ID](https://console.cloud.google.com/apis/credentials):
    - Application type: Web application
    - Authorized JavaScript origins: `http://localhost` and `http://localhost:8080`
    - Authorized redirect URIs: `http://localhost:8080/users/auth/google_oauth2/callback`
1. Create a `.env` based on the `.env.example` and add your Google OAuth2 credentials.
1. Edit the `docker-compose.yml` and change the `DATABASE_URL` and `BLAZER_DATABASE_URL` (suggestions are in file)
1. Run `docker-compose up` and access at [http://localhost:8080](http://localhost:8080).
1. Connect to the `web` service and run `rails db:migrate`.

All routes are protected by Devise, so will need to sign in with Google to access Blazer.  Users that are already signed into their Google account will be automatically signed in once they've accepted the consent screen.

## Notes
To remove Google Sign-in and use server-side sign-in:

1. Add `gem "omniauth-rails_csrf_protection"` to the [`Gemfile`](./Gemfile).
1. Delete the [`config/initializers/omniauth.rb`](./config/initializers/omniauth.rb) file.
1. Add a sign-in button to [`app/views/devise/sessions/new.html.erb`](./app/views/devise/sessions/new.html.erb):

```ruby
<%= button_to "Sign in with Google", user_google_oauth2_omniauth_authorize_path, method: :post %>
```

## Credits
- The majority of this project setup is from [ankane/blazer-docker](https://github.com/ankane/blazer-docker).


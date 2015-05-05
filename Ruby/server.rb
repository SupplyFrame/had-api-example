#!/usr/bin/env ruby
#
# to run this, you'll need two gems:
#    gem install sinatra httparty
#
# run like this:
#    ruby server.rb
#
# go to http://localhost:4567/ and then after authorizing, you should get back /v1/projects JSON response
#
require 'rubygems'
require 'sinatra'
require 'httparty'

CLIENT_ID="your client_id"
CLIENT_SECRET="your client_secret"
API_KEY="your api_key"

set :bind, '0.0.0.0'
set :server, 'thin'
set :protection, :except => [:json_csrf]

get '/' do
    return simple("<a href=\"http://hackaday.io/authorize?client_id=#{CLIENT_ID}&response_type=code\">Authorize this app</a>")
end

get '/oauth-callback' do
    code = params['code']
    url = "https://auth.hackaday.io/access_token?client_id=#{CLIENT_ID}&client_secret=#{CLIENT_SECRET}&code=#{code}&grant_type=authorization_code"
    r1 = HTTParty.post(url)
    return error(r1.body) unless r1.code == 200

    token = r1["access_token"]
    return error("no token found") if token.nil?

    token = "token #{token}"
    r2 = HTTParty.get("http://api.hackaday.io/v1/projects",
                       :headers => {"Authorization" => token},
                       :query => {"api_key" => API_KEY}
                     )
    content_type 'application/json'
    r2.body
end

def simple(body)
b=<<EOL
<!DOCTYPE html>
<html>
  <body>
    #{body}
  </body>
</html>
EOL
b
end

def error(message)
e=<<EOL
<!DOCTYPE html>
<html>
  <body>
  <h2>An error was encountered</h2>
  <pre>#{message}</pre>
  </body>
</html>
EOL
e
end
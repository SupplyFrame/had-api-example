Examples

----------

[NodeJS](https://nodejs.org/):

1. Register app from https://dev.hackaday.io/applications
2.	Fill in `clientId`, `clientSecret`, and `userKey` in `/server.js:18`
3.	`npm i` in console
4.	`node server`  in console
5.	Go To `http://localhost:3000`.

----------

Ruby:

1. To run install two gems: `gem install sinatra httparty`
2. `ruby server.rb` in console
3. Go to `http://localhost:4567/`.  After authorizing, you should get back `/v1/projects` JSON response

----------

Python 2.7/3.4 using Tornado:

1. Register app from https://dev.hackaday.io/applications
2. `python server.py --client-id YOUR_ID --client-secret YOUR_SECRET --user-key YOUR_KEY` in console.
3. Go to `http://localhost:3000`.

----------

For more information, see the [Hackaday API docs](https://dev.hackaday.io/) and the [Hackaday API Project on Hackaday.io](https://hackaday.io/project/5602-hackaday-api)

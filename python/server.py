#!/usr/bin/env python

"""
Example Hackaday.io application in Python using Tornado.
"""

# Original Credit: Stuart Longland <me@vk4msl.id.au>
#
# I hereby contribute the following code to SupplyFrame and the Hackaday.io
# community under the MIT license.

import json
import argparse
import logging

from tornado.web import Application, RequestHandler, \
        RedirectHandler
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.gen import coroutine
from tornado.ioloop import IOLoop


class RootHandler(RequestHandler):
    def get(self):
        self.set_status(200)
        self.render('index.html', dataType=None)


class CallbackHandler(RequestHandler):
    @coroutine
    def get(self):
        # Retrieve the code
        code = self.get_query_argument('code', strip=False)
        logging.debug('Received code %s', code)

        # Determine where to retrieve the access token from
        post_uri = self.application._token_uri \
                + '?client_id=' + self.application._client_id \
                + '&client_secret=' + self.application._client_secret \
                + '&code=' + code \
                + '&grant_type=authorization_code'

        logging.debug('Retrieving access token from %s', post_uri)
        response = yield self.application._client.fetch(
                post_uri, method='POST', body=b'')

        logging.debug('Parsing %s (headers %s)',
                response.body, response.headers)

        body = json.loads(response.body.decode('UTF-8'))
        token = body['access_token']

        response = yield self.application._client.fetch(
                self.application._api_uri \
                        + '/me?api_key=' + self.application._user_key,
                headers={
                    'Authorization': 'token %s' % token
                })

        body = json.loads(response.body.decode('UTF-8'))
        self.set_status(200)
        self.render('index.html',
            dataType='oAuth Data',
            token=token,
            apiData=json.dumps(body)
        )


class UserHandler(RequestHandler):
    @coroutine
    def get(self, user_id):
        logging.debug('inside /users/%s', user_id)
        uri = self.application._api_uri \
                + '/users/' + user_id \
                + '?api_key=' + self.application._user_key \
                + '&sortby=skulls'
        logging.debug('User Data Query: %s', uri)

        response = yield self.application._client.fetch(uri)
        body = json.loads(response.body.decode('UTF-8'))

        self.set_status(200)
        self.render('index.html',
                dataType='User data',
                apiData=json.dumps(body)
        )


class ProjectHandler(RequestHandler):
    @coroutine
    def get(self):
        logging.debug('inside /projects/skulls')
        uri = self.application._api_uri \
                + '/projects?api_key=' + self.application._user_key \
                + '&sortby=skulls'
        logging.debug('Project Data Query: %s', uri)

        response = yield self.application._client.fetch(uri)
        body = json.loads(response.body.decode('UTF-8'))

        self.set_status(200)
        self.render('index.html',
                dataType='Top Skulled Projects',
                apiData=json.dumps(body)
        )


class HADExampleApp(Application):
    """
    Example Hackaday.io API application.
    """
    def __init__(self, client_id, client_secret, user_key,
            api_uri, auth_uri, token_uri):
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_key = user_key
        self._api_uri = api_uri
        self._auth_uri = auth_uri
        self._token_uri = token_uri
        self._client = AsyncHTTPClient()
        super(HADExampleApp, self).__init__([
            (r"/", RootHandler),
            (r"/callback", CallbackHandler),
            (r"/authorize", RedirectHandler, {
                "url": auth_uri \
                        + '?client_id='
                        + client_id
                        + '&response_type=code'
            }),
            (r"/users/([0-9]+)", UserHandler),
            (r"/projects/skulls", ProjectHandler),
        ])


def main(*args, **kwargs):
    """
    Console entry point.
    """
    parser = argparse.ArgumentParser(
            description='HAD API example in Python')
    parser.add_argument('--client-id', dest='client_id',
            help='Hackaday.io client ID')
    parser.add_argument('--client-secret', dest='client_secret',
            help='Hackaday.io client secret')
    parser.add_argument('--user-key', dest='user_key',
            help='Hackaday.io user key')
    parser.add_argument('--api-uri', dest='api_uri',
            default='https://api.hackaday.io/v1',
            help='Hackaday.io API URI')
    parser.add_argument('--auth-uri', dest='auth_uri',
            default='https://hackaday.io/authorize',
            help='Hackaday.io API Authorization URI')
    parser.add_argument('--token-uri', dest='token_uri',
            default='https://auth.hackaday.io/access_token',
            help='Hackaday.io API Token URI')
    parser.add_argument('--listen-address', dest='listen_address',
            default='', help='Interface address to listen on.')
    parser.add_argument('--listen-port', dest='listen_port', type=int,
            default=3000, help='Port number (TCP) to listen on.')
    parser.add_argument('--log-level', dest='log_level',
            default='INFO', help='Logging level')

    args = parser.parse_args(*args, **kwargs)

    # Start logging
    logging.basicConfig(level=args.log_level)

    # Validate arguments
    if (args.client_id is None) or \
            (args.client_secret is None) or \
            (args.user_key is None):
        raise ValueError('--client-id, --client-secret and '\
                '--user-key are mandatory.  Retrieve those '\
                'when you register at '\
                'https://dev.hackaday.io/applications')

    application = HADExampleApp(
            client_id=args.client_id,
            client_secret=args.client_secret,
            user_key=args.user_key,
            api_uri=args.api_uri,
            auth_uri=args.auth_uri,
            token_uri=args.token_uri
    )
    http_server = HTTPServer(application)
    http_server.listen(port=args.listen_port, address=args.listen_address)
    IOLoop.current().start()

if __name__ == '__main__':
    main()

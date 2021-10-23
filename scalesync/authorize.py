import logging
import toml
from rauth.service import OAuth1Service

log = logging.getLogger(__name__)
config = toml.load('config.toml')

oauth = OAuth1Service(
  name='fatsecret',
  consumer_key=config['app_key'],
  consumer_secret=config['app_secret'],
  request_token_url='https://www.fatsecret.com/oauth/request_token',
  access_token_url='https://www.fatsecret.com/oauth/access_token',
  authorize_url='https://www.fatsecret.com/oauth/authorize',
  base_url='https://platform.fatsecret.com/rest/server.api'
)

## Get a Request Token
request_token, request_secret = oauth.get_request_token(method='GET', params={'oauth_callback': 'oob'})

## Get ser uathorization
url = oauth.get_authorize_url(request_token)
print(f'Open this URL in browser and sign in: {url}')
pin = input("Pin: ")

## Get an Access Token
session_token = oauth.get_access_token(request_token, request_secret, params={'oauth_verifier': pin})

access_token = session_token[0]
access_secret = session_token[1]

print(f'Access token: {access_token}')
print(f'Access secret: {access_secret}')

print('You can use those in config file.')

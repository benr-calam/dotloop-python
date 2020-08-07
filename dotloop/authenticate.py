import requests
from base64 import b64encode
from urllib.parse import urljoin
from .bases import DotloopError


class Authenticate:
    base_url = 'https://auth.dotloop.com/oauth/'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
        }

    def url_for_authentication(self, redirect_uri, response_type='code', state=None, redirect_on_deny=False):
        endpoint = 'authorize'
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, params={
            'response_type': response_type,
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'redirect_on_deny': redirect_on_deny
        })
        if response.ok:
            return response.json()
        else:
            raise DotloopError(response.status_code, response.content.decode())

    def acquire_access_and_refresh_tokens(self, code, redirect_uri, state=None):
        endpoint = 'token'
        url = urljoin(self.base_url, endpoint)
        response = self.session.post(url, params={
            'code': code,
            'redirect_uri': redirect_uri,
            'state': state,
            'grant_type': 'authorization_code'
        }, headers=self.headers)

        if response.ok:
            return response.json()
        else:
            raise DotloopError(response.status_code, response.content.decode())

    def refresh_access_token(self, refresh_token):
        endpoint = 'token'
        url = urljoin(self.base_url, endpoint)
        response = self.session.post(url, params={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }, headers=self.headers)

        if response.ok:
            return response.json()
        else:
            raise DotloopError(response.status_code, response.content.decode())

    def revoke_access(self, access_token):
        endpoint = 'token/revoke'
        url = urljoin(self.base_url, endpoint)
        response = self.session.post(url, params={
            'token': access_token
        })

        if response.ok:
            return response.json()
        else:
            raise DotloopError(response.status_code, response.content.decode())
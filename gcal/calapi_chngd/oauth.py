from google_auth_oauthlib import flow as oauthflow

class Oauth(object):

    def __init__(self, credentials_path, scopes, redirect_uri):
        '''Calapi Oauth Constructor

        Parameters:
        credentials_path (string): local directory path to google's oauth
            credentials file
        scopes (list): List of Oauth scopes for which user's consent is required

        Returns:
        Oauth Instance

        Example usage :
        client = Oauth(
            credentials_path='./credentials.json',
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/calendar.events',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.readonly'
            ]
        )
        '''
        self.credentials_path = credentials_path
        self.scopes = scopes
        self.redirect_uri = redirect_uri

    def get_user_credentials(self):
        '''Returns user's credentials with
        access token, reefresh token, etc
        '''
        return self.__session_credentials

    def get_authorization_url(
        self,
        access_type='offline',
        include_granted_scopes='true'
    ):
        '''Returns Authorization Url, used for user's consent
        (Users Consent is required for accessing user calendar)

        Parameters:
        redirect_uri (string): Redirect URL to which google will callback with 
            state and code
        access_type (string): Access token type, default set to 'offline'
        include_granted_scopes (string): Include granted scopes,
            default set to 'true'

        Returns:
        Authorization Url (string)

        Example usage:
        callback_url = 'https://yourdomain.com/api/v1/google/calendar/callback'
        oauth_consent_url = client.get_authorization_url(redirect_uri=callback_url)

        Use `oauth_consent_url` to get user's consent
        '''
        flow = oauthflow.Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        self.redirect_uri = self.redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type=access_type,
            include_granted_scopes=include_granted_scopes
        )
        return authorization_url

    def on_auth_callback(self, state, code):
        '''On Googles Oauth callback, fetch users token using state & code
        Call this function on google's callback after users consent
        
        Parameters:
        state (string): Query param value provided by google
        code (string): Query param value provided by google

        Returns:
        Users Session credentials with access token (dict)

        Example usage:
        state = request.args.get('state')
        code = request.args.get('code')
        session_credentials = client.on_auth_callback(state, code)
        '''
        
        flow = oauthflow.Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.scopes,
            state=state
        )
        flow.redirect_uri = self.redirect_uri
        flow.fetch_token(code=code)
        self.__session_credentials = {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes,
            'expiry': flow.credentials.expiry.strftime('%Y-%m-%dT%H:%M:%S')
        }
        return self.__session_credentials

from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service


class Settings(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)


    def get(self, setting_id):
        '''Returns a single user setting.

        Parameters:
        setting_id (string): The id of the user setting.

        Returns:
        dict: Setting response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/settings/get):
        setting_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.settings.get(setting_id)
        '''
        return self.service.settings().get(setting=setting_id).execute()

    def list(self):
        '''Returns all user settings for the authenticated user.

        Parameters:
        No Params

        Returns:
        dict: User Settings 

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/settings/list):
        resp = session.settings.list()
        '''
        return self.service.settings().list().execute()

    def watch(self):
        '''Not Implemented'''
        raise NotImplementedError("Watch API Wrapper Function Not Implemented")

    def __getattr__(self, name):
        if name == 'query':
            return Query()

from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service


class Colors(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)


    def get(self):
        '''Returns the color definitions for calendars and events.

        Parameters:
        No Params

        Returns:
        dict: Colors response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/colors/get):
        colors = session.colors.get()
        '''
        return self.service.colors().get().execute()

    def __getattr__(self, name):
        if name == 'query':
            return Query()

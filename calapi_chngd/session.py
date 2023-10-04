from .events import Events
from .acl import Acl
from .calendarlist import CalendarList
from .calendars import Calendars
from .calendarsettings import Settings
from .colors import Colors


class Session():

    def __init__(self, session_credentials):
        '''Calapi Users Session Constructor

        Parameters:
        session_credentials (dict): Users credentials with access token

        Returns:
        User Session Instance

        Example usage :
        session = Session(session_credentials=session_credentials)
        '''
        self.session_credentials = session_credentials
    
    def __getattr__(self, name):
        if name == 'acl':
            return Acl(self.session_credentials)
        if name == 'calendarlist':
            return CalendarList(self.session_credentials)
        if name == 'calendars':
            return Calendars(self.session_credentials)
        if name == 'colors':
            return Colors(self.session_credentials)
        if name == 'settings':
            return Settings(self.session_credentials)
        if name == 'events':
            return Events(self.session_credentials)

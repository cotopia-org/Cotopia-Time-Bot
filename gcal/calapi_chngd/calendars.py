from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service


class Calendars(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)

    def clear(self, calendar_id):
        '''Clears a primary calendar. This operation deletes all events
        associated with the primary calendar of an account.

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar Events Deleted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/delete):
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.calendars.clear(calendar_id)
        '''
        return self.service.calendars().clear(calendar_id).execute()

    def delete(self, calendar_id):
        '''Deletes a secondary calendar.
            Use calendars.clear for clearing all events on primary calendars.

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar Deleted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/delete):
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.calendars.delete(calendar_id)
        '''
        return self.service.calendars().delete(calendarId=calendar_id).execute()

    def get(self, calendar_id):
        '''Returns metadata for a calendar

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/get):
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.calendars.get(calendar_id)
        '''
        return self.service.calendars().get(
                    calendarId=calendar_id,
                ).execute()

    def insert(self, query):
        '''Creates a secondary calendar. 

        Parameters:
        query (Query or dict): Calendar Body

        Returns:
        dict: Secondary Calendar Created response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/insert):
        query = session.calendars.query.summary(
                'calendarSummary'
            ).time_zone(
                'America/Los_Angeles'
            )
        calendar = session.calendars.insert(query)
        '''
        if isinstance(query, Query):
            calendar = query.json(camelify=True)
        elif isinstance(query, dict):
            calendar = _camelify(query)
        else:
            raise InvalidJsonError()
        return self.service.calendars().insert(
                    body=calendar
                ).execute()

    def list(self, calendar_id, page_token=None):
        '''Returns the calendars on the user's calendar list.

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary
        page_token (string): Initially Token is kept None,
                for further pages use nextPageToken from the response

        Returns:
        dict: List of Rules response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/list):
        calendar_list_page_1 = session.calendarlist.list(calendar_id=calendar_id)
        page_token = calendar_list_page_1.get('nextPageToken')
        calendar_list_page_2 = session.calendars.list(
                                    calendar_id=calendar_id,
                                    page_token=page_token)
        '''
        return self.service.calendars().list(
                    calendarId=calendar_id,
                    pageToken=page_token
                ).execute()

    def patch(self):
        '''Not Implemented'''
        raise NotImplementedError("Patch API Wrapper Function Not Implemented")

    def update(self, query, calendar_id):
        '''Updates metadata for a calendar. 

        Parameters:
        query (Query or dict): Calendar Update Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar updated response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendars/update):
        query = session.calendars.query.summary(
                        'New Summary'
                    )
        resp = session.calendars.update(query)
        '''
        if isinstance(query, Query):
            calendar = query.json(camelify=True)
        elif isinstance(query, dict):
            calendar = _camelify(query)
        else:
            raise InvalidJsonError()

        updated_calendar = self.service.calendars().get(
                    calendarId=calendar_id,
                ).execute()

        for params in calendar:
            updated_calendar[params] = calendar[params]

        return self.service.calendars().update(
                    calendarId=calendar_id,
                    body=updated_calendar
                ).execute()

    def __getattr__(self, name):
        if name == 'query':
            return Query()

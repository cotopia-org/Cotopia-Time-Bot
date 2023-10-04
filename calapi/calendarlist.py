from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service


class CalendarList(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)

    def delete(self, calendar_id):
        '''Removes a calendar from the user's calendar list

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar Deleted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendarList/delete):
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.calendarlist.delete(calendar_id)
        '''
        return self.service.calendarList().delete(calendarId=calendar_id).execute()

    def get(self, calendar_id):
        '''Returns a calendar from the user's calendar list. 

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendarList/get):
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.calendarlist.get(calendar_id)
        '''
        return self.service.calendarList().get(
                    calendarId=calendar_id,
                ).execute()

    def insert(self, query, calendar_id):
        '''Inserts an existing calendar into the user's calendar list. 

        Parameters:
        query (Query or dict): Calendar Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Calendar Inserted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendarList/insert):
        query = session.calendarList.query.backgroundColor(
                '#0088aa'
            ).foregroundColor(
                '#0088ab'
            )
        calendar_id = 'v497l802ha00asds1p97frtdd0'
        rule = session.calendarlist.insert(query, calendar_id)
        '''
        if isinstance(query, Query):
            calendar_list_entry = query.json(camelify=True)
        elif isinstance(query, dict):
            calendar_list_entry = _camelify(query)
        else:
            raise InvalidJsonError()
        query['id'] = calendar_id
        return self.service.calendarList().insert(
                    body=calendar_list_entry
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
            https://developers.google.com/calendar/v3/reference/calendarList/list):
        calendar_list_page_1 = session.calendarlist.list(calendar_id=calendar_id)
        page_token = calendar_list_page_1.get('nextPageToken')
        calendar_list_page_2 = session.calendarList.list(
                                    calendar_id=calendar_id,
                                    page_token=page_token)
        '''
        return self.service.calendarList().list(
                    calendarId=calendar_id,
                    pageToken=page_token
                ).execute()

    def patch(self):
        '''Not Implemented'''
        raise NotImplementedError("Patch API Wrapper Function Not Implemented")

    def update(self, query, calendar_id):
        '''Updates an existing calendar on the user's calendar list.

        Parameters:
        rule_id (string): Rule ID
        query (Query or dict): Rule Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Rule updated response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/calendarList/update):
        query = session.calendarList.query.scope(
                        type=updatedScopeType,
                        value=updatedScopeEmail,
                    ).role(
                        'updatedRole'
                    )
        resp = session.calendarlist.update(rule_id, query)
        '''
        if isinstance(query, Query):
            calendar_list_entry = query.json(camelify=True)
        elif isinstance(query, dict):
            calendar_list_entry = _camelify(query)
        else:
            raise InvalidJsonError()

        updated_calendar_list_entry = self.service.calendarList().get(
                    calendarId=calendar_id,
                ).execute()

        for params in calendar_list_entry:
            updated_calendar_list_entry[params] = calendar_list_entry[params]

        return self.service.calendarList().update(
                    calendarId=calendar_id,
                    body=updated_calendar_list_entry
                ).execute()

    def watch(self):
        '''Not Implemented'''
        raise NotImplementedError("Watch API Wrapper Function Not Implemented")

    def __getattr__(self, name):
        if name == 'query':
            return Query()

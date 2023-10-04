import google.oauth2.credentials

from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service


class Events(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)

    def delete(self, event_id, calendar_id='primary'):
        '''Deletes an event.

        Parameters:
        event_id (string): Event ID
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Event Deleted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/delete):
        event_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.events.delete(event_id)
        '''
        return self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

    def get(self, event_id, calendar_id='primary'):
        '''Returns an event.

        Parameters:
        event_id (string): Event ID
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Event response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/get):
        event_id = 'v497l802ha00asds1p97frtdd0'
        event = session.events.get(event_id)
        '''
        return self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

    def import_event(self, query, calendar_id='primary'):
        '''Imports an event. This operation is used to add a private copy of
        an existing event to a calendar

        Parameters:
        query (Query or dict): Event Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Import Event response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/import):
        query = session.events.query.summary(
                'Appointment'
            ).location(
                'Somewhere'
            )
        resp = session.events.import_event(query)
        '''
        if isinstance(query, Query):
            request_params = query.json(camelify=True)
        elif isinstance(query, dict):
            request_params = _camelify(query)
        else:
            raise InvalidJsonError()
        return self.service.events().import_(
            calendarId=calendar_id,
            body=request_params
        ).execute()

    def insert(self, query, calendar_id='primary'):
        '''Creates an event

        Parameters:
        query (Query or dict): Event Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Event Created response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/insert):
        query = session.events.query.start(
                date_time='2021-06-03T09:00:00-07:00',
                time_zone='America/Los_Angeles'
            ).end(
                date_time='2021-06-03T09:30:00-07:00',
                time_zone='America/Los_Angeles'
            ).attendees([
                {'email': 'lp_age@example.com'},
                {'email': 'sbrin@example.com'},
            ]).summary(
                'Google I/O 2015'
            ).description(
                '800 Howard St., San Francisco, CA 94103'
            )
        event = session.events.insert(query)
        '''
        if isinstance(query, Query):
            event = query.json(camelify=True)
        elif isinstance(query, dict):
            event = _camelify(query)
        else:
            raise InvalidJsonError()
        return self.service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()

    def instances(self, event_id, page_token=None, calendar_id='primary'):
        '''Returns instances of the specified recurring event.

        Parameters:
        event_id (string): Event ID
        page_token (string): Initially Token is kept None,
                for further pages use nextPageToken from the response
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: List of Instances response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/instances):
        event_id = 'v497l802ha00asds1p97frtdd0'
        instances_page_1 = session.events.instances(event_id)
        page_token = instances_page_1.get('nextPageToken')
        instances_page_2 = session.events.instances(
                                    event_id, page_token=page_token)
        '''
        return self.service.events().instances(
            calendarId=calendar_id,
            eventId=event_id,
            pageToken=page_token
        ).execute()

    def list(self, page_token=None, calendar_id='primary'):
        '''Returns events on the specified calendar.

        Parameters:
        page_token (string): Initially Token is kept None,
                for further pages use nextPageToken from the response
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: List of Events response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/list):
        events_page_1 = session.events.list()
        page_token = events_page_1.get('nextPageToken')
        events_page_2 = session.events.list(page_token=page_token)
        '''
        return self.service.events().list(
            calendarId=calendar_id,
            pageToken=page_token
        ).execute()

    def move(self, event_id, destination_calendar_id, calendar_id='primary'):
        '''Moves an event to another calendar, i.e. changes an event's organizer.

        Parameters:
        event_id (string): Event ID
        destination_calendar_id (string): Destination Calendar ID
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Evemts moved response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/move):
        event_id = 'v497l802ha00asds1p97frtdd0'
        destination_calendar_id = 'some_calendar_id'
        resp = session.events.move(
                            event_id,
                            destination_calendar_id
                        )
        '''
        return self.service.events().move(
            calendarId=calendar_id,
            eventId=event_id,
            destinationCalendarId=destination_calendar_id
        ).execute()

    def patch(self):
        '''Not Implemented'''
        raise NotImplementedError("Patch API Wrapper Function Not Implemented")

    def quickadd(self, text, send_updates='all', calendar_id='primary'):
        '''Creates an event based on a simple text string.

        Parameters:
        text (string): Event Describing the event
        send_updates (string): Guests who should receive notifications 
            about the creation of the new event.
            (Eg. "all" or "externalOnly" or "none")
            Default is set to "all"
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Event created response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/quickAdd):
        text = 'Appointment at Somewhere on June 3rd 10am-10:25am'
        send_updates = 'externalOnly'
        resp = session.events.quickAdd(text, send_updates=send_updates)
        '''
        return self.service.events().quickAdd(
            calendarId=calendar_id,
            text=text,
            send_updates=send_updates
        ).execute()

    def update(self, event_id, query, calendar_id='primary'):
        '''Updates an event.

        Parameters:
        event_id (string): Event ID
        query (Query or dict): Event Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Event updated response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/events/update):
        query = session.events.query.summary(
                'Updated summary Google I/O 2015'
            ).description(
                'Updated description 800 Howard St., San Francisco, CA 94103'
            )
        resp = session.events.update(event_id, query)
        '''
        if isinstance(query, Query):
            event = query.json(camelify=True)
        elif isinstance(query, dict):
            event = _camelify(query)
        else:
            raise InvalidJsonError()

        updated_event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        for params in event:
            updated_event[params] = event[params]

        return self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=updated_event
        ).execute()

    def watch(self):
        '''Not Implemented'''
        raise NotImplementedError("Watch API Wrapper Function Not Implemented")

    def __getattr__(self, name):
        if name == 'query':
            return Query()

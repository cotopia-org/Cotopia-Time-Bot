from .query import Query, _camelify
from .exceptions import InvalidJsonError
from .service import Service

class Acl(Service):

    def __init__(self, session_credentials):
        super().__init__(session_credentials)

    def delete(self, rule_id, calendar_id='primary'):
        '''Deletes an access control rule.

        Parameters:
        rule_id (string): Rule ID
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Rule Deleted response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/acl/delete):
        rule_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.acl.delete(rule_id)
        '''
        return self.service.acl().delete(
                    calendarId=calendar_id,
                    ruleId=rule_id
                ).execute()

    def get(self, rule_id, calendar_id='primary'):
        '''Returns an access control rule

        Parameters:
        rule_id (string): Rule ID
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Rule response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/acl/get):
        rule_id = 'v497l802ha00asds1p97frtdd0'
        resp = session.acl.get(rule_id)
        '''
        return self.service.acl().get(
                    calendarId=calendar_id,
                    ruleId=rule_id
                ).execute()

    def insert(self, query, calendar_id='primary'):
        '''Creates an access control rule.

        Parameters:
        query (Query or dict): Rule Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Rule Created response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/acl/insert):
        query = session.acl.query.scope(
                type=scopeType,
                value=scopeEmail,
            ).role(
                'role'
            )
        rule = session.acl.insert(query)
        '''
        if isinstance(query, Query):
            rule = query.json(camelify=True)
        elif isinstance(query, dict):
            rule = _camelify(query)
        else:
            raise InvalidJsonError()
        return self.service.acl().insert(
                    calendarId=calendar_id,
                    body=rule
                ).execute()

    def list(self, calendar_id='primary'):
        '''Returns the rules in the access control list for the calendar.

        Parameters:
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: List of Rules response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/acl/list):
        rules = session.acl.list()
        '''
        return self.service.acl().list(calendarId=calendar_id).execute()

    def patch(self):
        '''Not Implemented'''
        raise NotImplementedError("Patch API Wrapper Function Not Implemented")

    def update(self, rule_id, query, calendar_id='primary'):
        '''Updates an access control rule. 

        Parameters:
        rule_id (string): Rule ID
        query (Query or dict): Rule Body
        calendar_id (string): Calendar ID, default is set to primary

        Returns:
        dict: Rule updated response

        Example usage (Refer:
            https://developers.google.com/calendar/v3/reference/acl/update):
        query = session.acl.query.scope(
                        type=updatedScopeType,
                        value=updatedScopeEmail,
                    ).role(
                        'updatedRole'
                    )
        resp = session.acl.update(rule_id, query)
        '''
        if isinstance(query, Query):
            rule = query.json(camelify=True)
        elif isinstance(query, dict):
            rule = _camelify(query)
        else:
            raise InvalidJsonError()

        updated_rule = self.service.acl().get(
                    calendarId=calendar_id,
                    ruleId=rule_id
                ).execute()

        for params in rule:
            updated_rule[params] = rule[params]

        return self.service.acl().update(
                    calendarId=calendar_id,
                    ruleId=rule_id,
                    body=updated_rule
                ).execute()

    def watch(self):
        '''Not Implemented'''
        raise NotImplementedError("Watch API Wrapper Function Not Implemented")

    def __getattr__(self, name):
        if name == 'query':
            return Query()

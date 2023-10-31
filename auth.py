import datetime
from jose import jwt
import pytz


def create_token(d: dict):
    token = None
    now = datetime.datetime.now(tz=pytz.utc)
    expires_at = now + datetime.timedelta(0,3600) # an hour later
    d['expires_at'] = expires_at.strftime("%Y-%m-%dT%H:%M:%S%z")
    d['is_genuine'] = "5c0f70258bbad3a97852b9ce6d4f43373c8bd2ac288e1a3fd258f1abc780f47a"
    token = jwt.encode(d, 'd6e526898ba5c41aaac53f45c99d7f2fd3fdca475fa394c006b9b809eadb951c', algorithm='HS256')
    return token

def decode_token(token: str):
    decoded = jwt.decode(token, 'd6e526898ba5c41aaac53f45c99d7f2fd3fdca475fa394c006b9b809eadb951c', algorithms=['HS256'])
    if ('is_genuine' in decoded):
        if (decoded['is_genuine'] == "5c0f70258bbad3a97852b9ce6d4f43373c8bd2ac288e1a3fd258f1abc780f47a"):
            expires_at = datetime.datetime.strptime(decoded['expires_at'], "%Y-%m-%dT%H:%M:%S%z")
            now = datetime.datetime.now(tz=pytz.utc)
            delta = expires_at - now
            if (delta.total_seconds() > 0):
                del decoded['is_genuine']
                return decoded
            else:
                return False
        else:
            return False
    else:
        return False
import datetime
from jose import jwt
import pytz


def create_token(d: dict):
    token = None
    now = datetime.datetime.now(tz=pytz.utc)
    expires_at = now + datetime.timedelta(0,3600) # an hour later
    d['expires_at'] = expires_at.strftime("%Y-%m-%dT%H:%M:%S%z")
    d['is_genuine'] = "hast be quran!"
    token = jwt.encode(d, 'this is shit fr fr', algorithm='HS256')
    return token

def decode_token(token: str):
    decoded = jwt.decode(token, 'this is shit fr fr', algorithms=['HS256'])
    if ('is_genuine' in decoded):
        if (decoded['is_genuine'] == "hast be quran!"):
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
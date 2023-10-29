import datetime

import pytz
import auth
from jose import jwt


d = {
    'discord_guild': 1125764070935638086,
    'discord_id': 592386692569366559,
    'discord_name': "kharrati",
    'discord_roles': {},
    }

# token = auth.create_token(d)

# print(token)

d['is_genuine'] = "hast be quran!"

now = datetime.datetime.now(tz=pytz.utc)
expires_at = now - datetime.timedelta(0,3600) # an hour later
d['expires_at'] = expires_at.strftime("%Y-%m-%dT%H:%M:%S%z")

token = jwt.encode(d, 'this is shit fr fr', algorithm='HS256')


decoded = auth.decode_token(token)

print(decoded)
import psycopg2
from gcal import calcal as GCalSetup
from google.oauth2.credentials import Credentials
import json
from datetime import datetime


# try:
#     GCalSetup.get_cotopia_events(discord_guild=1125764070935638086, discord_id=592386692569366559)
# except:
#     g_redirect_url = GCalSetup.gen_GOAuth_URL()
#     link = "http://127.0.0.1:8000/gcal?u=" + g_redirect_url + "&a=" + str(592386692569366559) + "&b=" + str(1125764070935638086)
#     print(link)

# 

# ValueError: time data '2023-10-07T11:16:47.203215Z' does not match format '%Y-%m-%dT%H:%M:%SZ'

creds = None
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()
cur.execute("SELECT google_token FROM person WHERE discord_guild = %s AND discord_id = %s;",
                 (1125764070935638086, 592386692569366559))
try:
    token = cur.fetchone()[0]
except:
    token = None

if (token != None):
        creds = Credentials.from_authorized_user_info(token)
        print("token found!")
        print("the token ---------")
        print(token)
        print("creds.to_json ---------")
        print(creds.to_json())

conn.commit()
cur.close()
conn.close()
the_dict = json.loads(creds.to_json())
print(the_dict["expiry"])
the_dict["expiry"] = datetime.strptime('2023-10-07T11:16:47.203215Z', '%Y-%m-%dT%H:%M:%S.%fZ')
print(the_dict)
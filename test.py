import psycopg2
from gcal import calcal as GCalSetup
from google.oauth2.credentials import Credentials
import json
from datetime import datetime

from person import Person

# instances = GCalSetup.get_event_instances(discord_guild=1125764070935638086, discord_id=592386692569366559, event_id="70sjie9i68r32bb3cdj3gb9k65ijcbb2c4pjgb9p6hijap1h6th38o9n6k")
# events = GCalSetup.get_keyword_events(discord_guild=1125764070935638086, discord_id=592386692569366559, keyword="cotopia")
# f = open("instances.json", "w")
# f.write(events)
# f.close()


# print(GCalSetup.get_user_calendars(1125764070935638086, 592386692569366559))

# raw_instances = GCalSetup.get_event_instances(1125764070935638086, 592386692569366559, "70sjie9i68r32bb3cdj3gb9k65ijcbb2c4pjgb9p6hijap1h6th38o9n6k_20231008T053000Z'")
# print(raw_instances["items"])

# l = []
# print(GCalSetup.process_events(l))

# events = GCalSetup.get_keyword_events(1125764070935638086, 592386692569366559, "cotopia")
# f = open("events.json", "w")
# f.write(events)
# f.close()

# 1125764070935638086
# 592386692569366559
# kharrati
# 4/0AfJohXlRFQAXnS91ijKvR1JiT7KpXx0L9w2G352UUiHwZRgtKlYnhrxNZ01fS13YvyIugg
# HW0g1XEZtSQqUKRJIB0jV2gw5vnkvU

# GCalSetup.store_user_creds(1125764070935638086, 592386692569366559, "kharrati", "4/0AfJohXlxwoQVJB5hqmhRFxARnjQ0IozBR7bmiI_dKXP0DugZ0NKolnaqYyyAdFt7Uh4taA", "HW0g1XEZtSQqUKRJIB0jV2gw5vnkvU")
# print(GCalSetup.get_user_events(1125764070935638086, 592386692569366559))


person = Person()

print(person.get_person_info(1125764070935638086, "kharrati"))
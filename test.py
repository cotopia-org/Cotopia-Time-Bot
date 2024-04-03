import pytz
import datetime

# SelectOption(label="Asia/Tehran", value="Asia/Tehran"),
#             SelectOption(label="Asia/Dubai", value="Asia/Dubai"),
#             SelectOption(label="Asia/Istanbul", value="Asia/Istanbul"),
#             SelectOption(label="Africa/Cairo", value="Africa/Cairo"),
#             SelectOption(label="Europe/London", value="Europe/London"),
#             SelectOption(label="America/Toronto", value="America/Toronto"),

now = datetime.datetime.now(pytz.timezone("America/Toronto"))
start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
start_epoch = int(start_dt.timestamp())
end_epoch = start_epoch + (24 * 3600)
end = datetime.datetime.fromtimestamp(end_epoch, tz=pytz.timezone("America/Toronto"))
print(start_dt)
print(end)
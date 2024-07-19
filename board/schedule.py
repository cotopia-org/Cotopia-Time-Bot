import datetime

import requests


def get_schedules(start_epoch: int, end_epoch: int, guild_id: int):
    result = {}
    REQUEST_URL = "http://tooljet.cotopia.social:8084/total_hours/all"
    start_str = datetime.datetime.fromtimestamp(start_epoch).strftime("%Y-%m-%d")
    end_str = datetime.datetime.fromtimestamp(end_epoch).strftime("%Y-%m-%d")
    params = {
        "id_server": guild_id,
        "start_date": start_str,
        "end_date": end_str,
    }
    r = requests.get(url=REQUEST_URL, params=params)
    if r.status_code == 200:
        the_list = r.json()["total_duration_hours"]
        for each in the_list:
            result[int(each["id_discord"])] = each["total_duration_hours"]
    else:
        print("http://tooljet.cotopia.social:8084/total_hours/all RETURNED AN ERROR")
        print(r.json())
    return result

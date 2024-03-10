import datetime

import psycopg2


class HeatMap:

    def __init__(self, doer: str) -> None:
        conn = psycopg2.connect(
            host="localhost",
            dbname="discord_bot_db",
            user="cotopia",
            password="123123",
            port=5432,
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM discord_event WHERE doer = %s ORDER BY ts;", [doer])
        self.data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

    def get_first_event(self):
        return self.data[0][1]

    def get_start(self):
        first_event = self.get_first_event()
        # 0 for Monday
        days_ahead = 0 - first_event.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (first_event + datetime.timedelta(days_ahead)).date()

    def get_last_event(self):
        return self.data[len(self.data) - 1][1]

    def get_end():
        pass

    def number_of_weeks():
        pass

    def create_dict():
        pass

    def event_processor():
        pass

    def calc_percentage():
        pass


# get first apearance
# start = get next Monday 00:00
# get last apearance
# end = get previous Sunday 23:59 (handle edge cases)
# k = number of weeks
# create dic with 7 * 48 keys, all set to [0, k]
# for each session start add +1 to [0, k] accoarding key
# for duration, add +1 to next keys
# check weather an evnent is for an already calcd slot
# calc percentage


hm = HeatMap(doer="kharrati")
print(hm.get_first_event())
# print(hm.get_last_event_epoch())
print(hm.get_start())


# f(day, res)

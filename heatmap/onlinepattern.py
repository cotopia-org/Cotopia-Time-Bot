from datetime import datetime, timedelta
from os import getenv

import psycopg2
from dotenv import load_dotenv


class OnlinePattern:

    def __init__(self, doer: str) -> None:
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM discord_event WHERE doer = %s ORDER BY ts;", [doer])
        self.data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

    # resolution is in seconds
    def a_day(self, day: datetime, resolution: int):
        day_start = int(
            datetime(
                year=day.year, month=day.month, day=day.day, hour=0, minute=0, second=0
            ).strftime("%s")
        )
        day_end = day_start + 86399
        number_of_slots = int(24 * 3600 / resolution)
        arr = []
        n = 1
        while n <= number_of_slots:
            arr.append(False)
            n = n + 1

        events = []
        for i in self.data:
            if i[3] == "SESSION STARTED":
                if day_start <= i[2] <= day_end:
                    events.append(i)

        if len(events) == 0:
            return arr

        index = 0
        e = 0
        while index <= (number_of_slots - 1):
            slot_start = day_start + (resolution * index)
            slot_end = slot_start + resolution
            if slot_start <= events[e][2]:
                if events[e][2] <= slot_end:
                    # ok inja bood
                    arr[index] = True
                    index = index + 1
                    # bebinim che ghadr tool mikeshe
                    if 0 < events[e][9]:
                        session_end = events[e][2] + events[e][9]
                        next_slot_start = slot_end
                        while next_slot_start <= session_end:
                            if index <= (number_of_slots - 1):
                                arr[index] = True
                            index = index + 1
                            next_slot_start = next_slot_start + resolution
                    # berim event ba'di
                    e = e + 1
                    if len(events) <= e:
                        break
                else:
                    index = index + 1
            else:
                # this means the event belonges to the previous slot which is already true
                e = e + 1
                if len(events) <= e:
                    break
        # ممکنه که روز با یه شسن باز از روز قبلی شروع بشه
        # این هندل نشده
        # اگر توی این روز سشن اندی بود که قبلش استارت نبود، همه‌ی اسلات‌های قبل از اون باید ترو بشن
        first_start_of_day = events[0][2]
        print(f"first_start_of_day is {first_start_of_day}")
        # looking for session end before it
        the_end_before_start = -1
        for i in self.data:
            if day_start <= i[2] < first_start_of_day:
                if i[3] == "SESSION ENDED":
                    the_end_before_start = i[2]

        if the_end_before_start != -1:
            print(f"the_end_before_start  is {the_end_before_start }")
            # all slots with the start smaller than this, should be true
            slot_start = day_start
            i = 0
            while slot_start < the_end_before_start:
                arr[i] = True
                slot_start = slot_start + resolution
                i = i + 1

        return arr

    def a_period(
        self, start_day: datetime, end_day: datetime, resolution: int, scope: str
    ):
        if scope == "WEEK":
            return self.a_period_weekly(start_day, end_day, resolution)
        elif scope == "MONTH":
            return self.a_period_monthly(start_day, end_day, resolution)

    def a_period_weekly(self, start_day: datetime, end_day: datetime, resolution: int):

        all = [[], [], [], [], [], [], []]

        the_day = start_day
        while the_day <= end_day:
            arr = self.a_day(day=the_day, resolution=resolution)
            all[the_day.weekday()].append(arr)
            the_day = the_day + timedelta(days=1)

        return all

    def a_period_monthly(self, start_day: datetime, end_day: datetime, resolution: int):
        pass


op = OnlinePattern(doer="kharrati")
day = datetime(year=2023, month=10, day=14)
end = datetime(year=2023, month=11, day=16)

print(op.a_period_weekly(start_day=day, end_day=end, resolution=3600))

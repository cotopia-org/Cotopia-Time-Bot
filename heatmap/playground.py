import psycopg2
import time


# Monday	0
# Tuesday	1
# Wednesday	2
# Thursday	3
# Friday	4
# Saturday	5
# Sunday	6


# conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
#                         password="Tp\ZS?gfLr|]'a", port=5432)
# cur = conn.cursor()
# cur.execute("SELECT ts FROM discord_event WHERE id = 100;")
# data = cur.fetchone()[0]

# conn.commit()
# cur.close()
# conn.close()


# print(data)
# print(type(data))
# print(data.weekday())


# we need a func that shows presence
# give each half an hour a score! 48 points for each day
# divided by total number of that day!



conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()
cur.execute("SELECT * FROM discord_event WHERE doer = 'kharrati';")
data = cur.fetchall()
conn.commit()
cur.close()
conn.close()

weekday_count = {
    "Monday": 0,
    "Tuesday": 0,
    "Wednesday": 0,
    "Thursday": 0,
    "Friday": 0,
    "Saturday": 0,
    "Sunday": 0
}

for e in data:

    if (e[3] == "SESSION STARTED"):
        if e[1].weekday() == 0:
            weekday_count["Monday"] = weekday_count["Monday"] + 1
            print(e[1].time())
        elif e[1].weekday() == 1:
            weekday_count["Tuesday"] = weekday_count["Tuesday"] + 1
        elif e[1].weekday() == 2:
            weekday_count["Wednesday"] = weekday_count["Wednesday"] + 1
        elif e[1].weekday() == 3:
            weekday_count["Thursday"] = weekday_count["Thursday"] + 1
        elif e[1].weekday() == 4:
            weekday_count["Friday"] = weekday_count["Friday"] + 1
        elif e[1].weekday() == 5:
            weekday_count["Saturday"] = weekday_count["Saturday"] + 1
        else:
            weekday_count["Sunday"] = weekday_count["Sunday"] + 1

print(weekday_count)




# --------------------------------------------------------------

end = int(time.time())
start = end - (2678400 * 3)



# ---------
# get first apearance 
# start = get next Monday 00:00 
# get last apearance
# end = get previous Sunday 23:59 (handle edge cases)
# k = number of weeks
# create dic with 7 * 48 keys, all set to [0, k]
# for each session start add +1 to [0, k] accoarding key
# for duration, add +1 to next keys
# calc percentage
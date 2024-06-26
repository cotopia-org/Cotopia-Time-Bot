from datetime import datetime
from os import getenv

import psycopg2
import pytz
from dotenv import load_dotenv
from persiantools.jdatetime import JalaliDateTime

from person import Person


# ✅
def make_report(driver: str, doer: str, start_epoch: int, end_epoch: int):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()
    cur.execute(
        """
                SELECT * From discord_event
                WHERE pairid IS NOT NULL
                AND driver = %s
                AND kind = ANY(ARRAY['SESSION STARTED', 'TALKING STARTED', 'SESSION PAUSED'])
                AND doer = %s
                AND epoch >= %s
                AND epoch <= %s
                ORDER BY id
                """,
        (driver, doer, start_epoch, end_epoch),
    )

    data = cur.fetchall()

    rows_count = 0
    sessions_count = 0
    pausings_count = 0
    talkings_count = 0
    total_session_duration = 0.0
    total_pausing_duration = 0.0
    total_talking_duration = 0.0

    for row in data:
        # print(row)
        rows_count += 1
        if row[3] == "SESSION STARTED":
            sessions_count += 1
            total_session_duration = total_session_duration + row[9]
        elif row[3] == "SESSION PAUSED":
            pausings_count += 1
            total_pausing_duration = total_pausing_duration + row[9]
        elif row[3] == "TALKING STARTED":
            talkings_count += 1
            total_talking_duration = total_talking_duration + row[9]

    total_sd_hours = round((total_session_duration / 3600), 1)
    total_pd_hours = round((total_pausing_duration / 3600), 1)
    total_td_hours = round((total_talking_duration / 3600), 1)

    on_mobile_hours = round(
        (on_mobile_duration(driver, doer, start_epoch, end_epoch, cur) / 3600), 1
    )

    net_sd_hours = round((total_sd_hours - total_pd_hours), 1)

    report_dic = {
        "User": doer,
        "From": start_epoch,
        "To": end_epoch,
        "Number Of Rows": rows_count,
        "Number Of Sessions": sessions_count,
        "Number Of Pausings": pausings_count,
        "Number Of Talkings": talkings_count,
        "Number Of On Moblies": on_mobile_count(
            driver, doer, start_epoch, end_epoch, cur
        ),
        "Raw Session Hours": total_sd_hours,
        "Total Puasing Hours": total_pd_hours,
        "Total Talking Hours": total_td_hours,
        "Net On Mobile Hours": on_mobile_hours,
        "Net Session Hours": net_sd_hours,
    }

    # report = json.dumps(report_dic)

    conn.commit()
    cur.close()
    conn.close()

    return report_dic


def make_report_seconds(driver: str, doer: str, start_epoch: int, end_epoch: int):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()
    cur.execute(
        """
                SELECT * From discord_event
                WHERE pairid IS NOT NULL
                AND driver = %s
                AND kind = ANY(ARRAY['SESSION STARTED', 'TALKING STARTED', 'SESSION PAUSED'])
                AND doer = %s
                AND epoch >= %s
                AND epoch <= %s
                ORDER BY id
                """,
        (driver, doer, start_epoch, end_epoch),
    )

    data = cur.fetchall()

    rows_count = 0
    sessions_count = 0
    pausings_count = 0
    talkings_count = 0
    total_session_duration = 0.0
    total_pausing_duration = 0.0
    total_talking_duration = 0.0

    for row in data:
        # print(row)
        rows_count += 1
        if row[3] == "SESSION STARTED":
            sessions_count += 1
            total_session_duration = total_session_duration + row[9]
        elif row[3] == "SESSION PAUSED":
            pausings_count += 1
            total_pausing_duration = total_pausing_duration + row[9]
        elif row[3] == "TALKING STARTED":
            talkings_count += 1
            total_talking_duration = total_talking_duration + row[9]

    total_sd_seconds = int(total_session_duration)
    total_pd_seocnds = int(total_pausing_duration)
    total_td_seconds = int(total_talking_duration)

    on_mobile_seconds = int(
        on_mobile_duration(driver, doer, start_epoch, end_epoch, cur)
    )

    net_sd_seconds = total_sd_seconds - total_pd_seocnds

    report_dic = {
        "User": doer,
        "From": start_epoch,
        "To": end_epoch,
        "Number Of Rows": rows_count,
        "Number Of Sessions": sessions_count,
        "Number Of Pausings": pausings_count,
        "Number Of Talkings": talkings_count,
        "Number Of On Moblies": on_mobile_count(
            driver, doer, start_epoch, end_epoch, cur
        ),
        "Raw Session Hours": total_sd_seconds,
        "Total Puasing Hours": total_pd_seocnds,
        "Total Talking Hours": total_td_seconds,
        "Net On Mobile Hours": on_mobile_seconds,
        "Net Session Hours": net_sd_seconds,
    }

    # report = json.dumps(report_dic)

    conn.commit()
    cur.close()
    conn.close()

    return report_dic


# # ✅
def on_mobile_count(driver: str, doer: str, start_epoch: int, end_epoch: int, cursor):
    cursor.execute(
        """
                SELECT COUNT(note->>'is_on_mobile') FROM discord_event
                WHERE doer = %s
                AND epoch >= %s
                AND epoch <= %s
                AND driver = %s
                AND kind = 'SESSION STARTED'
                AND duration != -1
                AND note->>'is_on_mobile' = 'true'
                AND note->>'mobile_status' = 'online'
                """,
        (doer, start_epoch, end_epoch, driver),
    )
    number_of_on_mobile = cursor.fetchone()[0]
    if number_of_on_mobile is None:
        return 0
    else:
        return number_of_on_mobile


# # ✅
def on_mobile_duration(
    driver: str, doer: str, start_epoch: int, end_epoch: int, cursor
):
    cursor.execute(
        """
                   SELECT SUM(duration) FROM discord_event
                   WHERE doer = %s
                   AND epoch >= %s
                   AND epoch <= %s
                   AND driver = %s
                   AND kind = 'SESSION STARTED'
                   AND duration != -1
                   AND note->>'is_on_mobile' = 'true'
                   AND note->>'mobile_status' = 'online'
                   """,
        (doer, start_epoch, end_epoch, driver),
    )

    duration_of_on_mobile = cursor.fetchone()[0]

    if duration_of_on_mobile is None:
        return 0
    else:
        cursor.execute(
            """
                   SELECT SUM(duration) FROM discord_event
                   WHERE doer = %s
                   AND epoch >= %s
                   AND epoch <= %s
                   AND driver = %s
                   AND kind = 'SESSION PAUSED'
                   AND duration != -1
                   AND note->>'is_on_mobile' = 'true'
                   AND note->>'mobile_status' = 'online'
                   """,
            (doer, start_epoch, end_epoch, driver),
        )

        paused_on_mobile = cursor.fetchone()[0]
        if paused_on_mobile is None:
            paused_on_mobile = 0

        return duration_of_on_mobile - paused_on_mobile


# ✅
def make_raw_file(
    driver: str, doer: str, start_epoch: int, end_epoch: int, asker_id: int
):
    person = Person()
    locale = person.get_locale(discord_guild=int(driver), discord_id=asker_id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    if calsys == "Gregorian":
        from_date = datetime.fromtimestamp(
            int(start_epoch), pytz.timezone(tz)
        ).strftime("%c")
        to_date = datetime.fromtimestamp(int(end_epoch), pytz.timezone(tz)).strftime(
            "%c"
        )
    elif calsys == "Jalali":
        from_date = JalaliDateTime.fromtimestamp(
            int(start_epoch), pytz.timezone(tz)
        ).strftime("%c")
        to_date = JalaliDateTime.fromtimestamp(
            int(end_epoch), pytz.timezone(tz)
        ).strftime("%c")

    try:
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT * From discord_event
                    WHERE doer = %s
                    AND epoch >= %s
                    AND epoch <= %s
                    AND driver = %s
                    ORDER BY id
                    """,
            (doer, start_epoch, end_epoch, driver),
        )
        data = cur.fetchall()

        filename = doer + "_" + str(int(((start_epoch + end_epoch) / 17)))
        reportfile = open("./rawreports/" + filename + ".txt", "w")
        reportfile.write(
            "(id SERIAL NOT NULL PRIMARY KEY, ts TIMESTAMPTZ NOT NULL DEFAULT NOW(), epoch integer null, kind varchar(255) null, doer varchar(255) null, isPair boolean DEFAULT FALSE, pairID integer null, isValid boolean DEFAULT TRUE, note json null, duration integer DEFAULT -1, driver varchar(255))\n"
        )
        reportfile.write(
            "_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________\n"
        )
        reportfile.write(
            "doer = "
            + doer
            + "\nFrom: "
            + from_date
            + f"   epoch {start_epoch}"
            + "\nTo: "
            + to_date
            + f"   epoch {end_epoch}"
            + "\nTime Zone: "
            + tz
            + "\n"
        )
        reportfile.write(
            "_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________\n"
        )

        for row in data:
            reportfile.write(str(row) + "\n")

        filepath = "./rawreports/" + filename + ".txt"

        conn.commit()
        cur.close()
        conn.close()
        reportfile.close()

    except Exception as e:
        filepath = "./rawreports/error.log"
        print(e)

    return filepath


# ✅
def get_doers_list(driver: str, start_epoch: int, end_epoch: int):
    doers = []
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()

    cur.execute(
        """
                SELECT DISTINCT doer From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                AND driver = %s
                ORDER BY doer;
                """,
        (start_epoch, end_epoch, driver),
    )
    d1 = cur.fetchall()

    #### yadam nemiad chera in kar ro karde boodam
    #### be nazar dige bi fayede miad

    #### aha fek konam chon ye seri az event ha ro ba discord_id
    #### sabt mikardak ye seri ro ba discord_name
    #### dige alan hame ba discord_id hastan pas niazi nist dige

    # cur.execute(
    #     f"""
    #             SELECT discord_id FROM person
    #             WHERE discord_guild = {driver}"""
    # )
    # d2 = cur.fetchall()
    # discord_ids = []
    # for i in d2:
    #     discord_ids.append(str(i[0]))

    for row in d1:
        if row[0] is not None and row[0] != "/today":
            # if row[0] not in discord_ids:
            doers.append(row[0])

    conn.commit()
    cur.close()
    conn.close()

    return doers


# ✅
def make_board(driver: str, start_epoch: int, end_epoch: int):
    doers = get_doers_list(driver=driver, start_epoch=start_epoch, end_epoch=end_epoch)
    the_board = {}

    for user in doers:
        user_report = make_report(
            driver=driver, doer=user, start_epoch=start_epoch, end_epoch=end_epoch
        )
        if user_report["Net Session Hours"] > 0:
            the_board[user] = user_report["Net Session Hours"]

    sorted_board = sorted(the_board.items(), key=lambda x: x[1], reverse=True)

    return sorted_board


def make_board_seconds(driver: str, start_epoch: int, end_epoch: int):
    doers = get_doers_list(driver=driver, start_epoch=start_epoch, end_epoch=end_epoch)
    the_board = {}

    for user in doers:
        user_report = make_report_seconds(
            driver=driver, doer=user, start_epoch=start_epoch, end_epoch=end_epoch
        )
        if user_report["Net Session Hours"] > 0:
            the_board[user] = user_report["Net Session Hours"]

    sorted_board = sorted(the_board.items(), key=lambda x: x[1], reverse=True)

    return sorted_board


# ✅
def get_status(driver: str, doer: str):
    doers_list = get_doers_list(driver, start_epoch=0, end_epoch=2147483647)
    if doer in doers_list:
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT kind, pendingid FROM pending_event WHERE doer = %s AND driver = %s ORDER BY ts DESC",
            (doer, driver),
        )
        all_pendings = cur.fetchall()
        cur.execute(
            "SELECT note FROM discord_event WHERE id >= %s AND doer = %s AND driver = %s ORDER BY ts DESC",
            (all_pendings[0][1], doer, driver),
        )
        note = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        if len(all_pendings) == 0:
            return "Offline"
        else:
            channel = note["channel"]
            return all_pendings[0][0] + "\nchannel: " + channel

    else:
        return "User Not Found!"


# ✅
def get_events(driver: str, start: int, end: int):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()
    cur.execute(
        """
                SELECT * From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                AND driver = %s
                ORDER BY epoch
                """,
        (start, end, driver),
    )
    result = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return result


# ✅
def get_events_of_doer(driver: str, start: int, end: int, doer: str):
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()
    cur.execute(
        """
                SELECT * From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                AND doer = %s
                AND driver = %s
                ORDER BY epoch
                """,
        (start, end, doer, driver),
    )
    result = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return result

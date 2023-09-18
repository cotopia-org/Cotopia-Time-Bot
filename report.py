import psycopg2
from persiantools.jdatetime import JalaliDateTime
import pytz
import datetime

def make_report (doer: str, start_epoch: int, end_epoch: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""
                SELECT * From discord_event
                WHERE pairid IS NOT NULL
                AND kind = ANY(ARRAY['SESSION STARTED', 'TALKING STARTED', 'SESSION PAUSED'])
                AND doer = %s
                AND epoch >= %s
                AND epoch <= %s
                ORDER BY id
                """, (doer, start_epoch, end_epoch))
    
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
        if (row[3] == 'SESSION STARTED'):
            sessions_count += 1
            total_session_duration = total_session_duration + row[9]
        elif (row[3] == 'SESSION PAUSED'):
            pausings_count += 1
            total_pausing_duration = total_pausing_duration + row[9]
        elif (row[3] == 'TALKING STARTED'):
            talkings_count += 1
            total_talking_duration = total_talking_duration + row[9]

    total_sd_hours = round((total_session_duration/3600), 1)
    total_pd_hours = round((total_pausing_duration/3600), 1)
    total_td_hours = round((total_talking_duration/3600), 1)
    
    on_mobile_hours = round((on_mobile_duration(doer, start_epoch, end_epoch, cur)/3600), 1)

    net_sd_hours = round((total_sd_hours - total_pd_hours - on_mobile_hours), 1)



    report_dic = {"User": doer,
                  "From": start_epoch,
                  "To": end_epoch,
                  "Number Of Rows": rows_count,
                  "Number Of Sessions": sessions_count,
                  "Number Of Pausings": pausings_count,
                  "Number Of Talkings": talkings_count,
                  "Number Of On Moblies": on_mobile_count(doer, start_epoch, end_epoch, cur),
                  "Raw Session Hours": total_sd_hours,
                  "Total Puasing Hours": total_pd_hours,
                  "Total Talking Hours": total_td_hours,
                  "On Mobile Hours": on_mobile_hours,
                  "Net Session Hours": net_sd_hours}
    
    # report = json.dumps(report_dic)

    conn.commit()
    cur.close()
    conn.close()

    return report_dic


def on_mobile_count(doer: str, start_epoch: int, end_epoch: int, cursor):
    cursor.execute("""
                SELECT COUNT(note->>'is_on_mobile') FROM discord_event
                WHERE doer = %s
                AND epoch >= %s
                AND epoch <= %s
                AND kind = 'SESSION STARTED'
                AND duration != -1
                AND note->>'is_on_mobile' = 'true'
                AND note->>'mobile_status' = 'online'
                """, (doer, start_epoch, end_epoch))
    number_of_on_mobile = cursor.fetchone()[0]
    if(number_of_on_mobile == None):
        return 0
    else:
        return number_of_on_mobile


def on_mobile_duration(doer: str, start_epoch: int, end_epoch: int, cursor):
    cursor.execute("""
                   SELECT SUM(duration) FROM discord_event
                   WHERE doer = %s
                   AND epoch >= %s
                   AND epoch <= %s
                   AND kind = 'SESSION STARTED'
                   AND duration != -1
                   AND note->>'is_on_mobile' = 'true'
                   AND note->>'mobile_status' = 'online'
                   """, (doer, start_epoch, end_epoch))
    
    duration_of_on_mobile = cursor.fetchone()[0]
    
    if(duration_of_on_mobile == None):
        return 0
    else:
        return duration_of_on_mobile


def make_raw_file(doer: str, start_epoch: int, end_epoch: int):

    from_date = JalaliDateTime.fromtimestamp(int(start_epoch), pytz.timezone("Asia/Tehran")).strftime("%c")
    to_date = JalaliDateTime.fromtimestamp(int(end_epoch), pytz.timezone("Asia/Tehran")).strftime("%c")

    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("""
                    SELECT * From discord_event
                    WHERE doer = %s
                    AND epoch >= %s
                    AND epoch <= %s
                    ORDER BY id
                    """, (doer, start_epoch, end_epoch))
        data = cur.fetchall()

        filename = doer + "_" + str(int(((start_epoch + end_epoch)/17)))
        reportfile = open("./rawreports/" + filename + ".txt", "w")
        reportfile.write("(id SERIAL NOT NULL PRIMARY KEY, ts TIMESTAMPTZ NOT NULL DEFAULT NOW(), epoch integer null, kind varchar(255) null, doer varchar(255) null, isPair boolean DEFAULT FALSE, pairID integer null, isValid boolean DEFAULT TRUE, note json null, duration integer DEFAULT -1)\n")
        reportfile.write("_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________\n")
        reportfile.write("doer = " + doer + "\nFrom: " + from_date + "\nTo: " + to_date + "\n" )
        reportfile.write("_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________\n")

        for row in data:
            reportfile.write(str(row)+"\n")

        filepath = "./rawreports/" + filename + ".txt"

        conn.commit()
        cur.close()
        conn.close()
        reportfile.close()

    except Exception as e:
        filepath = "./rawreports/error.log"
        print(e)


    return filepath


# def make_heat_map():
#     conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
#                         password="Tp\ZS?gfLr|]'a", port=5432)
#     cur = conn.cursor()


def get_doers_list(start_epoch: int, end_epoch: int):
    doers = []
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT DISTINCT doer From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                ORDER BY doer;
                """, (start_epoch, end_epoch))
    data = cur.fetchall()

    for row in data:
        if (row[0] != None):
            doers.append(row[0])

    conn.commit()
    cur.close()
    conn.close()

    return doers

# def get_starts_epochs(doer: str):
#     pass

# def get_stops_epochs(doer: str):
#     pass


# def get_hour(epoch: int):

#     jtime = JalaliDateTime.fromtimestamp(epoch, pytz.timezone("Asia/Tehran"))
#     return jtime.strftime("%H:%M")



def make_board(start_epoch: int, end_epoch: int):
    doers = []
    the_board = {}
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT DISTINCT doer From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                ORDER BY doer;
                """, (start_epoch, end_epoch))
    data = cur.fetchall()

    for row in data:
        if (row[0] != None and row[0] != "/today"):
            doers.append(row[0])

    for user in doers:
        user_report = make_report(doer=user, start_epoch=start_epoch, end_epoch=end_epoch)
        the_board[user] = user_report["Net Session Hours"]
    
    sorted_board = sorted(the_board.items(), key=lambda x: x[1], reverse=True) 
        

    conn.commit()
    cur.close()
    conn.close()

    return sorted_board




def get_status(doer: str):
    doers_list = get_doers_list(start_epoch=0, end_epoch=2147483647)
    if (doer in doers_list):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("SELECT kind, pendingid FROM pending_event WHERE doer = %s ORDER BY ts DESC", [doer])
        all_pendings = cur.fetchall()
        cur.execute("SELECT note FROM discord_event WHERE id >= %s ORDER BY ts DESC", [all_pendings[0][1]])
        note = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        if (len(all_pendings) == 0):
            return "Offline"
        else:
            channel = note["channel"]
            return all_pendings[0][0] + "\nchannel: " + channel 

    else:
        return "User Not Found!"
    

def get_events(start: int, end: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""
                SELECT * From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                ORDER BY epoch
                """, (start, end))
    result = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return result


def get_events_of_doer(start: int, end: int, doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""
                SELECT * From discord_event
                WHERE epoch >= %s
                AND epoch <= %s
                AND doer = %s
                ORDER BY epoch
                """, (start, end, doer))
    result = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return result
    





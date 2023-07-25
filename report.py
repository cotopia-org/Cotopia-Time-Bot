import psycopg2
import json


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

    total_sd_hours = round((total_session_duration/3600), 2)
    total_pd_hours = round((total_pausing_duration/3600), 2)
    total_td_hours = round((total_talking_duration/3600), 2)
    
    on_mobile_hours = round((on_mobile_duration(doer, start_epoch, end_epoch, cur)/3600), 2)

    net_sd_hours = round((total_sd_hours - total_pd_hours - on_mobile_hours), 2)



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
                   """, (doer, start_epoch, end_epoch))
    
    duration_of_on_mobile = cursor.fetchone()[0]
    
    if(duration_of_on_mobile == None):
        return 0
    else:
        return duration_of_on_mobile
    



def make_raw_file(doer: str, start_epoch: int, end_epoch: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    try:
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
        reportfile.write("doer = " + doer + "\nFrom: " + str(start_epoch)+ "\nTo: " + str(end_epoch) + "\n" )
        reportfile.write("_________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________\n")

        for row in data:
            reportfile.write(str(row)+"\n")

        filepath = "./rawreports/" + filename + ".txt"

    except:
        filepath = "./rawreports/error.log"


    conn.commit()
    cur.close()
    conn.close()
    reportfile.close()

    return filepath



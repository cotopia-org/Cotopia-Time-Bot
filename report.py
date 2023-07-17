import psycopg2
import json
from datetime import datetime



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
    net_sd_hours = total_sd_hours - total_pd_hours

    report_dic = {"User": doer,
                  "From": str(datetime.fromtimestamp(start_epoch)),
                  "To": str(datetime.fromtimestamp(end_epoch)),
                  "Number Of Rows": rows_count,
                  "Number Of Sessions": sessions_count,
                  "Number Of Pausings": pausings_count,
                  "Number Of Talkings": talkings_count,
                  "Raw Session Hours": total_sd_hours,
                  "Total Puasing Hours": total_pd_hours,
                  "Total Talking Hours": total_td_hours,
                  "Net Session Hours": net_sd_hours}
    
    report = json.dumps(report_dic)

    conn.commit()
    cur.close()
    conn.close()

    return report
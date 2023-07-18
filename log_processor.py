from discord import VoiceState, Member
import time
import psycopg2
import json






# def better_record(member: Member, before: VoiceState, after: VoiceState):
#     write_event_to_db(rightnow(), kind, str(member), isPair, note)

def record(member: Member, before: VoiceState, after: VoiceState, extra: dict):
    
    if (before.channel is None):
        # start new session
        session_start(member, after.channel.name, extra)
        if (after.self_deaf == True):
            # pause the session
            session_pause(member, after.channel.name, extra)
        elif (after.self_mute == False):
            talking_start(member, after.channel.name, extra)
        return
    elif (after.channel is None):
        # end session
        talking_stop(member, before.channel.name, extra)
        session_resume(member, before.channel.name, extra)
        session_end(member, before.channel.name, extra)
        return

    if (before.channel != after.channel):
        # channel changed
        channel_change(member, after.channel.name, extra)
    elif (before.channel == after.channel):
        # mute or defen changed
        if (before.self_deaf == False and after.self_deaf == True):
            if (before.self_mute == False):
                talking_stop(member, after.channel.name, extra)
            session_pause(member, after.channel.name, extra)
        elif (before.self_deaf == True and after.self_deaf == False):
            if (after.self_mute == False):
                talking_start(member, after.channel.name, extra)
            session_resume(member, after.channel.name, extra)
        elif (before.self_mute == True and after.self_mute == False):
            talking_start(member, after.channel.name, extra)
        elif (before.self_mute == False and after.self_mute == True):
            talking_stop(member, after.channel.name, extra)    
            
    return


def session_start(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print ('SESSION STARTED')
    pendingID = write_event_to_db(rightnow(), "SESSION STARTED", str(m), True, note)
    write_pending_to_db(str(m), "SESSION STARTED", pendingID)

def session_end(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print ('SESSION ENDED')
    stop = write_event_to_db(rightnow(), "SESSION ENDED", str(m), True, note)
    print("stop:    "+ str(stop))
    start = get_pair_start_id(str(m), "SESSION STARTED")
    print("start:   "+ str(start))
    if (start != -1):
        add_pairid_to_db(start, stop)
    delete_all_pending_from_db(str(m))


def session_pause(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print('DEAFENED')
    print ('SESSION PAUSED')
    pendingID = write_event_to_db(rightnow(), "SESSION PAUSED", str(m), True, note)
    write_pending_to_db(str(m), "SESSION PAUSED", pendingID)

def session_resume(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print('UNDEAFENED')
    print ('SESSION RESUMED')
    stop = write_event_to_db(rightnow(), "SESSION RESUMED", str(m), True, note)
    start = get_pair_start_id(str(m), "SESSION PAUSED")
    if (start != -1):
        add_pairid_to_db(start, stop)


def channel_change(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print ('CHANEL CHANGED')
    write_event_to_db(rightnow(), "CHANEL CHANGED", str(m), False, note)


def talking_start(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print('UNMUTED')
    print('TALKING STARTED')
    pendingID = write_event_to_db(rightnow(), "TALKING STARTED", str(m), True, note)
    write_pending_to_db(str(m), "TALKING STARTED", pendingID)


def talking_stop(m: Member, channel: str, e: dict):
    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    stop = write_event_to_db(rightnow(), "TALKING STOPPED", str(m), True, note)
    start = get_pair_start_id(str(m), "TALKING STARTED")
    if (start != -1):
        add_pairid_to_db(start, stop)
    print('MUTED')
    print('TALKING STOPPED')



def rightnow():
    epoch = int(time.time())
    return epoch

def write_event_to_db(epoch: int, kind: str, doer: str, isPair: bool, note: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS discord_event(
            id SERIAL NOT NULL PRIMARY KEY,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            epoch integer null,
            kind varchar(255) null,
            doer varchar(255) null,
            isPair boolean DEFAULT FALSE,
            pairID integer null,
            isValid boolean DEFAULT TRUE,
            duration integer DEFAULT -1,
            note json null);""")
    cur.execute("INSERT INTO discord_event (epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (epoch, kind, doer, isPair, note))
    id_of_added_row = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return id_of_added_row

def write_pending_to_db(doer: str, kind: str, pendingID: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS pending_event(
            id SERIAL NOT NULL PRIMARY KEY,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            doer varchar(255) null,
            kind varchar(255) null,
            pendingID integer null);""")
    cur.execute("INSERT INTO pending_event (doer, kind, pendingID) VALUES (%s, %s, %s);",
                 (doer, kind, pendingID))
    conn.commit()
    cur.close()
    conn.close()
    
    

def add_pairid_to_db(start: int, stop: int):

    # print("start    :" +str(start))
    # print("stop    :" +str(stop))
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (start, stop))
    cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (stop, start))

    cur.execute("SELECT epoch From discord_event WHERE id = ANY(ARRAY[%s, %s]) ORDER BY id;", (start, stop))
    epochs = cur.fetchall()

    duration = epochs[1][0] - epochs[0][0]
    # print("epoches: " + str(epochs))
    # print("duration "+ str(duration))
    cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, start))
    cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, stop))

    conn.commit()
    cur.close()
    conn.close()


# Returns -1 if not found
def get_pair_start_id(doer: str, kind: str):
    pair_start_id = 0
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS pending_event(
            id SERIAL NOT NULL PRIMARY KEY,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            doer varchar(255) null,
            kind varchar(255) null,
            pendingID integer null);""")
    cur.execute("SELECT pendingid FROM pending_event WHERE doer = %s AND kind = %s;", (doer, kind))

    result = cur.fetchone()

    if (result == None):
        print("no pending found!")
        conn.commit()
        cur.close()
        conn.close()
        return -1
    
    else:
        pair_start_id = result[0]
        cur.execute(f"DELETE FROM pending_event WHERE pendingid = {pair_start_id};")
        conn.commit()
        cur.close()
        conn.close()
        return pair_start_id

def delete_all_pending_from_db(doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("DELETE FROM pending_event WHERE doer = %s;", [doer])
    conn.commit()
    cur.close()
    conn.close()

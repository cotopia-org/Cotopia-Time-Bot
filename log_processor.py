from discord import VoiceState, Member, VoiceChannel
import time
import psycopg2
import json


# the discord bot calls this on_voice_state_update
# it checks the event kind
# and calls the methods of each kind when needed
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
        talking_stop(member, before.channel.name, extra, True)
        session_resume(member, before.channel.name, extra, True)
        session_end(member, before.channel.name, extra)
        return

    if (before.channel != after.channel):
        # channel changed
        channel_change(member, after.channel, extra)
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


# 🚗
def session_start(m: Member, channel: str, e: dict):
    # when a session starts, we expect that there is no "SESSION STARTED"
    # in the pending_event table, logically
    # so if we have one in there, there must be an error that we need to fix now
    if ("SESSION STARTED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        print("unexpected session start is pending. Adding session end before it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        stop = write_event_to_db(str(m.guild.id), rightnow(), "SESSION ENDED", str(m), True, note)
        start = get_pair_start_id(str(m.guild.id), str(m), "SESSION STARTED")
        if (start != -1):
            add_pairid_to_db(start, stop)
        delete_all_pending_from_db(str(m.guild.id), str(m))

    notedic = {"channel": channel}
    notedic = notedic | e
    note = json.dumps(notedic)
    print ('SESSION STARTED')
    pendingID = write_event_to_db(str(m.guild.id), rightnow(), "SESSION STARTED", str(m), True, note)
    write_pending_to_db(str(m.guild.id), str(m), "SESSION STARTED", pendingID)


# 🚗
def session_end(m: Member, channel: str, e: dict):
    # when we receive a session end, we expect a "SESSION STARTED" in pendings
    if ("SESSION STARTED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        print ('SESSION ENDED')
        stop = write_event_to_db(str(m.guild.id), rightnow(), "SESSION ENDED", str(m), True, note)
        print("stop:    "+ str(stop))
        start = get_pair_start_id(str(m.guild.id), str(m), "SESSION STARTED")
        print("start:   "+ str(start))
        if (start != -1):
            add_pairid_to_db(start, stop)
        delete_all_pending_from_db(str(m.guild.id), str(m))
    else:
        print("unexpected session end is received. Adding session start for it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        start = write_event_to_db(str(m.guild.id), rightnow(), "SESSION STARTED", str(m), True, note)
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        print ('SESSION ENDED')
        stop = write_event_to_db(str(m.guild.id), rightnow(), "SESSION ENDED", str(m), True, note)
        add_pairid_to_db(start, stop)
        delete_all_pending_from_db(str(m.guild.id), str(m))


# 🚗
def session_pause(m: Member, channel: str, e: dict):
    # when we receive a session pause, we expect a "SESSION STARTED" in pendings
    if ("SESSION STARTED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        print('DEAFENED')
        print ('SESSION PAUSED')
        # renew to fix that edge case, when user starts a session before midnight and pauses it,
        # after midnight, it causes negative raw session hours for that next day
        renew_pendings_of_a_doer(driver=str(m.guild.id), doer=str(m))
        pendingID = write_event_to_db(str(m.guild.id), rightnow(), "SESSION PAUSED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "SESSION PAUSED", pendingID)
    else:
        print("unexpected session pause is received. Adding session start for it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        start_pendingID = write_event_to_db(str(m.guild.id), rightnow(), "SESSION STARTED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "SESSION STARTED", start_pendingID)
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        pause_pendingID = write_event_to_db(str(m.guild.id), rightnow(), "SESSION PAUSED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "SESSION PAUSED", pause_pendingID)


# 🚗
def session_resume(m: Member, channel: str, e: dict, comes_from_s_end: bool | None = None):
    # when we receive a session resume, we expect a "SESSION PAUSED" in pendings
    if ("SESSION PAUSED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        print('UNDEAFENED')
        print ('SESSION RESUMED')
        stop = write_event_to_db(str(m.guild.id), rightnow(), "SESSION RESUMED", str(m), True, note)
        start = get_pair_start_id(str(m.guild.id), str(m), "SESSION PAUSED")
        if (start != -1):
            add_pairid_to_db(start, stop)
    else:
        if (comes_from_s_end == True):
            return
        print("unexpected session resume is received. Adding session pause for it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        start = write_event_to_db(str(m.guild.id), rightnow(), "SESSION PAUSED", str(m), True, note)
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        stop = write_event_to_db(str(m.guild.id), rightnow(), "SESSION RESUMED", str(m), True, note)
        add_pairid_to_db(start, stop)


# 🚗
def channel_change(m: Member, channel: VoiceChannel, e: dict):
    notedic = {
        "channel": {
            "name": channel.name,
            "id": channel.id
            }
        }
    notedic = notedic | e
    note = json.dumps(notedic)
    print ('CHANNEL CHANGED')
    write_event_to_db(str(m.guild.id), rightnow(), "CHANNEL CHANGED", str(m), False, note)


# 🚗
def talking_start(m: Member, channel: str, e: dict):
    # when we receive a talking start, we expect a "SESSION STARTED" in pendings
    if ("SESSION STARTED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        print('UNMUTED')
        print('TALKING STARTED')
        pendingID = write_event_to_db(str(m.guild.id), rightnow(), "TALKING STARTED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "TALKING STARTED", pendingID)
    else:
        print("unexpected talking start is received. Adding session start for it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        start_pendingID = write_event_to_db(str(m.guild.id), rightnow(), "SESSION STARTED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "SESSION STARTED", start_pendingID)
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        talk_pendingID = write_event_to_db(str(m.guild.id), rightnow(), "TALKING STARTED", str(m), True, note)
        write_pending_to_db(str(m.guild.id), str(m), "TALKING STARTED", talk_pendingID)


# 🚗
def talking_stop(m: Member, channel: str, e: dict, comes_from_s_end: bool | None = None):
    # when we receive a talking stop, we expect a "TALKING STARTED" in pendings
    if ("TALKING STARTED" in get_pendings(driver=str(m.guild.id), doer=str(m))):
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        stop = write_event_to_db(str(m.guild.id), rightnow(), "TALKING STOPPED", str(m), True, note)
        start = get_pair_start_id(str(m.guild.id), str(m), "TALKING STARTED")
        if (start != -1):
            add_pairid_to_db(start, stop)
        print('MUTED')
        print('TALKING STOPPED')
    else:
        if (comes_from_s_end ==  True):
            return
        print("unexpected talking stop is received. Adding talking start for it!")
        notedic = {"NOTE": "Automatically added to fix an error in data!"}
        note = json.dumps(notedic)
        start = write_event_to_db(str(m.guild.id), rightnow(), "TALKING STARTED", str(m), True, note)
        notedic = {"channel": channel}
        notedic = notedic | e
        note = json.dumps(notedic)
        stop = write_event_to_db(str(m.guild.id), rightnow(), "TALKING STOPPED", str(m), True, note)
        add_pairid_to_db(start, stop)





# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch

# CREATES TABLE IF NOT EXISTS
# INSERTS INTO discord_event (epoch, kind, doer, isPair, note)
# retuns the id of the added row
# 🚗
def write_event_to_db(driver: str, epoch: int, kind: str, doer: str, isPair: bool, note: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS discord_event(
            id SERIAL NOT NULL PRIMARY KEY,
            driver VARCHAR(255) null,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            epoch integer null,
            kind varchar(255) null,
            doer varchar(255) null,
            isPair boolean DEFAULT FALSE,
            pairID integer null,
            isValid boolean DEFAULT TRUE,
            duration integer DEFAULT -1,
            note json null);""")
    cur.execute("INSERT INTO discord_event (driver, epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    (driver, epoch, kind, doer, isPair, note))
    id_of_added_row = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return id_of_added_row

# CREATES TABLE IF NOT EXISTS pending_event
# should be replaced with redis or something
# INSERTS INTO pending_event (doer, kind, pendingID)
# 🚗
def write_pending_to_db(driver: str, doer: str, kind: str, pendingID: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS pending_event(
            id SERIAL NOT NULL PRIMARY KEY,
            driver VARCHAR(255) null,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            doer varchar(255) null,
            kind varchar(255) null,
            pendingID integer null);""")
    cur.execute("INSERT INTO pending_event (driver, doer, kind, pendingID) VALUES (%s, %s, %s, %s);",
                 (driver, doer, kind, pendingID))
    conn.commit()
    cur.close()
    conn.close()


# adds pairID to events, both starting and ending event.
# calculates duration time in seconds and writes it to both starting and ending event
# 🚗
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


# CREATES TABLE IF NOT EXISTS pending_event
# finds and returns the starting pair id from pendings
# if found, deletes the pending row
# returns -1 if not found
# 🚗
def get_pair_start_id(driver: str, doer: str, kind: str):
    pair_start_id = 0
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS pending_event(
            id SERIAL NOT NULL PRIMARY KEY,
            driver VARCHAR(255) null,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            doer varchar(255) null,
            kind varchar(255) null,
            pendingID integer null);""")
    cur.execute("SELECT pendingid FROM pending_event WHERE doer = %s AND kind = %s AND driver = %s;", (doer, kind, driver))

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


# deletes all the pendings of a doer from pending_event table
# 🚗
def delete_all_pending_from_db(driver: str, doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("DELETE FROM pending_event WHERE doer = %s AND driver = %s;", (doer, driver))
    conn.commit()
    cur.close()
    conn.close()


# we need a function that gets all the pendings, finish them and renew them!
# this would be used to produce live /today report
# 🚗
def renew_pendings(driver: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    renew_epoch = rightnow()

    cur.execute("INSERT INTO discord_event (driver, epoch, kind, doer, isPair) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (driver, renew_epoch, "PENDING RENEW", "/today", True))
    id_of_slash_today_row = cur.fetchone()[0]


    cur.execute(f"SELECT * FROM pending_event WHERE driver = '{driver}'")
    current_pendings = cur.fetchall()


    for each in current_pendings:
        cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (id_of_slash_today_row, each[4]))

        cur.execute("SELECT epoch FROM discord_event WHERE id = %s", [each[4]])
        pending_epoch = cur.fetchone()[0]

        duration = renew_epoch - pending_epoch
        cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, each[4]))

        cur.execute("DELETE FROM pending_event WHERE id = %s", [each[0]])

        
        #readd the event
        cur.execute("SELECT * FROM discord_event WHERE id = %s", [each[4]])
        old_event = cur.fetchone()
        notedic = old_event[8]
        notedic["renew"] = "Renewed Automatically by renew_pendings()"
        note = json.dumps(notedic)
        cur.execute("INSERT INTO discord_event (driver, epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    (driver, renew_epoch, old_event[3], old_event[4], old_event[5], note))
        id_of_renewed_event = cur.fetchone()[0]
        
        # readd the pending
        cur.execute("INSERT INTO pending_event (driver, doer, kind, pendingID) VALUES (%s, %s, %s, %s);",
                 (driver, each[2], each[3], id_of_renewed_event))


    conn.commit()
    cur.close()
    conn.close()



def renew_pendings_of_a_doer(driver: str, doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    renew_epoch = rightnow()

    cur.execute("INSERT INTO discord_event (driver, epoch, kind, doer, isPair) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (driver, renew_epoch, "PENDING RENEW", "/today", True))
    id_of_slash_today_row = cur.fetchone()[0]


    cur.execute(f"SELECT * FROM pending_event WHERE driver = '{driver}' AND doer = '{doer}'")
    current_pendings = cur.fetchall()


    for each in current_pendings:
        cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (id_of_slash_today_row, each[4]))

        cur.execute("SELECT epoch FROM discord_event WHERE id = %s", [each[4]])
        pending_epoch = cur.fetchone()[0]

        duration = renew_epoch - pending_epoch
        cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, each[4]))

        cur.execute("DELETE FROM pending_event WHERE id = %s", [each[0]])

        
        #readd the event
        cur.execute("SELECT * FROM discord_event WHERE id = %s", [each[4]])
        old_event = cur.fetchone()
        notedic = old_event[8]
        notedic["renew"] = "Renewed Automatically by renew_pendings()"
        note = json.dumps(notedic)
        cur.execute("INSERT INTO discord_event (driver, epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    (driver, renew_epoch, old_event[3], old_event[4], old_event[5], note))
        id_of_renewed_event = cur.fetchone()[0]
        
        # readd the pending
        cur.execute("INSERT INTO pending_event (driver, doer, kind, pendingID) VALUES (%s, %s, %s, %s);",
                 (driver, each[2], each[3], id_of_renewed_event))


    conn.commit()
    cur.close()
    conn.close()



def get_pendings(driver: str, doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM pending_event WHERE driver = '{driver}' AND doer = '{doer}'")
    current_pendings = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    result = []
    if (current_pendings == None):
        return result
    else:
        for i in current_pendings:
            result.append(i[3])
        return result

# from discord import VoiceState, Member
import time
import db



# def ask4brief(member: Member, before: VoiceState, after: VoiceState):
#     if (before.channel is None):
#         pass

def should_record_brief(doer: str):
    last = get_last_brief_epoch(doer)
    if (last == -1):
        return True
    now = rightnow()
    dif = now - last
    print(f"last recorded brief for '{doer}' was from {dif} seconds ago")
    if (dif > 7200):
        return True
    else:
        return False

def get_last_brief(doer: str):
    db.cur.execute("""
                   SELECT content FROM brief
                   WHERE doer = %s
                   ORDER BY ts DESC;
                   """, [doer])
    
    result = db.cur.fetchone()

    if (result == None):
        print("no brief found!")
        db.conn.commit()
        db.cur.close()
        db.conn.close()
        return "N/A"
    else:
        db.conn.commit()
        db.cur.close()
        db.conn.close()
        return result[0]


def get_last_brief_epoch(doer: str):
    db.cur.execute("""
                   SELECT epoch FROM brief
                   WHERE doer = %s
                   ORDER BY epoch DESC;
                   """, [doer])
    
    result = db.cur.fetchone()

    if (result == None):
        print("no brief found!")
        db.conn.commit()
        db.cur.close()
        db.conn.close()
        return -1
    else:
        db.conn.commit()
        db.cur.close()
        db.conn.close()
        return result[0]


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch

def write_to_db(brief: str, doer: str):
    db.cur.execute("""CREATE TABLE IF NOT EXISTS brief(
            id SERIAL NOT NULL PRIMARY KEY,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            epoch INTEGER null,
            doer VARCHAR(255) null,
            content TEXT null);""")
    db.cur.execute("INSERT INTO brief (epoch, doer, content) VALUES (%s, %s, %s);",
                 (rightnow(), doer, brief))
    
    db.conn.commit()
    db.cur.close()
    db.conn.close()


# text = """very new ut perspiciatis, unde omnis iste 
# natus error sit voluptatem accusantium doloremque 
# laudantium, totam rem aperiam eaque ipsa, quae
# """
# write_to_db(brief=text, doer="ali")

# print(should_record_brief("yo"))

# print(type(get_last_brief("ali")))

# print(type(get_last_brief_epoch("yo")))

# print(rightnow())

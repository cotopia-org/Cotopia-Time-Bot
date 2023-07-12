from discord import VoiceState, Member
from datetime import datetime
import time

def record(member: Member, before: VoiceState, after: VoiceState):
    
    if (before.channel is None):
        # start new session
        session_start(member, after.channel.name)
        if (after.self_deaf == True):
            # pause the session
            session_pause(member, after.channel.name)
        return
    elif (after.channel is None):
        # end session
        session_end(member, before.channel.name)
        return

    if (before.channel != after.channel):
        # channel changed
        channel_change(member, after.channel.name)
    elif (before.channel == after.channel):
        # mute or defen changed
        if (before.self_deaf == False and after.self_deaf == True):
            session_pause(member, after.channel.name)
        elif (before.self_deaf == True and after.self_deaf == False):
            session_resume(member, after.channel.name)
        elif (before.self_mute == True and after.self_mute == False):
            talking_start(member, after.channel.name)
        elif (before.self_mute == False and after.self_mute == True):
            talking_stop(member, after.channel.name)    
            
    return

def session_start(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print ('SESSION STARTED')
    f.write(str(rightnow())+"   "+"SESSION STARTED"+"   "+ channel+"\n")
    f.close()

def session_end(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print ('SESSION ENDED')
    f.write(str(rightnow())+"   "+"SESSION ENDED"+"   "+ channel+"\n")
    f.close()

def session_pause(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print('DEAFENED')
    print ('SESSION PAUSED')
    f.write(str(rightnow())+"   "+"SESSION PAUSED"+"   "+ channel+"\n")
    f.close()

def session_resume(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print('UNDEAFENED')
    print ('SESSION RESUMED')
    f.write(str(rightnow())+"   "+"SESSION RESUMED"+"   "+ channel+"\n")
    f.close()

def channel_change(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print ('CHANEL CHANGED')
    f.write(str(rightnow())+"   "+"CHANEL CHANGED"+"   "+ channel+"\n")
    f.close()

def talking_start(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print('UNMUTED')
    print('TALKING STARTED')
    f.write(str(rightnow())+"   "+"TALKING STARTED"+"   "+ channel+"\n")
    f.close()

def talking_stop(m: Member, channel: str):
    f = open("{filename}.txt".format(filename = str(m)), "a")
    print('MUTED')
    print('TALKING STOPPED')
    f.write(str(rightnow())+"   "+"TALKING STOPPED"+"   "+ channel+"\n")
    f.close()

def rightnow():
    epoch = int(time.time())
    return epoch
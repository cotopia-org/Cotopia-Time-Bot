from discord import VoiceState, Member
from datetime import datetime
import time

def process(member: Member, before: VoiceState, after: VoiceState):
    
    if (before.channel is None):
        # start new session
        session_start(member)
        if (after.self_deaf == True):
            # pause the session
            session_pause(member)
        return
    elif (after.channel is None):
        # end session
        session_end(member)
        return

    if (before.channel != after.channel):
        # channel changed
        channel_change(member)
    elif (before.channel == after.channel):
        # mute or defen changed
        if (before.self_deaf == False and after.self_deaf == True):
            session_pause(member)
        elif (before.self_deaf == True and after.self_deaf == False):
            session_resume(member)
        elif (before.self_mute == True and after.self_mute == False):
            talking_start(member)
        elif (before.self_mute == False and after.self_mute == True):
            talking_stop(member)    
            
    return

def session_start(m: Member):
    print ('SESSION STARTED')

def session_end(m: Member):
    print ('SESSION ENDED')

def session_pause(m: Member):
    print('DEAFENED')
    print ('SESSION PAUSED')

def session_resume(m: Member):
    print('UNDEAFENED')
    print ('SESSION RESUMED')

def channel_change(m: Member):
    print ('CHANEL CHANGED')

def talking_start(m: Member):
    print('UNMUTED')
    print('TALKING STARTED')

def talking_stop(m: Member):
    print('MUTED')
    print('TALKING STOPPED')

def rightnow():
    epoch = int(time.time())
    return epoch
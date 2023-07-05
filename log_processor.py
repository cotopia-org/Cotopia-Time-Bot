from discord import VoiceState, Member
from datetime import datetime

def process(member: Member, before: VoiceState, after: VoiceState):
    
    if (before.channel is None):
        # start new session
        print ('SESSION STARTED')
        if (after.self_deaf == True):
            # puase the session
            print ('SESSION PAUSED')
        return
    
    elif (after.channel is None):
        # end session
        print ('SESSION ENDED')
        return

    if (before.channel != after.channel):
        # channel changed
        print ('CHANEL CHANGED')
    elif (before.channel == after.channel):
        # mute or defen changed
        if (before.self_deaf == False and after.self_deaf == True):
            print('DEAFENED')
        elif (before.self_deaf == True and after.self_deaf == False):
            print('UNDEAFENED')
        elif (before.self_mute == True and after.self_mute == False):
            print('UNMUTED')
        elif (before.self_mute == False and after.self_mute == True):
            print('MUTED')    

    return

def session_start():
    return
def session_end():
    return
def session_puased():
    return
def session_resumed():
    return
def channel_changed():
    return
def talking_start():
    return
def talking_stop():
    return
from datetime import datetime
from discord import VoiceState, Member
import time


def record(member: Member, before: VoiceState, after: VoiceState):
    f = open("raw_logs.txt", "a")
    f.write(str(member.guild.id) + "  " + str(rightnow()) + "  " + str(datetime.now()) + "  " + str(member) + " " + str(before) + " " + str(after) + "\n")
    f.close()


def rightnow():
    epoch = int(time.time())
    return epoch
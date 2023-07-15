
def makefiles(username: str):
    sessionfile = open("./plogs/"+username+"_session.txt", "a")
    pausefile = open("./plogs/"+username+"_pause.txt", "a")
    talkingfile = open("./plogs/"+username+"_talking.txt", "a")
    channelchangefile = open("./plogs/"+username+"_channels.txt", "a")
    with open("./oldlogs/"+username+".txt") as file:
        while line := file.readline():
            if "SESSION STARTED" in line:
                sessionfile.write(line)
            elif "SESSION ENDED" in line:
                sessionfile.write(line)
            elif "TALKING STARTED" in line:
                talkingfile.write(line)
            elif "TALKING STOPPED" in line:
                talkingfile.write(line)
            elif "SESSION PAUSED" in line:
                pausefile.write(line)
            elif "SESSION RESUMED" in line:
                pausefile.write(line)
            elif "CHANEL CHANGED" in line:
                channelchangefile.write(line)


    sessionfile.close()
    pausefile.close()
    talkingfile.close()
    channelchangefile.close()

def duration_calculator(username: str):
    s_start, s_stop, p_start, p_stop, t_start, t_stop = 0,0,0,0,0,0
    sessionfile = open("./plogs/"+username+"_session.txt", "r")
    pausefile = open("./plogs/"+username+"_pause.txt", "r")
    talkingfile = open("./plogs/"+username+"_talking.txt", "r")

    s_duration = open("./plogs/"+username+"_s_duration.txt", "a")
    p_duration = open("./plogs/"+username+"_p_duration.txt", "a")
    t_duration = open("./plogs/"+username+"_t_duration.txt", "a")

    while line := sessionfile.readline():
        if "SESSION STARTED" in line:
            slices = line.split("   ")
            s_start = int(slices[0])
        elif "SESSION ENDED" in line:
            slices = line.split("   ")
            s_stop = int(slices[0])
            duration = s_stop - s_start
            s_duration.write(str(s_start)+"||"+str(s_stop)+"||"+str(duration)+"\n")
    
    while line := pausefile.readline():
        if "SESSION PAUSED" in line:
            slices = line.split("   ")
            p_start = int(slices[0])
        elif "SESSION RESUMED" in line:
            slices = line.split("   ")
            p_stop = int(slices[0])
            duration = p_stop - p_start
            p_duration.write(str(p_start)+"||"+str(p_stop)+"||"+str(duration)+"\n")
    
    while line := talkingfile.readline():
        if "TALKING STARTED" in line:
            slices = line.split("   ")
            t_start = int(slices[0])
        elif "TALKING STOPPED" in line:
            slices = line.split("   ")
            t_stop = int(slices[0])
            duration = t_stop - t_start
            t_duration.write(str(t_start)+"||"+str(t_stop)+"||"+str(duration)+"\n")
    
    sessionfile.close()
    pausefile.close()
    talkingfile.close()
    s_duration.close()
    p_duration.close()
    t_duration.close()

def line_counter(username: str):
    s_duration = open("./plogs/"+username+"_s_duration.txt", "r")
    p_duration = open("./plogs/"+username+"_p_duration.txt", "r")
    t_duration = open("./plogs/"+username+"_t_duration.txt", "r")

    report = open("./plogs/reports/"+username+".report", "a")

    num_lines = sum(1 for _ in s_duration)
    report.write("Number of sessions:   "+str(num_lines)+"\n")
    num_lines = sum(1 for _ in p_duration)
    report.write("Number of pausings:   "+str(num_lines)+"\n")
    num_lines = sum(1 for _ in t_duration)
    report.write("Number of talkings:   "+str(num_lines)+"\n")

    s_duration.close()
    p_duration.close()
    t_duration.close()
    report.close()


def duration_sum(username:str):
    s_duration = open("./plogs/"+username+"_s_duration.txt", "r")
    p_duration = open("./plogs/"+username+"_p_duration.txt", "r")
    t_duration = open("./plogs/"+username+"_t_duration.txt", "r")
    report = open("./plogs/reports/"+username+".report", "a")


    sumS = 0
    while line := s_duration.readline():
        s = line.split("||")
        sumS = sumS + int(s[2])
    sumS = sumS/3600
    r = round(sumS, 2)
    report.write("Total session duration(hours):   "+str(r)+"\n")

    sumP = 0
    while line := p_duration.readline():
        s = line.split("||")
        sumP = sumP + int(s[2])
    sumP = sumP/3600
    r = round(sumP, 2)
    report.write("Total pausing duration(hours):   "+str(r)+"\n")

    sumT = 0
    while line := t_duration.readline():
        s = line.split("||")
        sumT = sumT + int(s[2])
    sumT = sumT/3600
    r = round(sumT, 2)
    report.write("Total talking duration(hours):   "+str(r)+"\n")

    billable = 0



    s_duration.close()
    p_duration.close()
    t_duration.close()
    report.close()


# makefiles("navid.madadi")
# duration_calculator("ajabimahdi")
# line_counter("ajabimahdi")
# duration_sum("ajabimahdi")
import report
from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
import pytz



def today_jalali():
    the_string = str(JalaliDate.today())
    slices = the_string.split("-")
    dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
    return dic

now = today_jalali()
start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-14, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-14, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )

discordDate_from = JalaliDateTime.fromtimestamp(start_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")
discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

the_board = report.make_board(start_epoch, end_epoch)


text = ("Net Session Hours\n\n" +
        "From: " + discordDate_from + "\n" +
        "To: " + discordDate_to + "\n" +
        "------------------------------\n")
for l in the_board:
    string = str(l)
    string = string.replace("('", "")
    string = string.replace("',", " :")
    string = string.replace(")", "")
    text = text + string + "\n"
            

print(text)
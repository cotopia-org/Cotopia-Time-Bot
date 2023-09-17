import log_processor
from persiantools.jdatetime import JalaliDateTime
from persiantools.jdatetime import JalaliDate
import pytz
import report


def today_jalali():
    the_string = str(JalaliDate.today())
    slices = the_string.split("-")
    dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
    return dic


log_processor.renew_pendings()

now = today_jalali()
start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
the_board = report.make_board(start_epoch, end_epoch)

title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
for l in the_board:
            string = str(l) 
            string = string.replace("('", "")
            string = string.replace("',", " :")
            string = string.replace(")", "")
            text = text + string + "\n"

print(text)
from fastapi import FastAPI
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

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/thismonth")
async def thismonth():
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
    text = ("Net Session Hours of " +
            str(title_date) +
            "\n------------------------------\n")
    for l in the_board:
                string = str(l)
                string = string.replace("('", "")
                string = string.replace("',", " :")
                string = string.replace(")", "")
                text = text + string + "\n"

    return text


@app.get("/events")
async def getevents(start: int, end: int):
      
      all = report.get_events(start=start, end=end)
      answer = []

      for event in all:
            d = {}
            d["id"] = event[0]
            d["ts"] = event[1]
            d["epoch"] = event[2]
            d["kind"] = event[3]
            d["doer"] = event[4]
            d["ispair"] = event[5]
            d["pairid"] = event[6]
            d["isvalid"] = event[7]
            d["note"] = event[8]
            d["duration"] = event[9]
            answer.append(d)
      
      return answer
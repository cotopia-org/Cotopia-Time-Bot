from fastapi import FastAPI, Request
from starlette.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(
    title="TimeMaster",
    description="A tool for recording and processing events.",
    version="0.0.42",
    contact={
        "name": "Ali Kharrati (developer)",
        "email": "ali.kharrati+timemaster@gmail.com",
    },
    servers=[
        {"url": "https://tmaster.ir", "description": "Staging environment"},
        {"url": "http://127.0.0.1:8000", "description": "Local environment"},
    ]
)

origins = [
    "https://tmaster.ir",
    "https://tmaster.ir/",
    "https://time-master-eight.vercel.app/",
    "https://time-master-eight.vercel.app",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8787",
    "http://127.0.0.1:8787",
    "http://localhost:8787/",
    "http://127.0.0.1:8787/",
    "http://localhost:8080/",
    "http://127.0.0.1:8080/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
async def root():
    return {"message": "https://tmaster.ir/docs"}

@app.get("/doers")
async def get_doers(start: int, end: int):
      return report.get_doers_list(driver="1125764070935638086", start_epoch=start, end_epoch=end)

@app.get("/thismonth")
async def this_month():

    log_processor.renew_pendings(driver="1125764070935638086", )

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
            
    the_board = report.make_board(driver="1125764070935638086", start_epoch=start_epoch, end_epoch=end_epoch)
    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
    title = "Net Session Hours of " + str(title_date)
    result = {}
    result["The Board Title"] = title

    for l in the_board:
                result[l[0]] = l[1]
                
    return result


@app.get("/events")
async def get_events(start: int, end: int, doer: str | None = None):
      
    if (doer == None):
        all = report.get_events(driver="1125764070935638086", start=start, end=end)
    else:
        all = report.get_events_of_doer(driver="1125764070935638086", start=start, end=end, doer=doer)
    

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
            d["driver"] = event[10]
            answer.append(d)
      
    return answer

@app.get("/goauth")
async def google_oauth(code: str, request: Request):
      # TO-DO
      # Handle no code response

      discord_id = request.cookies.get('discord_id')
      print("discord_id:    " + str(discord_id))
      guild_id = request.cookies.get('guild_id')
      print("guild_id:    " + str(guild_id))
      return code

@app.get("/gcal")
async def google_oauth():
      return FileResponse('static/gcal.html')
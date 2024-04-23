import json
from enum import Enum as pyEnum

import pytz
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from persiantools.jdatetime import JalaliDate, JalaliDateTime, timedelta
from starlette.responses import FileResponse

import auth
import log_processor
import report
from gcal import calcal as GCalSetup
from job_report.report import gen_user_report
from person import Person
from server import Server


class ReportInBetween(pyEnum):
    off = "off"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


app = FastAPI(
    title="TimeMaster",
    description="A tool for recording and processing events.",
    version="0.0.52",
    contact={
        "name": "Ali Kharrati (developer)",
        "email": "ali.kharrati+timemaster@gmail.com",
    },
    servers=[
        {
            "url": "https://time-api.cotopia.social",
            "description": "Staging environment",
        },
        {"url": "http://127.0.0.1:8000", "description": "Local environment"},
    ],
)

origins = [
    "https://time-bot.cotopia.social",
    "https://time-bot.cotopia.social/",
    "https://time-api.cotopia.social",
    "https://time-api.cotopia.social/",
    "https://time-master-eight.vercel.app/",
    "https://time-master-eight.vercel.app",
    "https://cotopia-bot-manager.vercel.app/",
    "https://cotopia-bot-manager.vercel.app",
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
    return "Visit https://time-api.cotopia.social/docs"


@app.get("/doers")
async def get_doers(start: int, end: int, request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])

    doers = report.get_doers_list(driver=driver, start_epoch=start, end_epoch=end)
    result = {}
    person = Person()
    for each in doers:
        if "#" in each:
            s = each.split("#", 1)
            result[each] = person.get_person_info(driver, s[0])
        else:
            result[each] = person.get_person_info(driver, each)

    return result


@app.get("/makeboard")
async def make_board(start_epoch: int, end_epoch: int, request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])

    log_processor.renew_pendings(driver=driver)

    the_board = report.make_board_seconds(
        driver=driver, start_epoch=start_epoch, end_epoch=end_epoch
    )
    from_date = JalaliDateTime.fromtimestamp(start_epoch)
    to_date = JalaliDateTime.fromtimestamp(start_epoch)
    title = f"Net Session Hours FROM: {str(from_date)} TO: {str(to_date)}"
    result = {}
    result["The Board Title"] = title

    for each in the_board:
        result[each[0]] = each[1]

    return result


@app.get("/thismonth")
async def this_month(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])

    log_processor.renew_pendings(driver=driver)
    emrooz = JalaliDate.today()
    start_dt = JalaliDateTime(
        year=emrooz.year,
        month=emrooz.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )
    localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())

    localized_end_dt = (localized_start_dt + timedelta(days=33)).replace(day=1)
    end_epoch = int(localized_end_dt.timestamp())

    the_board = report.make_board(
        driver=driver, start_epoch=start_epoch, end_epoch=end_epoch
    )
    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
    title = "Net Session Hours of " + str(title_date)
    result = {}
    result["The Board Title"] = title

    for each in the_board:
        result[each[0]] = each[1]

    return result


@app.get("/lastmaah")
async def last_maah(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])

    log_processor.renew_pendings(driver=driver)
    emrooz = JalaliDate.today()
    end_dt = JalaliDateTime(
        year=emrooz.year,
        month=emrooz.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )
    start_dt = (end_dt - timedelta(days=1)).replace(day=1)
    localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())

    localized_end_dt = pytz.timezone("Asia/Tehran").localize(dt=end_dt)
    end_epoch = int(localized_end_dt.timestamp())

    the_board = report.make_board(
        driver=driver, start_epoch=start_epoch, end_epoch=end_epoch
    )
    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
    title = "Net Session Hours of " + str(title_date)
    result = {}
    result["The Board Title"] = title

    for each in the_board:
        result[each[0]] = each[1]

    return result


@app.get("/events")
async def get_events(request: Request, start: int, end: int, doer: str | None = None):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])

    if doer is None:
        all = report.get_events(driver=driver, start=start, end=end)
    else:
        all = report.get_events_of_doer(driver=driver, start=start, end=end, doer=doer)

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
async def g_oauth(code: str, state: str, request: Request):
    # TO-DO
    # Handle no code response

    discord_id = request.cookies.get("discord_id")
    guild_id = request.cookies.get("guild_id")
    discord_name = request.cookies.get("discord_name")
    GCalSetup.store_user_creds(
        discord_guild=guild_id,
        discord_id=discord_id,
        discord_name=discord_name,
        code=code,
        state=state,
    )
    keyword = "cotopia"
    person = Person()
    cal = GCalSetup.get_processed_events(guild_id, discord_id, keyword)
    person.set_cal(guild_id, discord_id, json.dumps(cal))
    return FileResponse("static/goauthdone.html")


@app.get("/gcal")
async def google_oauth(a: int, b: int):
    discord_id = a
    guild_id = b
    person = Person()
    token = person.get_google_token(discord_guild=guild_id, discord_id=discord_id)
    if token is None:
        return FileResponse("static/gcal.html")
    else:
        return "You already did this before!"


@app.get("/getcal")
async def get_calendar(discord_name: str, request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])

    person = Person()

    cal = None
    cal = person.get_cal_by_name(guild_id, discord_name)
    if cal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar is not available for this user!",
        )
    else:
        return cal


@app.get("/doer_by_name")
async def get_doer_by_name(discord_name: str, request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])

    person = Person()
    info = person.get_person_info(guild_id, discord_name)
    return info


@app.get("/doer_by_id")
async def get_doer_by_id(discord_id: int, request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])

    person = Person()
    info = person.get_person_info_by_id(discord_guild=guild_id, discord_id=discord_id)
    return info


@app.get("/protected")
async def protected(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            return decoded


@app.get("/login")
async def login():
    return FileResponse("static/login.html")


@app.get("/me")
async def me(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])
            discord_id = str(decoded["discord_id"])
    person = Person()
    info = person.get_person_info_by_id(guild_id, discord_id)
    return info


@app.get("/server")
async def server(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])

    server = Server()
    try:
        info = server.getter(guild_id=guild_id)
        return info
    except:  # noqa: E722
        return {"Message": "Not Available. Run /update_info in the server"}


@app.get("/jobs/report")
async def jobs_report(request: Request, start: int, end: int, discord_id: int):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            guild_id = str(decoded["discord_guild"])

    report = gen_user_report(
        guild_id=guild_id, discord_id=discord_id, start_epoch=start, end_epoch=end
    )

    return report


@app.get("/detailed_report")
async def detailed_report(
    request: Request, start_epoch: int, end_epoch: int, in_between: ReportInBetween
):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in!"
        )
    else:
        try:
            decoded = auth.decode_token(token)
        except:  # noqa: E722
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Unable to read token!",
            )

        if decoded is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token! Login Again!",
            )
        else:
            driver = str(decoded["discord_guild"])
            doer = str(decoded["discord_id"])

    result = {}
    total_report = report.make_report_seconds(
        driver=driver, doer=doer, start_epoch=start_epoch, end_epoch=end_epoch
    )
    result["total"] = total_report
    if in_between == ReportInBetween.off:
        return result

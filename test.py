from persiantools.jdatetime import JalaliDate, JalaliDateTime, timedelta

emrooz = JalaliDate.today()
start_dt = JalaliDateTime(
        year=emrooz.year,
        month=emrooz.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )
end_dt = start_dt + timedelta(days=32)
end_dt = JalaliDateTime(
        year=end_dt.year,
        month=end_dt.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )

print(start_dt)
print(end_dt)
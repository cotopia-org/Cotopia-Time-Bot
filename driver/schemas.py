from datetime import date, datetime, time, timezone

from pydantic import BaseModel


class OurBaseModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone.utc).isoformat(),
            time: lambda v: v.astimezone(timezone.utc).isoformat(),
            date: lambda v: v.astimezone(timezone.utc).isoformat(),
        }


class DriverBase(OurBaseModel):
    email: str
    username: str


class DriverCreate(DriverBase):
    password: str


class DriverUpdate(DriverCreate):
    password: str | None = None
    location: str | None = None
    timezone: str | None = None
    locale: str | None = None
    other_settings: str | None = None


class Driver(DriverUpdate):
    id: int
    created_at: datetime
    roles: str

    class Config:
        orm_mode = True


class MinimalDriver(DriverBase):
    class Config:
        orm_mode = True

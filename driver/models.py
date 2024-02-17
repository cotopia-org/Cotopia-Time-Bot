from database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, func


class Driver(Base):
    __tablename__ = "driver"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(40), nullable=False, unique=True, index=False)
    roles = Column(String(127), nullable=False, index=False, default="regular")
    email = Column(String(127), unique=True, index=True)
    hashed_password = Column(String(511))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    timezone = Column(String(40), nullable=False, default="UTC")
    locale = Column(String(40), nullable=False, default="eng_us")
    other_settings = Column(JSON, nullable=True)

    def __repr__(self):
        return f"""
                    db id = {self.id} \n
                    username = {self.username} \n
                    roles = {self.roles} \n
                    email = {self.email} \n
                    hashed_password = {self.hashed_password} \n
                    is_active = {self.is_active} \n
                    created_at = {self.created_at} \n
                    timezone = {self.timezone} \n
                    locale = {self.locale} \n
                    other_settings = {self.other_settings} \n
                """

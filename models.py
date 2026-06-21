from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserSession(Base):

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)

    phone_number = Column(String, unique=True)

    state = Column(String)

    broker = Column(String)

    account_number = Column(String)

    is_verified = Column(Boolean, default=False)

class SupportTicket(Base):

    __tablename__ = "support_tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_phone = Column(String)

    query = Column(String)

    status = Column(String)
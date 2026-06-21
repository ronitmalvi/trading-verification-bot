from database import SessionLocal
from models import UserSession


def get_state(phone):

    db = SessionLocal()

    try:

        session = (
            db.query(UserSession)
            .filter(
                UserSession.phone_number == phone
            )
            .first()
        )

        if not session:
            return "START"

        return session.state

    finally:
        db.close()

def get_verified_state(phone):

    db = SessionLocal()

    try:

        session = (
            db.query(UserSession)
            .filter(
                UserSession.phone_number == phone
            )
            .first()
        )

        if not session:
            return "START"

        return session.is_verified

    finally:
        db.close()


def get_session(phone):

    db = SessionLocal()

    try:

        session = (
            db.query(UserSession)
            .filter(
                UserSession.phone_number == phone
            )
            .first()
        )

        return session

    finally:
        db.close()


def set_state(
    phone,
    state,
    broker=None,
    account_number=None
):

    db = SessionLocal()

    try:

        session = (
            db.query(UserSession)
            .filter(
                UserSession.phone_number == phone
            )
            .first()
        )

        if session:

            session.state = state

            if broker:
                session.broker = broker

            if account_number:
                session.account_number = account_number

        else:

            session = UserSession(
                phone_number=phone,
                state=state,
                broker=broker,
                account_number=account_number
            )

            db.add(session)

        db.commit()

    finally:
        db.close()

def mark_verified(phone,account_number):

    db = SessionLocal()

    try:

        session = (
            db.query(UserSession)
            .filter(
                UserSession.phone_number == phone
            )
            .first()
        )

        if session:

            session.is_verified = True
            session.account_number = account_number
            session.state = "VERIFIED"

            db.commit()

    finally:
        db.close()
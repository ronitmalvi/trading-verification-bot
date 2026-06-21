from database import SessionLocal
from models import SupportTicket


def create_ticket(
    phone,
    query
):

    db = SessionLocal()

    try:

        ticket = SupportTicket(
            user_phone=phone,
            query=query,
            status="OPEN"
        )

        db.add(ticket)

        db.commit()

        db.refresh(ticket)

        return ticket.id

    finally:
        db.close()
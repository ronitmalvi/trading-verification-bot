from database import SessionLocal
from models import SupportTicket

def resolve_ticket(
    ticket_id,
    resolution
):

    db = SessionLocal()

    try:

        ticket = (
            db.query(SupportTicket)
            .filter(
                SupportTicket.id == ticket_id
            )
            .first()
        )

        if not ticket:
            return None

        ticket.resolution = resolution
        ticket.status = "RESOLVED"

        db.commit()

        return {
            "id": ticket.id,
            "user_phone": ticket.user_phone
        }

    finally:
        db.close()


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
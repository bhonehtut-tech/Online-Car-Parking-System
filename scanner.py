import secrets
from database import get_connection

def create_ticket(reservation_id):
    token = secrets.token_urlsafe(12)
    with get_connection() as conn:
        res = conn.execute(
            "SELECT status FROM reservations WHERE id=?",
            (reservation_id,)
        ).fetchone()
        
        if not res or res["status"] != 'RESERVED':
            return "ERROR: Cannot generate ticket for an inactive or invalid reservation."
        
        # Save the securely generated token to the database
        conn.execute(
            "UPDATE reservations SET ticket_token=? WHERE id=?", 
            (token, reservation_id)
        )
        
    return f"PARK-{reservation_id}-{token}"

def scan_ticket(ticket):
    """Scanner: validates the PARK-<reservation_id>-<token> format and checks the database."""
    parts = ticket.strip().split("-")
    
    if len(parts) < 3 or parts[0] != "PARK":
        return None

    try:
        reservation_id = int(parts[1])
        token = parts[2] 
    except ValueError:
        return None

    with get_connection() as conn:
        # Validate that both the reservation ID AND the exact token match
        return conn.execute("""
            SELECT r.*, v.plate_number, p.space_number
            FROM reservations r
            JOIN vehicles v ON v.id=r.vehicle_id
            JOIN parking_spaces p ON p.id=r.space_id
            WHERE r.id=? AND r.status='RESERVED' AND r.ticket_token=?
        """, (reservation_id, token)).fetchone()
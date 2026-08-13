import math
from datetime import datetime
from database import get_connection

RATE_PER_HOUR = 5.00
MINIMUM_FEE = 2.00

def calculate_fee(entry_time, exit_time=None):
    start = datetime.fromisoformat(entry_time)
    end = datetime.fromisoformat(exit_time) if exit_time else datetime.now()
    minutes = max(1, math.ceil((end - start).total_seconds() / 60))
    amount = max(MINIMUM_FEE, math.ceil(minutes / 60) * RATE_PER_HOUR)
    return minutes, round(amount, 2)

def create_bill(session_id):
    with get_connection() as conn:
        session = conn.execute(
            "SELECT * FROM parking_sessions WHERE id=?",
            (session_id,)
        ).fetchone()
        if not session:
            return None

        minutes, amount = calculate_fee(
            session["entry_time"], session["exit_time"]
        )
        cur = conn.execute("""
            INSERT INTO bills(session_id,amount,duration_minutes,created_at,status)
            VALUES(?,?,?,?,?)
        """, (session_id, amount, minutes,
              datetime.now().isoformat(timespec="seconds"), "UNPAID"))
        return {
            "bill_id": cur.lastrowid,
            "session_id": session_id,
            "duration_minutes": minutes,
            "amount": amount,
            "status": "UNPAID"
        }

def pay_bill(bill_id):
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE bills SET status='PAID' WHERE id=? AND status='UNPAID'",
            (bill_id,)
        )
        return cur.rowcount > 0

def list_bills(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT b.*, ps.user_id, v.plate_number
            FROM bills b
            JOIN parking_sessions ps ON ps.id=b.session_id
            JOIN vehicles v ON v.id=ps.vehicle_id
            WHERE ps.user_id=?
            ORDER BY b.id DESC
        """, (user_id,)).fetchall()

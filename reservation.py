from datetime import datetime
from database import get_connection

def create_reservation(user_id, vehicle_id, space_number, start_time, end_time):
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except ValueError:
        return False, "Use date/time format YYYY-MM-DD HH:MM."

    if end <= start:
        return False, "End time must be after start time."

    with get_connection() as conn:
        space = conn.execute(
            "SELECT * FROM parking_spaces WHERE space_number=?",
            (space_number.strip().upper(),)
        ).fetchone()
        if not space:
            return False, "Parking space does not exist."

        conflict = conn.execute("""
            SELECT id FROM reservations
            WHERE space_id=? AND status='RESERVED'
              AND NOT (end_time <= ? OR start_time >= ?)
        """, (space["id"], start.isoformat(timespec="minutes"),
              end.isoformat(timespec="minutes"))).fetchone()

        if conflict:
            return False, "That parking space is already reserved for this period."

        cur = conn.execute("""
            INSERT INTO reservations
            (user_id,vehicle_id,space_id,start_time,end_time,status,created_at)
            VALUES(?,?,?,?,?,?,?)
        """, (user_id, vehicle_id, space["id"],
              start.isoformat(timespec="minutes"),
              end.isoformat(timespec="minutes"),
              "RESERVED", datetime.now().isoformat(timespec="seconds")))
        return True, f"Reservation created. Booking ID: {cur.lastrowid}"

def list_reservations(user_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.*, v.plate_number, p.space_number
            FROM reservations r
            JOIN vehicles v ON v.id=r.vehicle_id
            JOIN parking_spaces p ON p.id=r.space_id
            WHERE r.user_id=?
            ORDER BY r.start_time DESC
        """, (user_id,)).fetchall()

def cancel_reservation(user_id, reservation_id):
    with get_connection() as conn:
        cur = conn.execute("""
            UPDATE reservations SET status='CANCELLED'
            WHERE id=? AND user_id=? AND status='RESERVED'
        """, (reservation_id, user_id))
        return cur.rowcount > 0

def upcoming_reminders(user_id):
    now = datetime.now().isoformat(timespec="minutes")
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.*, v.plate_number, p.space_number
            FROM reservations r
            JOIN vehicles v ON v.id=r.vehicle_id
            JOIN parking_spaces p ON p.id=r.space_id
            WHERE r.user_id=? AND r.status='RESERVED' AND r.end_time >= ?
            ORDER BY r.start_time
        """, (user_id, now)).fetchall()

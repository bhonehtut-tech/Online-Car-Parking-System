from datetime import datetime
from database import get_connection

def list_spaces():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM parking_spaces ORDER BY space_number"
        ).fetchall()

def available_spaces():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM parking_spaces WHERE status='AVAILABLE' ORDER BY space_number"
        ).fetchall()

def get_space(space_number):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM parking_spaces WHERE space_number=?",
            (space_number.strip().upper(),)
        ).fetchone()

def check_in(user_id, vehicle_id, space_number):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        space = conn.execute(
            "SELECT * FROM parking_spaces WHERE space_number=?",
            (space_number.strip().upper(),)
        ).fetchone()
        
        if not space or space["status"] != "AVAILABLE":
            return False, "Parking space is not available.", None

        # --- NEW FIX: Prevent hijacking someone else's reservation ---
        conflict = conn.execute("""
            SELECT id FROM reservations
            WHERE space_id=? AND status='RESERVED'
              AND start_time <= ? AND end_time >= ?
              AND user_id != ?
        """, (space["id"], now, now, user_id)).fetchone()

        if conflict:
            return False, "This space is currently reserved by another user.", None
        # -------------------------------------------------------------

        active = conn.execute(
            "SELECT id FROM parking_sessions WHERE vehicle_id=? AND status='IN'",
            (vehicle_id,)
        ).fetchone()
        
        if active:
            return False, "This vehicle is already parked.", None

        cur = conn.execute(
            """INSERT INTO parking_sessions
               (user_id,vehicle_id,space_id,entry_time,status)
               VALUES(?,?,?,?,?)""",
            (user_id, vehicle_id, space["id"], now, "IN")
        )
        
        conn.execute(
            "UPDATE parking_spaces SET status='OCCUPIED' WHERE id=?",
            (space["id"],)
        )
        return True, "Vehicle checked in successfully.", cur.lastrowid

def check_out(user_id, vehicle_id):
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        session = conn.execute(
            """SELECT * FROM parking_sessions
               WHERE user_id=? AND vehicle_id=? AND status='IN'
               ORDER BY id DESC LIMIT 1""",
            (user_id, vehicle_id)
        ).fetchone()
        
        if not session:
            return False, "No active parking session found.", None

        conn.execute(
            """UPDATE parking_sessions
               SET exit_time=?, status='OUT' WHERE id=?""",
            (now, session["id"])
        )
        
        conn.execute(
            "UPDATE parking_spaces SET status='AVAILABLE' WHERE id=?",
            (session["space_id"],)
        )
        return True, "Vehicle checked out successfully.", session["id"]

def active_sessions():
    with get_connection() as conn:
        return conn.execute("""
            SELECT ps.*, v.plate_number, v.model, p.space_number
            FROM parking_sessions ps
            JOIN vehicles v ON v.id=ps.vehicle_id
            JOIN parking_spaces p ON p.id=ps.space_id
            WHERE ps.status='IN'
            ORDER BY ps.entry_time
        """).fetchall()
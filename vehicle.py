from datetime import datetime
from database import get_connection

def add_vehicle(user_id, plate_number, model, color=""):
    plate_number = plate_number.strip().upper()
    model = model.strip()
    if not plate_number or not model:
        return False, "Plate number and model are required."

    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO vehicles(user_id,plate_number,model,color,created_at)
                   VALUES(?,?,?,?,?)""",
                (user_id, plate_number, model, color.strip(),
                 datetime.now().isoformat(timespec="seconds"))
            )
        return True, "Vehicle registered."
    except Exception:
        return False, "This plate number is already registered."

def list_vehicles(user_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM vehicles WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()

def get_vehicle(user_id, plate_number):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM vehicles WHERE user_id=? AND plate_number=?",
            (user_id, plate_number.strip().upper())
        ).fetchone()

def recognize_vehicle(plate_number):
    """Simple vehicle-recognition layer: matches a scanned/entered plate.
    A camera/OCR implementation can replace this function later."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM vehicles WHERE plate_number=?",
            (plate_number.strip().upper(),)
        ).fetchone()

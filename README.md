# Online Car Parking Management System

A Python + SQLite Software Engineering project.

## Features
- User registration and secure password hashing
- Customer/admin roles
- Vehicle registration
- Parking-space availability
- Reservations
- Parking check-in/check-out
- Parking reminders
- Demo parking ticket scanner
- Vehicle recognition by registered license plate
- Parking fee calculation
- Bills and payment status
- Basic automated tests

## Requirements
- Python 3.9 or newer
- No third-party packages are required

## Run
Open a terminal in this folder and run:

```bash
python main.py
```

The SQLite database `parking.db` is created automatically.

## Default administrator
- Username: `admin`
- Password: `admin123`

Change this password before using the project beyond a classroom/demo environment.

## Test
Run:

```bash
python -m unittest discover -s tests -v
```

## Notes
The scanner and car-recognition modules are intentionally implemented as demo/software interfaces:
- Scanner validates a generated parking-ticket format.
- Vehicle recognition matches a plate number against registered vehicles.

A real QR camera scanner or license-plate camera/OCR can be integrated later without changing the overall module structure.

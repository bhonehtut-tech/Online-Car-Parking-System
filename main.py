from database import initialize_database, get_connection
from authentication import register_user, login
from vehicle import add_vehicle, list_vehicles, get_vehicle
from parking import list_spaces, available_spaces, check_in, check_out, active_sessions
from reservation import create_reservation, list_reservations, cancel_reservation, upcoming_reminders
from scanner import create_ticket, scan_ticket
from billing import create_bill, pay_bill, list_bills
from security import require_role

def pause():
    input("\nPress Enter to continue...")

def show_spaces():
    print("\n--- Parking Spaces ---")
    for s in list_spaces():
        print(f"{s['space_number']}: {s['status']}")

def choose_vehicle(user_id):
    vehicles = list_vehicles(user_id)
    if not vehicles:
        print("No vehicles registered.")
        return None
        
    for v in vehicles:
        print(f"{v['id']}. {v['plate_number']} - {v['model']} ({v['color'] or 'N/A'})")
        
    # --- The Fixed Loop ---
    while True:
        user_input = input("Vehicle ID (or 'c' to cancel): ").strip()
        
        if user_input.lower() == 'c':
            return None
            
        try:
            vid = int(user_input)
            vehicle = next((v for v in vehicles if v["id"] == vid), None)
            
            if vehicle:
                return vehicle
            else:
                print("Error: Vehicle ID not found. Please pick a number from the list above.")
                
        except ValueError:
            print("Error: Invalid input. You must type the numeric ID, not the plate number.")

def customer_menu(user):
    while True:
        print("""
=== CUSTOMER MENU ===
1. Register vehicle
2. View vehicles
3. View parking spaces
4. Reserve parking
5. View reservations
6. Cancel reservation
7. Create parking ticket
8. Check in
9. Check out
10. Scan ticket
11. View reminders
12. View bills
13. Pay bill
0. Logout
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            ok, msg = add_vehicle(
                user["id"],
                input("Plate number: "),
                input("Model: "),
                input("Color: ")
            )
            print(msg); pause()

        elif choice == "2":
            for v in list_vehicles(user["id"]):
                print(f"{v['id']}: {v['plate_number']} - {v['model']} - {v['color']}")
            pause()

        elif choice == "3":
            show_spaces(); pause()

        elif choice == "4":
            vehicle = choose_vehicle(user["id"])
            if not vehicle: continue
            show_spaces()
            ok, msg = create_reservation(
                user["id"], vehicle["id"], input("Space number: "),
                input("Start (YYYY-MM-DD HH:MM): "),
                input("End (YYYY-MM-DD HH:MM): ")
            )
            print(msg); pause()

        elif choice == "5":
            for r in list_reservations(user["id"]):
                print(f"#{r['id']} | {r['plate_number']} | {r['space_number']} | "
                      f"{r['start_time']} -> {r['end_time']} | {r['status']}")
            pause()

        elif choice == "6":
            try: rid = int(input("Reservation ID: "))
            except ValueError: print("Invalid ID."); continue
            print("Cancelled." if cancel_reservation(user["id"], rid) else "Could not cancel.")
            pause()

        elif choice == "7":
            try: rid = int(input("Reservation ID: "))
            except ValueError: print("Invalid ID."); continue
            ticket = create_ticket(rid)
            print("Parking ticket:", ticket); pause()

        elif choice == "8":
            vehicle = choose_vehicle(user["id"])
            if not vehicle: continue
            show_spaces()
            ok, msg, _ = check_in(user["id"], vehicle["id"], input("Space number: "))
            print(msg); pause()

        elif choice == "9":
            vehicle = choose_vehicle(user["id"])
            if not vehicle: continue
            ok, msg, session_id = check_out(user["id"], vehicle["id"])
            print(msg)
            if ok:
                bill = create_bill(session_id)
                print(f"Bill #{bill['bill_id']}: ${bill['amount']:.2f} "
                      f"for {bill['duration_minutes']} minutes.")
            pause()

        elif choice == "10":
            result = scan_ticket(input("Enter ticket: "))
            print(dict(result) if result else "Invalid ticket.")
            pause()

        elif choice == "11":
            reminders = upcoming_reminders(user["id"])
            if not reminders: print("No active reminders.")
            for r in reminders:
                print(f"Reservation #{r['id']} | {r['plate_number']} | "
                      f"{r['start_time']} -> {r['end_time']} | Space {r['space_number']}")
            pause()

        elif choice == "12":
            for b in list_bills(user["id"]):
                print(f"Bill #{b['id']} | {b['plate_number']} | "
                      f"{b['duration_minutes']} min | ${b['amount']:.2f} | {b['status']}")
            pause()

        elif choice == "13":
            try: bid = int(input("Bill ID: "))
            except ValueError: print("Invalid ID."); continue
            print("Payment successful." if pay_bill(bid) else "Payment failed or already paid.")
            pause()

        elif choice == "0":
            break
        else:
            print("Invalid choice.")

def admin_menu(user):
    require_role(user, "admin")
    while True:
        print("""
=== ADMIN MENU ===
1. View parking spaces
2. View active parking
3. View all reservations
4. View all users
5. View all bills
0. Logout
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            show_spaces(); pause()
        elif choice == "2":
            for s in active_sessions():
                print(f"Session #{s['id']} | {s['plate_number']} | "
                      f"{s['space_number']} | IN {s['entry_time']}")
            pause()
        elif choice == "3":
            with get_connection() as conn:
                rows = conn.execute("""
                    SELECT r.id,u.username,v.plate_number,p.space_number,
                           r.start_time,r.end_time,r.status
                    FROM reservations r
                    JOIN users u ON u.id=r.user_id
                    JOIN vehicles v ON v.id=r.vehicle_id
                    JOIN parking_spaces p ON p.id=r.space_id
                    ORDER BY r.start_time DESC
                """).fetchall()
            for r in rows:
                print(f"#{r['id']} | {r['username']} | {r['plate_number']} | "
                      f"{r['space_number']} | {r['status']}")
            pause()
        elif choice == "4":
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT id,username,role,created_at FROM users ORDER BY id"
                ).fetchall()
            for r in rows:
                print(dict(r))
            pause()
        elif choice == "5":
            with get_connection() as conn:
                rows = conn.execute("""
                    SELECT b.id,v.plate_number,b.amount,b.duration_minutes,b.status
                    FROM bills b
                    JOIN parking_sessions ps ON ps.id=b.session_id
                    JOIN vehicles v ON v.id=ps.vehicle_id
                    ORDER BY b.id DESC
                """).fetchall()
            for r in rows:
                print(f"Bill #{r['id']} | {r['plate_number']} | "
                      f"${r['amount']:.2f} | {r['duration_minutes']} min | {r['status']}")
            pause()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

def main():
    initialize_database()
    print("====================================")
    print(" ONLINE CAR PARKING MANAGEMENT SYSTEM")
    print("====================================")

    while True:
        print("\n1. Register\n2. Login\n0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            ok, msg = register_user(input("Username: "), input("Password: "))
            print(msg)
        elif choice == "2":
            user = login(input("Username: "), input("Password: "))
            if not user:
                print("Invalid username or password.")
                continue
            print(f"Welcome, {user['username']}!")
            if user["role"] == "admin":
                admin_menu(user)
            else:
                customer_menu(user)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
    
import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Path to the database directory
thisdir = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(thisdir, "firewallDB")
DB_FILE = os.path.join(DB_DIR, "firewall.db")

# ✅ Create the directory if it doesn't exist
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# ✅ Create database connection
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
ClientIPBase = declarative_base()

class ClientIP(ClientIPBase):
    __tablename__ = "client_ips"
    ip = Column(String, primary_key=True)

# ✅ Create tables once
ClientIPBase.metadata.create_all(engine)

# ✅ Create session factory (No session created yet)
Session = sessionmaker(bind=engine)

def get_session():
    """Creates and returns a new session (closes automatically when done)."""
    return Session()

# ✅ Function to add an IP to the list
def add_ip(ip_address):
    session = get_session()
    try:
        if session.query(ClientIP).filter_by(ip=ip_address).first():
            print(f"⚠️ The IP {ip_address} already exists in the list!")
        else:
            session.add(ClientIP(ip=ip_address))
            session.commit()
            print(f"✅ The IP {ip_address} has been added successfully!")
    except Exception as e:
        print(f"❌ Error adding IP: {e}")
        session.rollback()
    finally:
        session.close()

# ✅ Function to remove an IP from the list
def remove_ip(ip_address):
    session = get_session()
    try:
        ip_entry = session.query(ClientIP).filter_by(ip=ip_address).first()
        if ip_entry:
            session.delete(ip_entry)
            session.commit()
            print(f"❌ The IP {ip_address} has been removed!")
        else:
            print(f"⚠️ The IP {ip_address} is not in the list!")
    except Exception as e:
        print(f"❌ Error removing IP: {e}")
        session.rollback()
    finally:
        session.close()

# ✅ Function to display all IPs in the table
def list_ips():
    session = get_session()
    try:
        ips = session.query(ClientIP).all()
        if not ips:
            print("📌 No IP addresses in the database.")
        else:
            print("📌 List of IP addresses in the database:")
            for ip in ips:
                print(f"🔹 {ip.ip}")
    except Exception as e:
        print(f"❌ Error listing IPs: {e}")
    finally:
        session.close()

# ✅ CLI menu for managing the firewall IP list
def main():
    while True:
        print("\n🔹 Firewall IP Management 🔹")
        print("1️⃣ Add IP")
        print("2️⃣ Remove IP")
        print("3️⃣ Show all IPs")
        print("4️⃣ Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            ip = input("📥 Enter IP address to add: ").strip()
            add_ip(ip)
        elif choice == "2":
            ip = input("📥 Enter IP address to remove: ").strip()
            remove_ip(ip)
        elif choice == "3":
            list_ips()
        elif choice == "4":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid choice! Please try again.")

if __name__ == "__main__":
    main()

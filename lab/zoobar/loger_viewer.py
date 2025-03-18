import os
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Define the database path
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
DB_FILE = os.path.join(DB_DIR, "log.db")

# Initialize the database connection
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Define the base model
LogBase = declarative_base()

# Define the Log model
class Log(LogBase):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100))
    action = Column(String(50))
    username = Column(String(50))
    log_level = Column(String(10))
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

# Function to retrieve logs with filters
def get_logs(service_name=None, action=None, username=None, log_level=None, date_from=None, date_to=None):
    query = session.query(Log)

    # Apply filters
    if service_name:
        query = query.filter(Log.service_name == service_name)
    if action:
        query = query.filter(Log.action == action)
    if username:
        query = query.filter(Log.username == username)
    if log_level:
        query = query.filter(Log.log_level == log_level)
    if date_from:
        query = query.filter(Log.timestamp >= date_from)
    if date_to:
        query = query.filter(Log.timestamp <= date_to)

    logs = query.order_by(Log.timestamp.desc()).all()
    return logs

# Function to display logs
def display_logs(logs):
    if not logs:
        print("\n❌ No logs found with the selected filters.")
        return

    print("\n📋 Logs Found:")
    print("=" * 80)
    for log in logs:
        print(f"📌 [{log.timestamp}] [{log.log_level}] {log.service_name} - {log.action}")
        print(f"   👤 User: {log.username} | 🆔 Log ID: {log.id}")
        print(f"   📝 Message: {log.message}")
        print("=" * 80)

# Function to get user input for filtering logs
def user_interface():
    while True:
        print("\n🔍 Log Viewer - Main Menu")
        print("1️⃣ View logs with filters")
        print("2️⃣ Show all logs")
        print("3️⃣ Exit")

        choice = input("👉 Select an option: ").strip()

        if choice == "1":
            service_name = input("🔹 Filter by Service Name (leave blank to skip): ").strip() or None
            action = input("🔹 Filter by Action (leave blank to skip): ").strip() or None
            username = input("🔹 Filter by Username (leave blank to skip): ").strip() or None
            log_level = input("🔹 Filter by Log Level (INFO/WARNING/ERROR/DEBUG, leave blank to skip): ").strip() or None

            # Get date filters
            date_from = input("🔹 Filter by Start Date (YYYY-MM-DD, leave blank to skip): ").strip() or None
            date_to = input("🔹 Filter by End Date (YYYY-MM-DD, leave blank to skip): ").strip() or None

            # Convert dates to proper format if provided
            if date_from:
                date_from = datetime.strptime(date_from, "%Y-%m-%d")
            if date_to:
                date_to = datetime.strptime(date_to, "%Y-%m-%d")

            logs = get_logs(service_name, action, username, log_level, date_from, date_to)
            display_logs(logs)

        elif choice == "2":
            logs = get_logs()  # Retrieve all logs
            display_logs(logs)

        elif choice == "3":
            print("👋 Exiting Log Viewer. Goodbye!")
            break

        else:
            print("❌ Invalid choice! Please enter a valid option.")

# Run the user interface
if __name__ == "__main__":
    user_interface()

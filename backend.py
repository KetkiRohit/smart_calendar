import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from tkinter import messagebox

# Database setup and helper functions
class EventDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('events.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create table for events
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            priority INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            reminder_sent INTEGER DEFAULT 0
        )''')

        # Create table for history logs
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS event_history (
            id INTEGER PRIMARY KEY,
            action TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )''')

        self.conn.commit()

    def add_event(self, name, priority, date, time):
        self.cursor.execute("INSERT INTO events (name, priority, date, time) VALUES (?, ?, ?, ?)", 
                            (name, priority, date, time))
        self.conn.commit()

    def get_events(self):
        self.cursor.execute("SELECT * FROM events ORDER BY priority")
        return self.cursor.fetchall()

    def get_event_by_id(self, event_id):
        self.cursor.execute("SELECT * FROM events WHERE id=?", (event_id,))
        return self.cursor.fetchone()

    def update_event_reminder_status(self, event_id):
        self.cursor.execute("UPDATE events SET reminder_sent = 1 WHERE id=?", (event_id,))
        self.conn.commit()

    def log_event_history(self, action, event_id):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO event_history (action, event_id, timestamp) VALUES (?, ?, ?)",
                            (action, event_id, timestamp))
        self.conn.commit()

    def get_event_history(self):
        self.cursor.execute("""
            SELECT events.name, event_history.action, event_history.event_id, event_history.timestamp 
            FROM event_history
            JOIN events ON event_history.event_id = events.id 
            ORDER BY event_history.timestamp DESC
        """)
        return self.cursor.fetchall()

    def delete_event(self, event_id):
        # Delete event history first to maintain referential integrity
        self.cursor.execute("DELETE FROM event_history WHERE event_id=?", (event_id,))
        # Delete the event from the events table
        self.cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

# Reminder handling using schedule library
class EventReminder:
    def __init__(self, db):
        self.db = db

    def schedule_reminders(self):
        events = self.db.get_events()
        for event in events:
            event_time = f"{event[3]} {event[4]}"
            event_datetime = datetime.strptime(event_time, '%Y-%m-%d %H:%M')
            current_time = datetime.now()

            # Check if the event time is in the future
            if event_datetime > current_time and not event[5]:
                reminder_time = event_datetime - timedelta(minutes=10)  # Reminder 10 minutes before the event
                if reminder_time > current_time:
                    reminder_time_str = reminder_time.strftime('%H:%M')
                    # Schedule the reminder at the exact time
                    schedule.every().day.at(reminder_time_str).do(self.send_reminder, event[0], event[1])

    def send_reminder(self, event_id, event_name):
        print(f"Reminder: Event '{event_name}' is coming up in 10 minutes!")
        # Log the reminder action in the history table
        self.db.log_event_history("Reminder Sent", event_id)
        # Update reminder status in DB
        self.db.update_event_reminder_status(event_id)

# Main Application Logic
class SmartCalendarBackend:
    def __init__(self):
        self.db = EventDatabase()
        self.reminder = EventReminder(self.db)

    def add_event_to_db(self, name, priority, date, time):
        self.db.add_event(name, priority, date, time)
        event_id = self.db.cursor.lastrowid  # Get the ID of the last inserted event
        # Log the event addition in the history
        self.db.log_event_history("Event Added", event_id)
        self.reminder.schedule_reminders()

    def get_events_from_db(self):
        return self.db.get_events()

    def get_event_history(self):
        return self.db.get_event_history()

    def delete_event(self, event_id):
        self.db.delete_event(event_id)
        self.reminder.schedule_reminders()  # Reschedule reminders after deleting events

    def close_db(self):
        self.db.close()

# Example usage of the backend
if __name__ == "__main__":
    backend = SmartCalendarBackend()

    # Add a sample event to the database and log it
    backend.add_event_to_db("Meeting with Bob", 1, "2025-01-10", "15:00")

    # Start scheduling reminders
    backend.reminder.schedule_reminders()

    # Print event history whenever the project is opened
    print("Event History:")
    event_history = backend.get_event_history()
    for history in event_history:
        print(f"Event Name: {history[0]}, Action: {history[1]}, Event ID: {history[2]}, Timestamp: {history[3]}")

    # Keep checking the schedule
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second

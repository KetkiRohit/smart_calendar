import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from backend import SmartCalendarBackend  # Ensure backend.py is in the same directory

class SmartCalendarApp:
    def __init__(self, root):
        self.backend = SmartCalendarBackend()

        # Window setup
        root.title("Smart Calendar")
        root.state('zoomed')  # Make the window fullscreen
        root.config(bg="#f0f8ff")

        # Frame for UI elements
        self.main_frame = tk.Frame(root, bg="#f0f8ff")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        self.title_label = tk.Label(self.main_frame, text="Smart Calendar", font=("Arial", 24, "bold"), bg="#f0f8ff", fg="#ff6347")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Event Name
        self.name_label = tk.Label(self.main_frame, text="Event Name:", font=("Arial", 12), bg="#f0f8ff")
        self.name_label.grid(row=1, column=0, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
        self.name_entry.grid(row=1, column=1, pady=5)

        # Priority
        self.priority_label = tk.Label(self.main_frame, text="Priority (1-5):", font=("Arial", 12), bg="#f0f8ff")
        self.priority_label.grid(row=2, column=0, pady=5, sticky="w")
        self.priority_spin = tk.Spinbox(self.main_frame, from_=1, to=5, font=("Arial", 12), width=5)
        self.priority_spin.grid(row=2, column=1, pady=5)
        self.priority_spin.delete(0, tk.END)
        self.priority_spin.insert(0, "1")

        # Date
        self.date_label = tk.Label(self.main_frame, text="Event Date (YYYY-MM-DD):", font=("Arial", 12), bg="#f0f8ff")
        self.date_label.grid(row=3, column=0, pady=5, sticky="w")
        self.date_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
        self.date_entry.grid(row=3, column=1, pady=5)

        # Time
        self.time_label = tk.Label(self.main_frame, text="Event Time (HH:MM):", font=("Arial", 12), bg="#f0f8ff")
        self.time_label.grid(row=4, column=0, pady=5, sticky="w")
        self.time_entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
        self.time_entry.grid(row=4, column=1, pady=5)

        # Add Event Button
        self.add_event_button = tk.Button(self.main_frame, text="Add Event", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.add_event)
        self.add_event_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Event History Label
        self.history_label = tk.Label(self.main_frame, text="Event History", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#ff6347")
        self.history_label.grid(row=6, column=0, columnspan=2, pady=20)

        # Event History Treeview
        self.history_tree = ttk.Treeview(self.main_frame, columns=("Action", "Event ID", "Event Name", "Timestamp"), show="headings", height=15)
        self.history_tree.heading("Action", text="Action")
        self.history_tree.heading("Event ID", text="Event ID")
        self.history_tree.heading("Event Name", text="Event Name")
        self.history_tree.heading("Timestamp", text="Timestamp")
        self.history_tree.column("Action", width=150)
        self.history_tree.column("Event ID", width=150)
        self.history_tree.column("Event Name", width=300)
        self.history_tree.column("Timestamp", width=300)
        self.history_tree.grid(row=7, column=0, columnspan=2)

        # Load event history
        self.load_event_history()

        # Delete Event Button
        self.delete_event_button = tk.Button(self.main_frame, text="Delete Event", font=("Arial", 12), bg="#FF6347", fg="white", command=self.delete_event)
        self.delete_event_button.grid(row=8, column=0, columnspan=2, pady=10)

    def add_event(self):
        # Get the input data from the user
        name = self.name_entry.get()
        priority = self.priority_spin.get()
        date = self.date_entry.get()
        time = self.time_entry.get()

        # Validate inputs
        try:
            # Check if date and time are valid
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid date or time format.")
            return

        if not name.strip():
            messagebox.showerror("Invalid Input", "Event Name cannot be empty.")
            return

        # Add event to the database
        self.backend.add_event_to_db(name, int(priority), date, time)

        # Clear input fields
        self.name_entry.delete(0, tk.END)
        self.priority_spin.delete(0, tk.END)
        self.priority_spin.insert(0, "1")
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

        # Reload event history
        self.load_event_history()

    def load_event_history(self):
        # Clear existing history in the treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Get event history from the backend
        event_history = self.backend.get_event_history()
        for record in event_history:
            self.history_tree.insert("", "end", values=(record[1], record[2], record[0], record[3]))

    def delete_event(self):
        # Ask for the event ID to delete
        event_id = simpledialog.askinteger("Delete Event", "Enter the Event ID to delete:")

        if event_id:
            try:
                self.backend.delete_event(event_id)
                messagebox.showinfo("Success", "Event deleted successfully.")
                self.load_event_history()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete event: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCalendarApp(root)
    root.mainloop()

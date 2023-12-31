import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from tkcalendar import Calendar
import random 

# Create SQLite database and tables
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT,
        password TEXT,
        card_number TEXT,
        plate_number TEXT,
        employee_code TEXT,
        user_type TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        driver_id INTEGER,
        start_address TEXT,
        destination_address TEXT,
        postcode TEXT,
        date TEXT,
        time TEXT,
        paid TEXT,
        status TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (driver_id) REFERENCES drivers (id)
    )
''')




conn.commit()

def display_receipt(start_address, destination_address, duration, cost):
    receipt_window = tk.Toplevel(dashboard_window)
    receipt_window.title("Ride Receipt")
    receipt_window.geometry("300x300")

    # Display receipt information
    receipt_label = tk.Label(receipt_window, text="Ride Receipt", font=("Helvetica", 16, "bold"))
    receipt_label.pack(pady=10)

    start_label = tk.Label(receipt_window, text=f"Start Address: {start_address}")
    start_label.pack()

    destination_label = tk.Label(receipt_window, text=f"Destination Address: {destination_address}")
    destination_label.pack()

    duration_label = tk.Label(receipt_window, text=f"Duration: {duration} minutes")
    duration_label.pack()

    cost_label = tk.Label(receipt_window, text=f"Cost: £{cost}")
    cost_label.pack()
    
    
def destroy_dashboard():
    dashboard_window.destroy()
    root.deiconify()  # Unhide the main window when the dashboard is closed

def open_request_ride_window():
    request_ride_window = tk.Toplevel(dashboard_window)
    request_ride_window.title("Request Ride")

    # Labels and entry widgets for ride request details
    labels = ["Start Address:", "Destination Address:", "Postcode:", "Date (MM/DD/YY):", "Time:"]
    entries = []

    for i, label_text in enumerate(labels):
        label = tk.Label(request_ride_window, text=label_text)
        label.grid(row=i, column=0, padx=5, pady=5)

        entry = tk.Entry(request_ride_window)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    # Button to submit ride request
    btn_request_ride = tk.Button(request_ride_window, text="Request", command=lambda: submit_ride_request(entries))
    btn_request_ride.grid(row=len(labels), column=0, columnspan=2, pady=10)

def submit_ride_request(entries):
    # Get ride request details from entry widgets
    start_address = entries[0].get()
    destination_address = entries[1].get()
    postcode = entries[2].get()
    date = entries[3].get()
    time = entries[4].get()

    # Validate that all fields are filled
    if not all([start_address, destination_address, postcode, date, time]):
        messagebox.showerror("Request Failed", "Please fill in all fields")
        return

    # Insert the ride request into the bookings table with the current user's ID
    user_id = get_current_user_id()
    cursor.execute('''
        INSERT INTO bookings (user_id, start_address, destination_address, postcode, date, time, paid, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending', 'Not assigned')
    ''', (user_id, start_address, destination_address, postcode, date, time))
    conn.commit()

    # Display a success message
    messagebox.showinfo("Request Successful", "Ride request submitted successfully!")

    # Update the table in the dashboard with the latest ride requests
    update_ride_requests_table()

def check_user_is_driver(user_id):
    # You need to implement the logic to determine if the user with the given ID is a driver
    # For example, you might have a 'user_type' column in the database
    cursor.execute('SELECT user_type FROM users WHERE id=?', (user_id,))
    user_type = cursor.fetchone()[0] if cursor.rowcount > 0 else None

    return user_type == "Driver" if user_type else False

def update_ride_requests_table():
    # Clear existing items in the treeview
    for item in tree.get_children():
        tree.delete(item)

    # Retrieve and display bookings based on user type and user ID
    user_id = get_current_user_id()
    is_driver = check_user_is_driver(user_id)

    if is_driver:
        cursor.execute('SELECT id, start_address, destination_address, postcode, date, time, paid, status FROM bookings')
    else:
        cursor.execute('SELECT id, start_address, destination_address, postcode, date, time, paid, status FROM bookings WHERE user_id=?', (user_id,))

    bookings = cursor.fetchall()

    for booking in bookings:
        tree.insert("", "end", values=(booking[0], booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7]))


def assign_driver_to_booking(booking_id, driver_id):
    cursor.execute('UPDATE bookings SET driver_id=? WHERE id=?', (driver_id, booking_id))
    conn.commit()

def update_drivers_table():
    # Clear existing items in the treeview
    for item in driver_tree.get_children():
        driver_tree.delete(item)

    # Retrieve and display all available drivers
    cursor.execute('SELECT id, first_name, last_name, employee_code FROM users WHERE user_type="Driver"')
    drivers = cursor.fetchall()

    for driver in drivers:
        driver_tree.insert("", "end", values=(driver[0], driver[1], driver[2], driver[3]))

def update_dashboard(user_id, is_driver=False):
    # Clear existing items in the treeview
    for item in tree.get_children():
        tree.delete(item)

    # Retrieve and display ride requests from the database based on user type
    if is_driver:
        cursor.execute('SELECT id, start_address, destination_address, postcode, date, time, paid, status FROM bookings')
    else:
        cursor.execute('SELECT id, start_address, destination_address, postcode, date, time, paid, status FROM bookings WHERE user_id=?', (user_id,))

    bookings = cursor.fetchall()

    for booking in bookings:
        tree.insert("", "end", values=(booking[0], booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7]))


def get_current_user_id():
    # Assuming the user is logged in, get the ID of the currently logged-in user
    # This function should be extended based on your authentication mechanism
    email = entry_email_login.get()
    password = entry_password_login.get()
    user_type = var_user_type_login.get()

    cursor.execute('SELECT id FROM users WHERE email=? AND password=? AND user_type=?', (email, password, user_type))
    user = cursor.fetchone()

    return user[0] if user else None



def login():
    global btn_cancel_booking, btn_change_booking, btn_request_ride  # Declare as global variables
    email = entry_email_login.get()
    password = entry_password_login.get()
    user_type = var_user_type_login.get()

    cursor.execute('SELECT * FROM users WHERE email=? AND password=? AND user_type=?', (email, password, user_type))
    user = cursor.fetchone()

    if user:
        if user_type == "Customer":
            # Create a new window for the dashboard
            global dashboard_window
            dashboard_window = tk.Toplevel(root)
            dashboard_window.title("Customer Dashboard")
            dashboard_window.geometry("1700x500")  # Larger size

            # Display a welcome message with the user's first name
            welcome_label_text = f"Welcome, {user[2]}!"  # Assuming user's first name is at index 2
            welcome_label = tk.Label(dashboard_window, text=welcome_label_text)
            welcome_label.pack(pady=20)

            # Button to open the request ride window
            btn_request_ride = tk.Button(dashboard_window, text="Request Ride", command=open_request_ride_window)
            btn_request_ride.pack(side=tk.TOP, pady=10)

            # Cancel Booking button
            btn_cancel_booking = tk.Button(dashboard_window, text="Cancel Booking", command=cancel_booking, state=tk.DISABLED)
            btn_cancel_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Change Booking button
            btn_change_booking = tk.Button(dashboard_window, text="Change Booking", command=change_booking, state=tk.DISABLED)
            btn_change_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Treeview for displaying ride requests (right side)
            global tree
            tree = ttk.Treeview(dashboard_window, columns=("ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"), show="headings")

            # Center all values
            headings = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for heading in headings:
                tree.heading(heading, text=heading, anchor=tk.CENTER)
            
            columns = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for column in columns:
                tree.column(column, anchor=tk.CENTER)

            tree.heading("ID", text="ID", anchor=tk.CENTER)
            tree.heading("Start Address", text="Start Address", anchor=tk.CENTER)
            tree.heading("Destination Address", text="Destination Address", anchor=tk.CENTER)
            tree.heading("Postcode", text="Postcode", anchor=tk.CENTER)
            tree.heading("Date", text="Date", anchor=tk.CENTER)
            tree.heading("Time", text="Time", anchor=tk.CENTER)
            tree.heading("Paid", text="Paid", anchor=tk.CENTER)
            tree.heading("Status", text="Status", anchor=tk.CENTER)
            tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Set up an event handler for selecting a booking in the treeview
            tree.bind("<ButtonRelease-1>", on_tree_select)

            # Set up an event handler for closing the dashboard
            dashboard_window.protocol("WM_DELETE_WINDOW", destroy_dashboard)

            # Hide the main login window
            root.withdraw()

            # Update the table in the dashboard with the latest ride requests
            update_ride_requests_table()
            update_dashboard(get_current_user_id())

        elif user_type == "Driver":
            # Create a new window for the dashboard
            dashboard_window = tk.Toplevel(root)
            dashboard_window.title("Drivers Dashboard")
            dashboard_window.geometry("1700x500")  # Larger size

            # Display a welcome message with the user's first name
            welcome_label_text = f"Welcome, {user[2]}!"  # Assuming user's first name is at index 2
            welcome_label = tk.Label(dashboard_window, text=welcome_label_text)
            welcome_label.pack(pady=20)

            # Button to open the take ride window
            btn_request_ride = tk.Button(dashboard_window, text="Take Ride", command=take_ride, state=tk.DISABLED)
            btn_request_ride.pack(side=tk.TOP, pady=10)

            # Cancel Booking button
            btn_cancel_booking = tk.Button(dashboard_window, text="Cancel Ride", command=cancel_booking, state=tk.DISABLED)
            btn_cancel_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Change Booking button
            btn_change_booking = tk.Button(dashboard_window, text="End Ride", command=end_ride, state=tk.DISABLED)
            btn_change_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Treeview for displaying ride requests (right side)
            tree = ttk.Treeview(dashboard_window, columns=("ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"), show="headings")

            # Center all values
            headings = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for heading in headings:
                tree.heading(heading, text=heading, anchor=tk.CENTER)
            
            columns = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for column in columns:
                tree.column(column, anchor=tk.CENTER)

            tree.heading("ID", text="ID", anchor=tk.CENTER)
            tree.heading("Start Address", text="Start Address", anchor=tk.CENTER)
            tree.heading("Destination Address", text="Destination Address", anchor=tk.CENTER)
            tree.heading("Postcode", text="Postcode", anchor=tk.CENTER)
            tree.heading("Date", text="Date", anchor=tk.CENTER)
            tree.heading("Time", text="Time", anchor=tk.CENTER)
            tree.heading("Paid", text="Paid", anchor=tk.CENTER)
            tree.heading("Status", text="Status", anchor=tk.CENTER)
            tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Set up an event handler for selecting a booking in the treeview
            tree.bind("<ButtonRelease-1>", on_tree_select)

            # Set up an event handler for closing the dashboard
            dashboard_window.protocol("WM_DELETE_WINDOW", destroy_dashboard)

            # Hide the main login window
            root.withdraw()

            # Update the table in the dashboard with the latest ride requests
            update_ride_requests_table()#
            update_dashboard(get_current_user_id(), is_driver=True)
            
        elif user_type == "Admin":
            # Create a new window for the dashboard
            dashboard_window = tk.Toplevel(root)
            dashboard_window.title("Admins Dashboard")
            dashboard_window.geometry("1700x500")  # Larger size

            # Display a welcome message with the user's first name
            welcome_label_text = f"Welcome, {user[2]}!"  # Assuming user's first name is at index 2
            welcome_label = tk.Label(dashboard_window, text=welcome_label_text)
            welcome_label.pack(pady=20)

            # Button to open the take ride window
            btn_request_ride = tk.Button(dashboard_window, text="User management", command=user_management, state=tk.NORMAL)
            btn_request_ride.pack(side=tk.TOP, pady=10)

            # Cancel Booking button
            btn_cancel_booking = tk.Button(dashboard_window, text="Booking management", command=booking_management, state=tk.NORMAL)
            btn_cancel_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Change Booking button
            btn_change_booking = tk.Button(dashboard_window, text="Reports and Analytics", command=reports_analytics, state=tk.NORMAL)
            btn_change_booking.pack(side=tk.TOP, padx=5, pady=10)

            # Treeview for displaying ride requests (right side)
            tree = ttk.Treeview(dashboard_window, columns=("ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"), show="headings")

            # Center all values
            headings = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for heading in headings:
                tree.heading(heading, text=heading, anchor=tk.CENTER)
            
            columns = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
            for column in columns:
                tree.column(column, anchor=tk.CENTER)

            tree.heading("ID", text="ID", anchor=tk.CENTER)
            tree.heading("Start Address", text="Start Address", anchor=tk.CENTER)
            tree.heading("Destination Address", text="Destination Address", anchor=tk.CENTER)
            tree.heading("Postcode", text="Postcode", anchor=tk.CENTER)
            tree.heading("Date", text="Date", anchor=tk.CENTER)
            tree.heading("Time", text="Time", anchor=tk.CENTER)
            tree.heading("Paid", text="Paid", anchor=tk.CENTER)
            tree.heading("Status", text="Status", anchor=tk.CENTER)
            tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Set up an event handler for selecting a booking in the treeview
            tree.bind("<ButtonRelease-1>", on_tree_select)

            # Set up an event handler for closing the dashboard
            dashboard_window.protocol("WM_DELETE_WINDOW", destroy_dashboard)

            # Hide the main login window
            root.withdraw()

            # Update the table in the dashboard with the latest ride requests
            update_ride_requests_table()#
            update_dashboard(get_current_user_id(), is_driver=True)
        
                
            
    else:
        messagebox.showerror("Login Failed", "Invalid email, password, or user type")
def user_management():
    global user_tree
    # Create a new window for user management
    user_management_window = tk.Toplevel(dashboard_window)
    user_management_window.title("User Management")

    # Create a treeview to display user details
    user_tree = ttk.Treeview(user_management_window, columns=("ID", "Name", "Email", "User Type"), show="headings")

    # Set column headings
    headings = ["ID", "Name", "Email", "User Type"]
    for heading in headings:
        user_tree.heading(heading, text=heading, anchor=tk.CENTER)
        user_tree.column(heading, width=100, anchor=tk.CENTER)

    # Populate the tree with user data (replace this with your data retrieval logic)
    populate_user_tree(user_tree)

    # Add a "Suspend User" button
    suspend_button = ttk.Button(user_management_window, text="Suspend User", command=suspend_user)
    suspend_button.pack(pady=10)

    # Pack the treeview
    user_tree.pack(expand=True, fill="both")

# Function to populate the user tree with dummy data
def populate_user_tree(tree):
    # Replace this with your data retrieval logic
    cursor.execute('SELECT id, first_name || " " || last_name AS name, email, user_type FROM users')
    users = cursor.fetchall()

    for user in users:
        tree.insert("", "end", values=user)
        
user_tree = None
driver_tree = None



def assign_driver():
    global driver_tree
    # Implement the logic to assign the selected driver to the booking
    selected_booking_item = booking_tree.selection()
    selected_driver_item = driver_tree.selection()

    if selected_booking_item and selected_driver_item:
        # Get booking ID and driver ID from the selected items
        booking_id = booking_tree.item(selected_booking_item)["values"][0]
        driver_id = driver_tree.item(selected_driver_item)["values"][0]

        # Call your assign driver function here, passing the booking_id and driver_id
        # Example: assign_driver_function(booking_id, driver_id)

        # Update the booking in the SQLite database with the assigned driver
        cursor.execute('UPDATE bookings SET driver_id=? WHERE id=?', (driver_id, booking_id))
        conn.commit()

        # Remove the assigned booking from the bookings treeview
        booking_tree.delete(selected_booking_item)

        # Close the assign driver window
        assign_driver_window.destroy()
    else:
        # Show an information message if no booking or driver is selected
        tk.messagebox.showinfo("Info", "Please select both a booking and a driver to assign.")
# Function to suspend the selected user

def suspend_user():
    global user_tree  # Declare user_tree as a global variable
    # Get the selected item from the treeview
    selected_item = user_tree.selection()

    if selected_item:
        # Get user ID from the selected item
        user_id = user_tree.item(selected_item)["values"][0]

        # Call your suspend user function here, passing the user_id
        # Example: suspend_user_function(user_id)

        # Delete the user from the SQLite database
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()

        # Remove the selected item from the treeview
        user_tree.delete(selected_item)
        tk.messagebox.showinfo("Info", "User suspended")
    else:
        # Show an information message if no user is selected
        tk.messagebox.showinfo("Info", "Please select a user to suspend.")

        
def take_ride():
    # Get the first name of the driver
    driver_first_name = get_current_user_first_name()

    # Retrieve the selected booking ID
    selected_item = tree.selection()
    if selected_item:
        booking_id = tree.item(selected_item)["values"][0]

        # Check the status of the selected booking
        cursor.execute('SELECT status FROM bookings WHERE id=?', (booking_id,))
        status = cursor.fetchone()[0]

        # Only proceed if the status is not "Cancelled" or "Completed"
        if status not in ["Cancelled", "Completed"]:
            # Update the status of the selected booking to "Assigned by [Driver's First Name]"
            assigned_status = f"Assigned by {driver_first_name}"
            cursor.execute("UPDATE bookings SET status=? WHERE id=?", (assigned_status, booking_id))
            conn.commit()

            # Refresh the driver dashboard
            update_dashboard(get_current_user_id(), is_driver=True)

            messagebox.showinfo("Info", "Ride assigned successfully.")
        else:
            messagebox.showinfo("Error", "This booking is no longer available for assignment.")
    else:
        messagebox.showerror("Error", "Please select a booking to assign.")
        
    update_dashboard(get_current_user_id(), is_driver=True)


def on_tree_select(event):
    selected_item = tree.selection()
    if selected_item:
        # Get the ID and status of the selected booking
        booking_id, status = tree.item(selected_item)["values"][:2]

        # Enable or disable buttons based on the status
        if status == "Cancelled":
            # If the status is "Cancelled," disable all buttons
            btn_cancel_booking["state"] = tk.DISABLED
            btn_change_booking["state"] = tk.DISABLED
            btn_request_ride["state"] = tk.DISABLED
        else:
            # Enable the Cancel Booking and Change Booking buttons when a booking is selected
            btn_cancel_booking["state"] = tk.NORMAL
            btn_change_booking["state"] = tk.NORMAL

            # Enable the "Take Ride" button for the driver dashboard
            btn_request_ride["state"] = tk.NORMAL
    else:
        # Disable the Cancel Booking, Change Booking, and "Take Ride" buttons when no booking is selected
        btn_cancel_booking["state"] = tk.DISABLED
        btn_change_booking["state"] = tk.DISABLED
        btn_request_ride["state"] = tk.DISABLED  # Set to tk.NORMAL to enable "Take Ride" button



def cancel_booking():
    selected_item = tree.selection()
    if selected_item:
        # Get the ID of the selected booking
        booking_id = tree.item(selected_item)["values"][0]

        # Check the status of the selected booking
        cursor.execute('SELECT status FROM bookings WHERE id=?', (booking_id,))
        status = cursor.fetchone()[0]

        # Only proceed if the status is not "Cancelled" or "Completed"
        if status not in ["Cancelled", "Completed"]:
            # Update the status of the selected booking to "Cancelled"
            cursor.execute('UPDATE bookings SET status="Cancelled" WHERE id=?', (booking_id,))
            conn.commit()

            # Display a success message
            messagebox.showinfo("Booking Cancelled", "Booking cancelled successfully!")

            # Update the table in the dashboard with the latest ride requests
            update_ride_requests_table()
        else:
            # Display an error message if the status is "Cancelled" or "Completed"
            messagebox.showerror("Error", "Cannot cancel a booking with status 'Cancelled' or 'Completed'.")
    else:
        messagebox.showerror("Error", "Please select a booking to cancel.")
        
def booking_management():
    # Create a new window for booking management
    booking_management_window = tk.Toplevel(dashboard_window)
    booking_management_window.title("Booking Management")

    # Treeview for displaying bookings
    global booking_tree
    booking_tree = ttk.Treeview(booking_management_window, columns=("ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"), show="headings")

    # Center all values
    headings = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
    for heading in headings:
        booking_tree.heading(heading, text=heading, anchor=tk.CENTER)

    columns = ["ID", "Start Address", "Destination Address", "Postcode", "Date", "Time", "Paid", "Status"]
    for column in columns:
        booking_tree.column(column, anchor=tk.CENTER)

    booking_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Retrieve and display unassigned bookings from the database
    cursor.execute('SELECT id, start_address, destination_address, postcode, date, time, paid, status FROM bookings WHERE status="Not assigned"')
    bookings = cursor.fetchall()

    for booking in bookings:
        booking_tree.insert("", "end", values=(booking[0], booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7]))




def on_booking_select(event):
    # Enable buttons when a booking is selected
    global btn_cancel_booking, btn_assign_driver
    btn_cancel_booking.config(state=tk.NORMAL)
    btn_assign_driver.config(state=tk.NORMAL)
    
def update_bookings_table():
    # Clear existing items in the treeview
    for item in booking_tree.get_children():
        booking_tree.delete(item)

    # Retrieve and display all bookings
    cursor.execute('SELECT id, user_id, driver_id, start_address, destination_address, date, time, paid, status FROM bookings')
    bookings = cursor.fetchall()

    for booking in bookings:
        booking_tree.insert("", "end", values=(booking[0], booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7], booking[8]))

change_booking_window = None

def change_booking():
    selected_item = tree.selection()
    if selected_item:
        # Get the ID of the selected booking
        booking_id = tree.item(selected_item)["values"][0]

        # Check the status of the selected booking
        cursor.execute('SELECT status FROM bookings WHERE id=?', (booking_id,))
        status = cursor.fetchone()[0]

        # Only proceed if the status is not "Cancelled" or "Completed"
        if status not in ["Cancelled", "Completed"]:
            # Retrieve details of the selected booking using the ID
            cursor.execute('SELECT * FROM bookings WHERE id=?', (booking_id,))
            booking_details = cursor.fetchone()

            if booking_details:
                # Extract details from the tuple (assuming column order)
                start_address, destination_address, postcode, date, time = booking_details[2:7]

                # Create a new window for changing the booking details
                change_booking_window = tk.Toplevel(dashboard_window)
                change_booking_window.title("Change Booking")

                # Labels and entry widgets for changing booking details
                labels = ["Start Address:", "Destination Address:", "Postcode:", "Date (MM/DD/YY):", "Time:"]
                entries = []

                for i, label_text in enumerate(labels):
                    label = tk.Label(change_booking_window, text=label_text)
                    label.grid(row=i, column=0, padx=5, pady=5)

                    entry = tk.Entry(change_booking_window)
                    entry.grid(row=i, column=1, padx=5, pady=5)
                    entries.append(entry)

                # Pre-fill the entry fields with existing booking details
                entries[0].insert(0, start_address)
                entries[1].insert(0, destination_address)
                entries[2].insert(0, postcode)
                entries[3].insert(0, date)
                entries[4].insert(0, time)

                # Button to submit changes to the booking
                btn_submit_changes = tk.Button(change_booking_window, text="Submit Changes", command=lambda: submit_changes_to_booking(entries, booking_id))
                btn_submit_changes.grid(row=len(labels), column=0, columnspan=2, pady=10)
            else:
                messagebox.showerror("Error", "Failed to retrieve booking details.")
        else:
            # Display an error message if the status is "Cancelled" or "Completed"
            messagebox.showerror("Error", "Cannot change a booking with status 'Cancelled' or 'Completed'.")
    else:
        messagebox.showerror("Error", "Please select a booking to change.")


def submit_changes_to_booking(entries, booking_id):
    # ... (Previous code)

    # Close the Change Booking window
    destroy_change_booking_window()
    update_dashboard(get_current_user_id())

# Function to destroy the Change Booking window
def destroy_change_booking_window():
    global change_booking_window  # Declare as a global variable
    if change_booking_window:
        change_booking_window.destroy()


def get_current_user_first_name():
    # Assuming the user is logged in, get the first name of the currently logged-in user (driver)
    email = entry_email_login.get()
    password = entry_password_login.get()
    user_type = var_user_type_login.get()

    cursor.execute('SELECT first_name FROM users WHERE email=? AND password=? AND user_type=?', (email, password, user_type))
    user = cursor.fetchone()

    return user[0] if user else None

def display_receipt(start_address, destination_address, duration, cost):
    receipt_window = tk.Toplevel(dashboard_window)
    receipt_window.title("Ride Receipt")
    receipt_window.geometry("300x300")

    # Display receipt information
    receipt_label = tk.Label(receipt_window, text="Ride Receipt", font=("Helvetica", 16, "bold"))
    receipt_label.pack(pady=10)

    start_label = tk.Label(receipt_window, text=f"Start Address: {start_address}")
    start_label.pack()

    destination_label = tk.Label(receipt_window, text=f"Destination Address: {destination_address}")
    destination_label.pack()

    duration_label = tk.Label(receipt_window, text=f"Duration: {duration} minutes")
    duration_label.pack()

    cost_label = tk.Label(receipt_window, text=f"Cost: £{cost}")
    cost_label.pack()

def end_ride():
    selected_item = tree.selection()
    if selected_item:
        # Get the ID of the selected booking
        booking_id = tree.item(selected_item)["values"][0]
        cursor.execute('SELECT start_address, destination_address FROM bookings WHERE id=?', (booking_id,))
        booking_details = cursor.fetchone()
        
        if booking_details:
            start_address, destination_address = booking_details

            # Calculate random duration and cost
            duration = random.randint(8, 20)
            cost = round(random.uniform(15, 30), 2)
            
        # Check the status of the selected booking
        cursor.execute('SELECT status FROM bookings WHERE id=?', (booking_id,))
        status = cursor.fetchone()[0]
        
        # Only proceed if the status is not "Cancelled" or "Completed"
        if status not in ["Cancelled", "Completed"]:
            # Update the status of the selected booking to "Completed"
            cursor.execute('UPDATE bookings SET status="Completed" WHERE id=?', (booking_id,))
            conn.commit()

            # Display a success message
            messagebox.showinfo("Ride Completed", "Ride completed successfully!")

            display_receipt(start_address, destination_address, duration, cost)
            # Update the driver dashboard table with the latest ride requests
            update_dashboard(get_current_user_id(), is_driver=True)
        else:
            # Display an error message if the status is "Cancelled" or "Completed"
            messagebox.showerror("Error", "Cannot end ride for a booking with status 'Cancelled' or 'Completed'.")
    else:
        messagebox.showerror("Error", "Please select a booking to end the ride.")

    


def submit_changes_to_booking(entries, booking_id):
    # Get updated booking details from entry widgets
    start_address = entries[0].get()
    destination_address = entries[1].get()
    postcode = entries[2].get()
    date = entries[3].get()
    time = entries[4].get()

    # Validate that all fields are filled
    if not all([start_address, destination_address, postcode, date, time]):
        messagebox.showerror("Changes Failed", "Please fill in all fields")
        return

    # Update the booking in the database with the new details
    cursor.execute('''
        UPDATE bookings
        SET start_address=?, destination_address=?, postcode=?, date=?, time=?
        WHERE id=?
    ''', (start_address, destination_address, postcode, date, time, booking_id))
    conn.commit()

    # Display a success message
    messagebox.showinfo("Changes Successful", "Changes to booking submitted successfully!")

    # Close the Change Booking window
    destroy_change_booking_window()

    # Update the table in the dashboard with the latest ride requests
    update_ride_requests_table()

def destroy_change_booking_window():
    change_booking_window.destroy()

def open_signup_window():
    signup_window = tk.Toplevel(root)
    signup_window.title("Signup")

    label_user_type_signup = tk.Label(signup_window, text="Select User Type:")
    label_user_type_signup.grid(row=0, column=0, padx=5, pady=5)
    var_user_type_signup = tk.StringVar()
    var_user_type_signup.set("Customer")
    user_types_signup = ["Customer", "Driver", "Admin"]
    dropdown_user_type_signup = tk.OptionMenu(signup_window, var_user_type_signup, *user_types_signup)
    dropdown_user_type_signup.grid(row=0, column=1, padx=5, pady=5)

    btn_continue_signup = tk.Button(signup_window, text="Continue", command=lambda: show_signup_fields(signup_window, var_user_type_signup.get()))

    btn_continue_signup.grid(row=1, column=0, columnspan=2, pady=10)

def show_signup_fields(signup_window, user_type):
    signup_window.destroy()

    additional_info_window = tk.Toplevel(root)
    additional_info_window.title("Additional Information")

    label_title = tk.Label(additional_info_window, text="Title:")
    label_title.grid(row=0, column=0, padx=5, pady=5)
    entry_title = tk.Entry(additional_info_window)
    entry_title.grid(row=0, column=1, padx=5, pady=5)

    label_email = tk.Label(additional_info_window, text="Email:")
    label_email.grid(row=1, column=0, padx=5, pady=5)
    entry_email = tk.Entry(additional_info_window)
    entry_email.grid(row=1, column=1, padx=5, pady=5)

    label_password = tk.Label(additional_info_window, text="Password:")
    label_password.grid(row=2, column=0, padx=5, pady=5)
    entry_password = tk.Entry(additional_info_window, show="*")
    entry_password.grid(row=2, column=1, padx=5, pady=5)

    if user_type == "Customer":
        label_first_name = tk.Label(additional_info_window, text="First Name:")
        label_first_name.grid(row=3, column=0, padx=5, pady=5)
        entry_first_name = tk.Entry(additional_info_window)
        entry_first_name.grid(row=3, column=1, padx=5, pady=5)

        label_last_name = tk.Label(additional_info_window, text="Last Name:")
        label_last_name.grid(row=4, column=0, padx=5, pady=5)
        entry_last_name = tk.Entry(additional_info_window)
        entry_last_name.grid(row=4, column=1, padx=5, pady=5)

        label_phone_number = tk.Label(additional_info_window, text="Phone Number:")
        label_phone_number.grid(row=5, column=0, padx=5, pady=5)
        entry_phone_number = tk.Entry(additional_info_window)
        entry_phone_number.grid(row=5, column=1, padx=5, pady=5)

        label_card_number = tk.Label(additional_info_window, text="Card Number:")
        label_card_number.grid(row=6, column=0, padx=5, pady=5)
        entry_card_number = tk.Entry(additional_info_window)
        entry_card_number.grid(row=6, column=1, padx=5, pady=5)

    elif user_type == "Driver":
        label_first_name = tk.Label(additional_info_window, text="First Name:")
        label_first_name.grid(row=3, column=0, padx=5, pady=5)
        entry_first_name = tk.Entry(additional_info_window)
        entry_first_name.grid(row=3, column=1, padx=5, pady=5)

        label_last_name = tk.Label(additional_info_window, text="Last Name:")
        label_last_name.grid(row=4, column=0, padx=5, pady=5)
        entry_last_name = tk.Entry(additional_info_window)
        entry_last_name.grid(row=4, column=1, padx=5, pady=5)

        label_phone_number = tk.Label(additional_info_window, text="Phone Number:")
        label_phone_number.grid(row=5, column=0, padx=5, pady=5)
        entry_phone_number = tk.Entry(additional_info_window)
        entry_phone_number.grid(row=5, column=1, padx=5, pady=5)

        label_card_number = tk.Label(additional_info_window, text="Card Number:")
        label_card_number.grid(row=6, column=0, padx=5, pady=5)
        entry_card_number = tk.Entry(additional_info_window)
        entry_card_number.grid(row=6, column=1, padx=5, pady=5)

        label_plate_number = tk.Label(additional_info_window, text="Plate Number:")
        label_plate_number.grid(row=7, column=0, padx=5, pady=5)
        entry_plate_number = tk.Entry(additional_info_window)
        entry_plate_number.grid(row=7, column=1, padx=5, pady=5)

    elif user_type == "Admin":
        label_first_name = tk.Label(additional_info_window, text="First Name:")
        label_first_name.grid(row=3, column=0, padx=5, pady=5)
        entry_first_name = tk.Entry(additional_info_window)
        entry_first_name.grid(row=3, column=1, padx=5, pady=5)

        label_last_name = tk.Label(additional_info_window, text="Last Name:")
        label_last_name.grid(row=4, column=0, padx=5, pady=5)
        entry_last_name = tk.Entry(additional_info_window)
        entry_last_name.grid(row=4, column=1, padx=5, pady=5)

        label_employee_code = tk.Label(additional_info_window, text="Employee Code:")
        label_employee_code.grid(row=5, column=0, padx=5, pady=5)
        entry_employee_code = tk.Entry(additional_info_window)
        entry_employee_code.grid(row=5, column=1, padx=5, pady=5)

    btn_signup = tk.Button(additional_info_window, text="Signup", command=lambda: signup(user_type, entry_title.get(), entry_first_name.get(), entry_last_name.get(),
                                                                                       entry_phone_number.get() if user_type != "Admin" else None,
                                                                                       entry_email.get(), entry_password.get(),
                                                                                       entry_card_number.get() if user_type != "Admin" else None,
                                                                                       entry_plate_number.get() if user_type == "Driver" else None,
                                                                                       entry_employee_code.get() if user_type == "Admin" else None))
    btn_signup.grid(row=8 if user_type == "Customer" else 9, column=0, columnspan=2, pady=10)

def signup(user_type, title, first_name, last_name, phone_number, email, password, card_number, plate_number=None, employee_code=None):
    # Check if the email or phone number already exists in the database
    cursor.execute('SELECT id FROM users WHERE email=? OR phone_number=?', (email, phone_number))
    existing_user = cursor.fetchone()

    if existing_user:
        messagebox.showerror("Signup Failed", "An account with this email or phone number already exists.")
        return

    # If user_type is Admin and the employee code is not valid
    if user_type == "Admin" and employee_code != "0000":
        messagebox.showerror("Signup Failed", "Invalid employee code")
        return

    # Insert the new user into the database
    cursor.execute('INSERT INTO users (title, first_name, last_name, phone_number, email, password, card_number, plate_number, employee_code, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (title, first_name, last_name, phone_number, email, password, card_number, plate_number, employee_code, user_type))
    conn.commit()

    messagebox.showinfo("Signup Successful", "Account created successfully!")






# GUI setup
root = tk.Tk()
width = 600 # Width 
height = 300 # Height
screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight() # Height of the screen
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry('%dx%d+%d+%d' % (width, height, x, y))
root.title("Login System")

frame_login = tk.Frame(root)
frame_login.pack(padx=10, pady=10)

label_email_login = tk.Label(frame_login, text="Email:")
label_email_login.grid(row=0, column=0, padx=5, pady=5)
entry_email_login = tk.Entry(frame_login)
entry_email_login.grid(row=0, column=1, padx=5, pady=5)

label_password_login = tk.Label(frame_login, text="Password:")
label_password_login.grid(row=1, column=0, padx=5, pady=5)
entry_password_login = tk.Entry(frame_login, show="*")
entry_password_login.grid(row=1, column=1, padx=5, pady=5)

label_user_type_login = tk.Label(frame_login, text="Select User Type:")
label_user_type_login.grid(row=2, column=0, padx=5, pady=5)
var_user_type_login = tk.StringVar()
var_user_type_login.set("Customer")
user_types_login = ["Customer", "Driver", "Admin"]
dropdown_user_type_login = tk.OptionMenu(frame_login, var_user_type_login, *user_types_login)
dropdown_user_type_login.grid(row=2, column=1, padx=5, pady=5)

btn_login = tk.Button(frame_login, text="Login", command=login)
btn_login.grid(row=3, column=0, columnspan=2, pady=10)

btn_signup = tk.Button(root, text="Signup", command=open_signup_window)
btn_signup.pack(pady=10)

root.mainloop()


import streamlit as st
import sqlite3
from datetime import datetime
from faker import Faker
import random
import os

# Application-wide constants
MAX_LEAVE_PER_YEAR = 24
MAX_CONSECUTIVE_DAYS = 10
DB_NAME = "leave_management.db"

fake = Faker()

# --- Database Helper Functions ---

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary database tables for employees and leave requests if they don't exist."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT CHECK(role IN ('employee', 'manager')) NOT NULL,
            leave_balance INTEGER NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            leave_reason TEXT,
            status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) NOT NULL DEFAULT 'pending',
            applied_on TEXT NOT NULL,
            processed_on TEXT,
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        )
    ''')
    conn.commit()
    conn.close()

def initialize_data():
    """Wipes existing data and populates the database with new, random employees and a manager."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM leave_requests')
    c.execute('DELETE FROM employees')
    conn.commit()
    c.execute('INSERT INTO employees (name, role, leave_balance) VALUES (?, ?, ?)',
              (fake.name(), 'manager', MAX_LEAVE_PER_YEAR))
    for _ in range(7):
        c.execute('INSERT INTO employees (name, role, leave_balance) VALUES (?, ?, ?)',
                  (fake.name(), 'employee', random.randint(20, 23)))
    conn.commit()
    conn.close()

def is_data_initialized():
    """Checks if the database is populated with initial data by counting employee records."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM employees')
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_employees(role=None):
    """Fetches a list of all employees, optionally filtered by their role."""
    conn = get_connection()
    c = conn.cursor()
    if role:
        c.execute('SELECT * FROM employees WHERE role=? ORDER BY name', (role,))
    else:
        c.execute('SELECT * FROM employees ORDER BY name')
    rows = c.fetchall()
    conn.close()
    return rows

def get_leave_requests(emp_id=None, status=None):
    """Fetches leave requests, optionally filtered by employee ID or status."""
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT lr.*, e.name FROM leave_requests lr JOIN employees e ON lr.emp_id = e.emp_id"
    params, conditions = [], []
    if emp_id is not None:
        conditions.append("lr.emp_id = ?")
        params.append(emp_id)
    if status is not None:
        conditions.append("lr.status = ?")
        params.append(status)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY applied_on DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_employee(emp_id):
    """Fetches a single employee record using their ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM employees WHERE emp_id=?', (emp_id,))
    emp = c.fetchone()
    conn.close()
    return emp

def add_employee(name, role, leave_balance):
    """Adds a new employee record to the database."""
    try:
        name = name.strip()
        role = role.strip().lower()
        conn = get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO employees (name, role, leave_balance) VALUES (?, ?, ?)',
                  (name, role, leave_balance))
        conn.commit()
        conn.close()
        return True, f"Successfully added new {role}: {name}."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def apply_leave(emp_id, start_date, end_date, reason):
    """Submits a new leave request for an employee to the database."""
    try:
        s_date = datetime.strptime(start_date, "%Y-%m-%d")
        e_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."
    if e_date < s_date:
        return False, "End date cannot be before start date."
    if s_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        return False, "Start date cannot be in the past."
    total_days = (e_date - s_date).days + 1
    if total_days > MAX_CONSECUTIVE_DAYS:
        return False, f"Cannot apply for more than {MAX_CONSECUTIVE_DAYS} consecutive days."
    emp = get_employee(emp_id)
    if not emp:
        return False, "Employee not found."
    if total_days > emp['leave_balance']:
        return False, "Insufficient leave balance."
    approved_leaves = get_leave_requests(emp_id, status='approved')
    for leave in approved_leaves:
        lr_start = datetime.strptime(leave['start_date'], "%Y-%m-%d")
        lr_end = datetime.strptime(leave['end_date'], "%Y-%m-%d")
        if not (e_date < lr_start or s_date > lr_end):
            return False, "Leave dates overlap with existing approved leave."
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO leave_requests (emp_id, start_date, end_date, leave_reason, status, applied_on)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (emp_id, start_date, end_date, reason, 'pending', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True, "Leave application submitted successfully."

def approve_leave(manager_id, leave_id):
    """Approves a pending leave request, deducting the days from the employee's balance."""
    manager = get_employee(manager_id)
    if not manager or manager['role'] != 'manager':
        return False, "Not authorized."
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM leave_requests WHERE leave_id=?', (leave_id,))
    leave = c.fetchone()
    if not leave:
        conn.close()
        return False, "Leave request not found."
    if leave['status'] != 'pending':
        conn.close()
        return False, "Leave request already processed."
    emp_id = leave['emp_id']
    pending_requests = get_leave_requests(emp_id=emp_id, status='pending')
    if len(pending_requests) > 1:
        conn.close()
        return False, "This employee has multiple pending leave requests. Only one can be approved at a time."
    start_date = datetime.strptime(leave['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(leave['end_date'], "%Y-%m-%d")
    days = (end_date - start_date).days + 1
    emp = get_employee(emp_id)
    if emp['leave_balance'] < days:
        conn.close()
        return False, "Employee has insufficient leave balance."
    new_balance = emp['leave_balance'] - days
    c.execute('UPDATE employees SET leave_balance=? WHERE emp_id=?', (new_balance, emp_id))
    c.execute('UPDATE leave_requests SET status=?, processed_on=? WHERE leave_id=?',
              ('approved', datetime.now().isoformat(), leave_id))
    conn.commit()
    conn.close()
    return True, "Leave approved."

def reject_leave(manager_id, leave_id):
    """Rejects a pending leave request without affecting the employee's leave balance."""
    manager = get_employee(manager_id)
    if not manager or manager['role'] != 'manager':
        return False, "Not authorized."
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM leave_requests WHERE leave_id=?', (leave_id,))
    leave = c.fetchone()
    if not leave:
        conn.close()
        return False, "Leave request not found."
    if leave['status'] != 'pending':
        conn.close()
        return False, "Leave request already processed."
    c.execute('UPDATE leave_requests SET status=?, processed_on=? WHERE leave_id=?',
              ('rejected', datetime.now().isoformat(), leave_id))
    conn.commit()
    conn.close()
    return True, "Leave rejected"

# --- Main Application Logic ---

# Create database and tables if they do not exist
if not os.path.exists(DB_NAME):
    create_tables()

# Initialize dummy data on the first run of the app
if not is_data_initialized():
    initialize_data()

# --- Streamlit UI Setup ---

st.title("Employee Leave Tracker")

# Select role to switch between Employee and Manager portals
user_role = st.sidebar.selectbox("Select your role", ("Employee", "Manager"))

# --- Employee Portal ---
if user_role == "Employee":
    st.header("Employee Portal")
    employees = get_employees(role="employee")
    
    if not employees:
        st.info("No employee data found in the database. Please initialize the data.")
    else:
        employee_id = st.sidebar.selectbox(
            "Select your name",
            [(e['emp_id'], e['name']) for e in employees],
            format_func=lambda x: x[1]
        )[0]
        emp = get_employee(employee_id)
        st.write(f"Welcome, {emp['name']}!")
        st.write(f"Your current leave balance: **{emp['leave_balance']} days**")

        st.subheader("Apply for Leave")
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        leave_reason = st.text_area("Reason for leave")
        if st.button("Submit Leave Application"):
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            success, msg = apply_leave(employee_id, start_str, end_str, leave_reason)
            if success:
                st.success(msg)
            else:
                st.error(msg)
        
        st.subheader("Your Leave Requests")
        leave_requests = get_leave_requests(emp_id=employee_id)
        if leave_requests:
            for lr in leave_requests:
                st.write(
                    f"ID: {lr['leave_id']} | Status: {lr['status'].capitalize()} | "
                    f"From: {lr['start_date']} To: {lr['end_date']} | Reason: {lr['leave_reason'] or 'No reason provided'}"
                )
        else:
            st.info("No leave requests found.")

# --- Manager Portal ---
elif user_role == "Manager":
    st.header("Manager Portal")
    managers = get_employees(role="manager")
    if not managers:
        st.info("No manager data found in the database. Please initialize the data.")
    else:
        manager_id = st.sidebar.selectbox(
            "Select your name",
            [(m['emp_id'], m['name']) for m in managers],
            format_func=lambda x: x[1]
        )[0]
        st.write(f"Welcome, Manager {get_employee(manager_id)['name']}!")

        st.subheader("Pending Leave Requests")
        pending_leaves = get_leave_requests(status='pending')
        st.write(f"Pending requests found: {len(pending_leaves)}")
        if pending_leaves:
            for lr in pending_leaves:
                with st.container(border=True):
                    st.write(
                        f"Leave ID: **{lr['leave_id']}** | Employee: **{lr['name']}**"
                    )
                    st.write(
                        f"**Dates:** {lr['start_date']} to {lr['end_date']}"
                    )
                    st.write(
                        f"**Reason:** {lr['leave_reason'] or 'No reason provided'}"
                    )
                    cols = st.columns(2)
                    with cols[0]:
                        if st.button("Approve", key=f"approve_{lr['leave_id']}"):
                            success, msg = approve_leave(manager_id, lr['leave_id'])
                            if success:
                                st.success(msg)
                                st.rerun() 
                            else:
                                st.error(msg)
                    with cols[1]:
                        if st.button("Reject", key=f"reject_{lr['leave_id']}"):
                            success, msg = reject_leave(manager_id, lr['leave_id'])
                            if success:
                                st.success(msg)
                                st.rerun() 
                            else:
                                st.error(msg)
        else:
            st.info("No pending leave requests.")
    
    # Form to add a new employee to the database
    st.subheader("Add New Employee")
    with st.form("add_employee_form"):
        new_emp_name = st.text_input("Employee Name", help="Enter the full name of the new employee.")
        new_emp_role = st.selectbox("Role", ["Employee", "Manager"])
        new_emp_balance = st.number_input("Starting Leave Balance", min_value=0, max_value=MAX_LEAVE_PER_YEAR, value=MAX_LEAVE_PER_YEAR)
        submitted = st.form_submit_button("Add Employee")
        if submitted:
            if new_emp_name:
                success, msg = add_employee(new_emp_name, new_emp_role, new_emp_balance)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Employee name cannot be empty.")
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Constants
DB_NAME = "leave_management.db"
CSV_FILE_NAME = "employee_leave_history.csv"

def get_connection():
    """Establishes and returns a database connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def export_employee_leave_history_to_csv():
    """
    Fetches all employee and leave request data, calculates leave duration,
    and exports it into a CSV file for better analysis of leave history.
    """
    if not os.path.exists(DB_NAME):
        print(f"Error: Database file '{DB_NAME}' not found. "
              "Please ensure the main Streamlit application has been run at least once to create the database.")
        return

    conn = get_connection()
    c = conn.cursor()

    try:
        # SQL query to join employees and leave_requests tables
        # It selects all relevant fields to provide a full leave history context.
        c.execute('''
            SELECT
                e.emp_id,
                e.name AS EmployeeName,
                e.role AS EmployeeRole,
                e.leave_balance AS CurrentLeaveBalance,
                lr.leave_id,
                lr.start_date AS LeaveStartDate,
                lr.end_date AS LeaveEndDate,
                lr.leave_reason AS ReasonForLeave,
                lr.status AS LeaveStatus,
                lr.applied_on AS DateApplied,
                lr.processed_on AS DateProcessed
            FROM leave_requests lr
            JOIN employees e ON lr.emp_id = e.emp_id
            ORDER BY e.name, lr.start_date DESC
        ''')
        rows = c.fetchall()

        if not rows:
            print("No employee leave history found in the database.")
            return

        # Prepare a list of dictionaries to build the DataFrame
        data_for_df = []
        for row in rows:
            row_dict = dict(row)
            
            # --- NEW LOGIC: Clean the ReasonForLeave field ---
            if row_dict['ReasonForLeave'] is not None:
                # Replace any newline characters with a space
                row_dict['ReasonForLeave'] = row_dict['ReasonForLeave'].replace('\n', ' ')
            # --- END OF NEW LOGIC ---
            
            # Calculate the number of days for the leave request
            try:
                start_date = datetime.strptime(row_dict['LeaveStartDate'], "%Y-%m-%d")
                end_date = datetime.strptime(row_dict['LeaveEndDate'], "%Y-%m-%d")
                row_dict['NumberOfDays'] = (end_date - start_date).days + 1
            except (ValueError, TypeError):
                row_dict['NumberOfDays'] = "N/A" # Indicate if dates are malformed or missing

            data_for_df.append(row_dict)

        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(data_for_df)
        
        # Define a logical order for the columns in the CSV for better readability
        ordered_columns = [
            'emp_id',
            'EmployeeName',
            'EmployeeRole',
            'CurrentLeaveBalance',
            'leave_id',
            'LeaveStartDate',
            'LeaveEndDate',
            'NumberOfDays',
            'ReasonForLeave',
            'LeaveStatus',
            'DateApplied',
            'DateProcessed'
        ]
        
        # Ensure only existing columns are included and in the desired order
        df = df[[col for col in ordered_columns if col in df.columns]]

        # Export the DataFrame to a CSV file
        df.to_csv(CSV_FILE_NAME, index=False)

        print(f"Success: Employee leave history has been exported to '{CSV_FILE_NAME}'.")

    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    export_employee_leave_history_to_csv()
import sqlite3
import os

# --- Constants ---
# Name of the SQLite database file
DB_NAME = "leave_management.db"

# --- Database Connection Function ---

def get_connection():
    """
    Establishes a connection to the SQLite database.
    The row_factory is set to sqlite3.Row to allow accessing columns by name.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- Data Display Function ---

def display_employee_data_in_terminal():
    """
    Connects to the database, fetches all employee details (ID, Name, Role),
    and prints them directly to the terminal.
    """
    # Check if the database file exists before attempting to connect
    if not os.path.exists(DB_NAME):
        print(f"Error: Database file '{DB_NAME}' not found.")
        print("Please ensure your Streamlit application has been run at least once to create and populate the database.")
        return

    conn = None # Initialize connection to None
    try:
        conn = get_connection()
        c = conn.cursor()

        # SQL query to select only employee-specific data: ID, Name, and Role.
        # Data is ordered by name for readability.
        c.execute('''
            SELECT
                emp_id AS EmployeeID,
                name AS EmployeeName,
                role AS EmployeeRole
            FROM employees
            ORDER BY name ASC
        ''')
        rows = c.fetchall()

        # If no employee data is found, inform the user.
        if not rows:
            print("No employee data found in the database.")
            return

        print("\n--- Employee Data ---")
        print(f"{'ID':<5} {'Name':<25} {'Role':<15}") # Header for terminal output
        print("-" * 45) # Separator line

        # Iterate through each fetched row and print its details.
        for row in rows:
            # Access columns by their aliases defined in the SQL query
            employee_id = row['EmployeeID']
            employee_name = row['EmployeeName']
            employee_role = row['EmployeeRole']
            print(f"{employee_id:<5} {employee_name:<25} {employee_role:<15}")

        print("---------------------\n")

    except sqlite3.Error as e:
        # Catch and report any SQLite specific errors during database operations.
        print(f"Database error occurred: {e}")
    except Exception as e:
        # Catch and report any other unexpected errors.
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the database connection is always closed.
        if conn:
            conn.close()

# --- Script Entry Point ---

if __name__ == "__main__":
    display_employee_data_in_terminal()

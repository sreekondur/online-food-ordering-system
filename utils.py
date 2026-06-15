import mysql.connector
from mysql.connector import Error
import os
from tkinter import messagebox
from config import Config

def connect_to_database():
    """
    Establishes a connection to the MySQL database using credentials from config.py.
    
    Returns:
        connection (mysql.connector.connection): Database connection object
    """
    try:
        # Connect to the database using Config class
        connection = mysql.connector.connect(
            host=Config.db_host,
            user=Config.user,
            password=Config.password,
            database=Config.database
        )
        
        # Check if the connection was successful
        if connection.is_connected():
            return connection
            
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """
    Executes a SQL query with optional parameters and returns results if requested.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch (bool, optional): Whether to fetch and return results
        
    Returns:
        result: Query results if fetch=True, otherwise None
    """
    connection = connect_to_database()
    result = None
    
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                
            cursor.close()
            
    except Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            
    return result

def validate_user(email, password):
    """
    Validates user credentials and returns user info if valid.
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        dict: User information if credentials are valid, otherwise None
    """
    # In a real application, passwords should be hashed and not stored or compared as plaintext
    query = """
        SELECT UserID, FirstName, LastName, Email, Role
        FROM User 
        WHERE Email = %s AND Password = %s
    """
    
    result = execute_query(query, (email, password), fetch=True)
    
    if result and len(result) > 0:
        return result[0]
    else:
        return None

def register_user(first_name, last_name, email, password, role='customer'):
    """
    Registers a new user in the database.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email
        password (str): User's password
        role (str, optional): User role (default: 'customer')
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    # Check if user already exists
    check_query = "SELECT UserID FROM User WHERE Email = %s"
    existing_user = execute_query(check_query, (email,), fetch=True)
    
    if existing_user:
        messagebox.showerror("Registration Error", "A user with this email already exists.")
        return False
    
    # Create new user
    insert_query = """
        INSERT INTO User (FirstName, LastName, Email, Password, Role)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        execute_query(insert_query, (first_name, last_name, email, password, role))
        return True
    except Exception as e:
        messagebox.showerror("Registration Error", f"Failed to register user: {e}")
        return False
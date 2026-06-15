import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re  # For password validation
import bcrypt
from utils import connect_to_database, execute_query
from CTkMessagebox import CTkMessagebox  # Assuming you'll install this package

# Function to validate user credentials
def validate_user(email, password):
    """
    Validates user login credentials.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        dict or None: User data if credentials are valid, None otherwise
    """
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
            return user
        return None
    except Exception as err:
        print(f"Database Error: {err}")
        return None


# Function to add a new user
def register_user(first_name, last_name, email, password, role='customer'):
    """
    Registers a new user in the database with a hashed password.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email
        password (str): User's password (will be hashed)
        role (str): User's role (default: 'customer')
        
    Returns:
        bool: True if registration was successful, False otherwise
    """
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Check if email already exists
        check_query = "SELECT UserID FROM User WHERE Email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert the new user
        query = """
        INSERT INTO User (FirstName, LastName, Email, Password, Role)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, hashed_password, role))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as err:
        print(f"Database Error: {err}")
        return False


# Function to reset a user's password
def reset_password_logic(email, new_password):
    """
    Resets a user's password if the email exists in the database.
    
    Args:
        email (str): User's email
        new_password (str): New password to set
        
    Returns:
        tuple: (success_boolean, message_string)
    """
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Check if email exists
        query = "SELECT UserID FROM User WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return False, "Email not found."

        # Update password with hash
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_query = "UPDATE User SET Password = %s WHERE Email = %s"
        cursor.execute(update_query, (hashed_password, email))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Password reset successfully."
    except Exception as err:
        return False, f"Database error: {err}"


# Function to check password strength
def is_password_strong(password):
    """
    Checks if a password meets minimum security requirements.
    
    Args:
        password (str): Password to check
        
    Returns:
        bool: True if password is strong, False otherwise
    """
    # Password must be at least 8 characters, have 1 uppercase letter and 1 special character
    if len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return True
    return False


class LoginWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="#FF7F50")  # Coral background matching the design
        
        # Initialize variable for tracking current view
        self.is_signup_mode = False
        
        # Set window size to properly fit the layout
        self.master.geometry("950x650")
        self.master.minsize(950, 650)
        
        # Try to load background image (combined girl and mobile)
        try:
            background_image_path = "static/images/bg_img.png"  # Path to your combined background image
            pil_image = Image.open(background_image_path)
            self.background_image = ctk.CTkImage(light_image=pil_image, size=(950, 650))
            
            # Background Label
            self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Set a solid color as fallback
            self.configure(fg_color="#FF7F50")  # Coral background as fallback

        # Form Frame (white login box on the right)
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15, width=450, height=580)
        self.form_frame.place(relx=0.735, rely=0.5, anchor="center")
        self.form_frame.pack_propagate(False)
        
        # Initialize with the login view
        self.create_login_view()
        
        # Initialize with the login view
        self.create_login_view()

    def clear_form_frame(self):
        """Clear all widgets in the form frame."""
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def create_login_view(self):
        """Create Login View that resembles the Figma design while preserving functionality."""
        self.clear_form_frame()
        self.is_signup_mode = False

        # Create an inner frame to hold the form content
        self.inner_frame = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Welcome Back! Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Welcome Back!", 
            font=("Arial", 24, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 30), anchor="center")

        # User Type Selection (hidden but functional)
        # self.user_type_var = ctk.StringVar(value="customer")
        
        # Email
        self.email_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter your email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        # Email error message (hidden initially)
        self.email_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red", 
            width=380,
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 10))

        # Password
        self.password_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.inner_frame, 
            placeholder_text="Enter your password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.password_entry.pack(pady=(0, 5), fill="x")
        
        # Password error message (hidden initially)
        self.password_error_label = ctk.CTkLabel(
            self.inner_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red", 
            width=380,
            anchor="w"
        )
        self.password_error_label.pack(anchor="w", pady=(0, 5))

        # Show Password Checkbox 
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.inner_frame, 
            text="Show Password", 
            variable=self.show_password_var, 
            command=self.toggle_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_password_checkbox.pack(anchor="w", pady=(0, 15))

        # Login Button - Orange button that matches the design
        self.login_button = ctk.CTkButton(
            self.inner_frame, 
            text="Login", 
            command=self.login, 
            width=380, 
            height=45,
            fg_color="#FF5722",  # Orange color from the design
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(pady=(0, 20))

        # Bottom options frame for "Forgot Password?" and "Register Now"
        self.options_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 0))
        
        # Forgot Password Link - Left side
        self.forgot_password_label = ctk.CTkLabel(
            self.options_frame, 
            text="Forgot Password?", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.forgot_password_label.pack(side="left")
        self.forgot_password_label.bind("<Button-1>", lambda e: self.create_forgot_password_view())
        
        # Register Now Link - Right side
        self.register_now_label = ctk.CTkLabel(
            self.options_frame, 
            text="Register Now", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.register_now_label.pack(side="right")
        self.register_now_label.bind("<Button-1>", lambda e: self.create_signup_view())

    def create_signup_view(self):
        """Create Sign-Up View."""
        self.clear_form_frame()
        self.is_signup_mode = True

        # Create scrollable frame to accommodate all form fields
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.form_frame, 
            fg_color="white", 
            corner_radius=15,
            width=400,
            height=520
        )
        self.scrollable_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Create a New Account", 
            font=("Arial", 20, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(10, 20), anchor="center")

        # First Name
        self.first_name_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="First Name", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.first_name_label.pack(anchor="w", pady=(0, 5))
        
        self.first_name_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your first name", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.first_name_entry.pack(pady=(0, 5), fill="x")
        
        self.first_name_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.first_name_error_label.pack(anchor="w", pady=(0, 5))

        # Last Name
        self.last_name_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Last Name", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.last_name_label.pack(anchor="w", pady=(0, 5))
        
        self.last_name_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your last name", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.last_name_entry.pack(pady=(0, 5), fill="x")
        
        self.last_name_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.last_name_error_label.pack(anchor="w", pady=(0, 5))

        # Email
        self.email_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        self.email_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 5))

        # Password
        self.password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.password_entry.pack(pady=(0, 5), fill="x")
        
        # Show Password Checkbox 
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame, 
            text="Show Password", 
            variable=self.show_password_var, 
            command=self.toggle_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_password_checkbox.pack(anchor="w", pady=(5, 5))
        
        self.password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.password_error_label.pack(anchor="w", pady=(0, 5))
        
        # Password requirements hint
        self.password_hint_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password must be at least 8 characters with 1 uppercase\nletter and 1 special character", 
            font=("Arial", 10), 
            text_color="#777777",
            anchor="w"
        )
        self.password_hint_label.pack(anchor="w", pady=(0, 10))

        # User Type (Account Type)
        self.user_type_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Account Type", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.user_type_label.pack(anchor="w", pady=(0, 5))
        
        # Create a frame for radio buttons
        self.radio_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.radio_frame.pack(fill="x", pady=(0, 10))
        
        # Default role is customer
        self.user_type_var = ctk.StringVar(value="customer")
        
        # Radio buttons for user types
        self.customer_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="Customer",
            variable=self.user_type_var,
            value="customer",
            font=("Arial", 12),
            fg_color="#FF5722",
            border_color="#FF5722"
        )
        self.customer_radio.pack(side="left", padx=(0, 20))
        
        self.restaurant_radio = ctk.CTkRadioButton(
            self.radio_frame,
            text="Restaurant",
            variable=self.user_type_var,
            value="restaurant",
            font=("Arial", 12),
            fg_color="#FF5722",
            border_color="#FF5722"
        )
        self.restaurant_radio.pack(side="left")

        # Sign-Up Button
        self.signup_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Sign Up", 
            command=self.signup, 
            width=380, 
            height=45,
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.signup_button.pack(pady=(10, 15))

        # Back to Login Button - text link instead of button to match design
        self.back_to_login_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Already have an account? Login", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.back_to_login_label.pack(pady=(0, 10))
        self.back_to_login_label.bind("<Button-1>", lambda e: self.create_login_view()).signup_button.pack(pady=(10, 15))

        # Back to Login Button - text link instead of button to match design
        self.back_to_login_label = ctk.CTkLabel(
            self.inner_frame, 
            text="Already have an account? Login", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.back_to_login_label.pack(pady=(0, 10))
        self.back_to_login_label.bind("<Button-1>", lambda e: self.create_login_view())

    def create_forgot_password_view(self):
        """Create Forgot Password View."""
        self.clear_form_frame()

        # Create a scrollable frame to accommodate all form fields
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.form_frame, 
            fg_color="white", 
            corner_radius=15,
            width=400,
            height=520
        )
        self.scrollable_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Reset Your Password", 
            font=("Arial", 20, "bold"), 
            text_color="#333333"
        )
        self.title_label.pack(pady=(10, 20), anchor="center")

        # Email
        self.email_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Email", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter your registered email", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.email_entry.pack(pady=(0, 5), fill="x")
        
        self.email_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.email_error_label.pack(anchor="w", pady=(0, 10))

        # New Password
        self.new_password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="New Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.new_password_label.pack(anchor="w", pady=(0, 5))
        
        self.new_password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Enter new password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.new_password_entry.pack(pady=(0, 5), fill="x")
        
        # Show Password Checkbox 
        self.show_new_password_var = ctk.BooleanVar(value=False)
        self.show_new_password_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame, 
            text="Show Password", 
            variable=self.show_new_password_var, 
            command=self.toggle_new_password,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        self.show_new_password_checkbox.pack(anchor="w", pady=(5, 5))
        
        self.new_password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.new_password_error_label.pack(anchor="w", pady=(0, 10))

        # Confirm Password
        self.confirm_password_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Confirm Password", 
            font=("Arial", 14), 
            text_color="#555555",
            anchor="w"
        )
        self.confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            self.scrollable_frame, 
            placeholder_text="Re-enter new password", 
            show="*", 
            width=380, 
            height=40,
            border_color="#DDDDDD",
            corner_radius=5
        )
        self.confirm_password_entry.pack(pady=(0, 5), fill="x")
        
        self.confirm_password_error_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="", 
            font=("Arial", 10), 
            text_color="red",
            anchor="w"
        )
        self.confirm_password_error_label.pack(anchor="w", pady=(0, 5))
        
        # Password requirements hint
        self.password_hint_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Password must be at least 8 characters with 1 uppercase\nletter and 1 special character", 
            font=("Arial", 10), 
            text_color="#777777",
            anchor="w"
        )
        self.password_hint_label.pack(anchor="w", pady=(0, 15))

        # Reset Password Button
        self.reset_password_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Reset Password", 
            command=self.reset_password, 
            width=380, 
            height=45,
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 14, "bold")
        )
        self.reset_password_button.pack(pady=(10, 15))

        # Back to Login - text link
        self.back_to_login_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Back to Login", 
            font=("Arial", 12), 
            text_color="#FF5722", 
            cursor="hand2"
        )
        self.back_to_login_label.pack(pady=(0, 10))
        self.back_to_login_label.bind("<Button-1>", lambda e: self.create_login_view())
        
    def toggle_new_password(self):
        """Toggle new password visibility based on checkbox state."""
        if self.show_new_password_var.get():
            self.new_password_entry.configure(show="")
        else:
            self.new_password_entry.configure(show="*")

    def toggle_password(self):
        """Toggle password visibility based on checkbox state."""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def login(self):
        """Handle login attempt."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        # user_type = self.user_type_var.get()

        # Reset error messages
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")
        
        # Validate input
        if not email:
            self.email_error_label.configure(text="Email is required.")
            return
        elif "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            return

        if not password:
            self.password_error_label.configure(text="Password is required.")
            return

        # Verify credentials
        user = validate_user(email, password)
        if user :
            # Store user information in the main app
            self.master.current_user = user
            self.master.user_role = user['Role']
            
            # Show the appropriate dashboard
            self.master.show_dashboard()
        else:
            # Show error message for invalid credentials
            self.password_error_label.configure(text="Invalid email or password.")

    def signup(self):
        """Handle user registration."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()

        # Reset error messages
        self.first_name_error_label.configure(text="")
        self.last_name_error_label.configure(text="")
        self.email_error_label.configure(text="")
        self.password_error_label.configure(text="")

        valid = True  # Validation flag

        # Validate fields
        if not first_name:
            self.first_name_error_label.configure(text="First Name is required.")
            valid = False
            
        if not last_name:
            self.last_name_error_label.configure(text="Last Name is required.")
            valid = False
            
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Invalid email address.")
            valid = False
            
        if not is_password_strong(password):
            self.password_error_label.configure(
                text="Password must meet all requirements."
            )
            valid = False

        if valid:
            # If all fields are valid, attempt to create the user
            if register_user(first_name, last_name, email, password, user_type):
                # Use the CTkMessagebox instead of standard messagebox
                CTkMessagebox(
                    title="Account Created", 
                    message="Your account has been created successfully.\nPlease login with your credentials.", 
                    icon="check",
                    option_1="OK"
                )
                self.create_login_view()  # Redirect to login view on success
            else:
                self.email_error_label.configure(text="Email already exists or registration failed.")

    def reset_password(self):
        """Handle password reset request."""
        email = self.email_entry.get().strip()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Reset error labels
        self.email_error_label.configure(text="")
        self.new_password_error_label.configure(text="")
        self.confirm_password_error_label.configure(text="")

        valid = True  # Validation flag

        # Validate email
        if not email or "@" not in email or "." not in email:
            self.email_error_label.configure(text="Enter a valid email address.")
            valid = False

        # Validate new password
        if not new_password or not is_password_strong(new_password):
            self.new_password_error_label.configure(
                text="Password must meet all requirements."
            )
            valid = False

        # Validate password match
        if new_password != confirm_password:
            self.confirm_password_error_label.configure(text="Passwords do not match.")
            valid = False

        if valid:
            success, message = reset_password_logic(email, new_password)
            if success:
                CTkMessagebox(
                    title="Password Reset", 
                    message="Your password has been reset successfully.", 
                    icon="check",
                    option_1="OK"
                )
                self.create_login_view()  # Redirect to login view on success
            else:
                self.email_error_label.configure(text=message)

# If module is run directly
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x600")
    app.title("Food Ordering System - Login")
    login_window = LoginWindow(app)
    login_window.pack(expand=True, fill="both")
    app.mainloop()
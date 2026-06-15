import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime, timedelta
from custom.navigation_frame_admin import NavigationFrameAdmin
from utils import connect_to_database, execute_query
from CTkMessagebox import CTkMessagebox
import bcrypt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class AdminDashboard(ctk.CTkFrame):
    """Dashboard for administrators to manage the entire food ordering system."""
    def __init__(self, master, user_id=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store user information
        self.master = master
        self.user_id = user_id
        self.admin_data = self.get_admin_data()
        
        # Configure this frame
        self.configure(fg_color="#f5f5f5")
        
        # Create main content container (all screens will be placed here)
        self.content_container = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)
        
        # Create and place navigation at bottom
        self.navigation_frame = NavigationFrameAdmin(self, user_id=self.user_id)
        self.navigation_frame.pack(side="bottom", fill="x")
        
        # Initialize frames for different screens
        self.home_frame = HomeFrame(self.content_container, self)
        self.users_frame = UsersFrame(self.content_container, self)
        self.restaurants_frame = RestaurantsFrame(self.content_container, self)
        self.orders_frame = OrdersFrame(self.content_container, self)
        self.settings_frame = SettingsFrame(self.content_container, self)
        self.reports_frame = ReportsFrame(self.content_container, self)
        
        # Show default frame (home)
        self.show_frame("home")
        
    def get_admin_data(self):
        """Fetch admin data from database."""
        if not self.user_id:
            return {"FirstName": "Admin", "LastName": "User"}
        
        query = "SELECT * FROM User WHERE UserID = %s AND Role = 'admin'"
        result = execute_query(query, (self.user_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return {"FirstName": "Admin", "LastName": "User"}
    
    def show_frame(self, frame_name, **kwargs):
        """Show selected frame and hide others."""
        # Hide all frames
        for frame in [self.home_frame, self.users_frame, self.restaurants_frame, 
                     self.orders_frame, self.settings_frame, self.reports_frame]:
            frame.pack_forget()
        
        # Show selected frame
        if frame_name == "home":
            self.home_frame.pack(fill="both", expand=True)
        elif frame_name == "users":
            self.users_frame.refresh_users()
            self.users_frame.pack(fill="both", expand=True)
        elif frame_name == "restaurants":
            self.restaurants_frame.refresh_restaurants()
            self.restaurants_frame.pack(fill="both", expand=True)
        elif frame_name == "orders":
            self.orders_frame.refresh_orders()
            self.orders_frame.pack(fill="both", expand=True)
        elif frame_name == "settings":
            self.settings_frame.pack(fill="both", expand=True)
        elif frame_name == "reports":
            self.reports_frame.refresh_data()
            self.reports_frame.pack(fill="both", expand=True)
    
    def sign_out(self):
        """Sign out and return to login screen."""
        confirm = CTkMessagebox(
            title="Sign Out",
            message="Are you sure you want to sign out?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        if confirm.get() == "Yes":
            self.master.current_user = None
            self.master.user_role = None
            self.master.show_login_window()

class HomeFrame(ctk.CTkFrame):
    """Home screen for admin dashboard with system overview."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title section
        admin_name = f"{controller.admin_data.get('FirstName', 'Admin')} {controller.admin_data.get('LastName', 'User')}"
        self.title_label = ctk.CTkLabel(
            self, 
            text=f"Welcome, {admin_name}",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Quick stats frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.stats_frame.pack(fill="x", padx=15, pady=10)
        
        # Define stats
        stats = [
            ("Total Users", self.get_total_users()),
            ("Total Restaurants", self.get_total_restaurants()),
            ("Total Orders", self.get_total_orders()),
            ("Total Revenue", f"${self.get_total_revenue():.2f}")
        ]
        
        # Display stats
        for stat, value in stats:
            stat_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10, pady=15)
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=("Arial", 18, "bold"),
                text_color="#333333"
            )
            value_label.pack()
            
            label = ctk.CTkLabel(
                stat_frame,
                text=stat,
                font=("Arial", 12),
                text_color="#666666"
            )
            label.pack()
        
        # Quick actions section
        self.actions_label = ctk.CTkLabel(
            self,
            text="Quick Actions",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.actions_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Actions frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.actions_frame.pack(fill="x", padx=15, pady=10)
        
        # Define actions
        actions = [
            ("Add User", self.add_user),
            ("Add Restaurant", self.add_restaurant),
            ("View Orders", lambda: self.controller.show_frame("orders")),
            ("Generate Reports", lambda: self.controller.show_frame("reports"))
        ]
        
        # Create action buttons
        for action_text, command in actions:
            action_button = ctk.CTkButton(
                self.actions_frame,
                text=action_text,
                command=command,
                fg_color="#2196F3",
                hover_color="#1976D2",
                corner_radius=10,
                font=("Arial", 14),
                height=40
            )
            action_button.pack(fill="x", padx=10, pady=10)
    
    def get_total_users(self):
        """Get total number of users."""
        query = "SELECT COUNT(*) as total FROM User"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_restaurants(self):
        """Get total number of restaurants."""
        query = "SELECT COUNT(*) as total FROM Restaurant"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_orders(self):
        """Get total number of orders."""
        query = "SELECT COUNT(*) as total FROM `Order`"
        result = execute_query(query, fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_revenue(self):
        """Get total revenue from all orders."""
        query = "SELECT SUM(TotalAmount) as revenue FROM `Order`"
        result = execute_query(query, fetch=True)
        return result[0]["revenue"] if result and result[0]["revenue"] else 0.0
    
    def add_user(self):
        """Open add user dialog."""
        self.controller.show_frame("users")
    
    def add_restaurant(self):
        """Open add restaurant dialog."""
        self.controller.show_frame("restaurants")

class UsersFrame(ctk.CTkFrame):
    """Users management screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="User Management",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Add user button
        self.add_user_button = ctk.CTkButton(
            self,
            text="Add New User",
            command=self.open_add_user_dialog,
            fg_color="#2196F3",
            hover_color="#1976D2",
            corner_radius=10,
            font=("Arial", 14),
            height=40,
            width=250
        )
        self.add_user_button.pack(pady=(0, 15))
        
        # Users container
        self.users_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.users_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Refresh users
        self.refresh_users()
    
    def refresh_users(self):
        """Refresh and display users."""
        # Clear existing items
        for widget in self.users_container.winfo_children():
            widget.destroy()
        
        # Get users
        users = self.get_users()
        
        if not users:
            # No users
            no_users_label = ctk.CTkLabel(
                self.users_container,
                text="No users found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_users_label.pack(pady=50)
            return
        
        # Display users
        for user in users:
            self.create_user_card(user)
    
    def get_users(self):
        """Get all users from the database."""
        query = """
            SELECT UserID, FirstName, LastName, Email, Role, 
                   DATE_FORMAT(DATE(NOW()), '%Y-%m-%d') as JoinDate 
            FROM User
            ORDER BY UserID
        """
        return execute_query(query, fetch=True) or []
    
    def create_user_card(self, user):
        """Create a card for a user."""
        card = ctk.CTkFrame(self.users_container, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=5, ipady=10)
        
        # User details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Name
        name_label = ctk.CTkLabel(
            details_frame,
            text=f"{user['FirstName']} {user['LastName']}",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        name_label.pack(anchor="w")
        
        # Email
        email_label = ctk.CTkLabel(
            details_frame,
            text=user['Email'],
            font=("Arial", 12),
            text_color="#666666"
        )
        email_label.pack(anchor="w")
        
        # Role and Join Date
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        role_label = ctk.CTkLabel(
            info_frame,
            text=f"Role: {user['Role']}",
            font=("Arial", 12),
            text_color="#4CAF50"
        )
        role_label.pack(side="left")
        
        join_label = ctk.CTkLabel(
            info_frame,
            text=f"Joined: {user.get('JoinDate', 'N/A')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        join_label.pack(side="right")
        
        # Actions frame
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=100,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda u=user: self.edit_user(u)
        )
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=100,
            fg_color="#F44336",
            hover_color="#D32F2F",
            command=lambda u=user: self.delete_user(u)
        )
        delete_btn.pack(side="right", padx=5)
    
    def open_add_user_dialog(self):
        """Open dialog to add a new user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # First Name
        first_name_label = ctk.CTkLabel(dialog, text="First Name", anchor="w")
        first_name_label.pack(padx=20, pady=(20, 5), anchor="w")
        first_name_entry = ctk.CTkEntry(dialog, width=350)
        first_name_entry.pack(padx=20, pady=5)
        
        # Last Name
        last_name_label = ctk.CTkLabel(dialog, text="Last Name", anchor="w")
        last_name_label.pack(padx=20, pady=(10, 5), anchor="w")
        last_name_entry = ctk.CTkEntry(dialog, width=350)
        last_name_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.pack(padx=20, pady=5)
        
        # Password
        password_label = ctk.CTkLabel(dialog, text="Password", anchor="w")
        password_label.pack(padx=20, pady=(10, 5), anchor="w")
        password_entry = ctk.CTkEntry(dialog, width=350, show="*")
        password_entry.pack(padx=20, pady=5)
        
        # Role
        role_label = ctk.CTkLabel(dialog, text="User Role", anchor="w")
        role_label.pack(padx=20, pady=(10, 5), anchor="w")
        role_var = ctk.StringVar(value="customer")
        role_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=["customer", "restaurant", "admin"],
            variable=role_var,
            width=350
        )
        role_dropdown.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Create User", 
            command=lambda: self.save_new_user(
                first_name_entry.get(), 
                last_name_entry.get(), 
                email_entry.get(), 
                password_entry.get(), 
                role_var.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_new_user(self, first_name, last_name, email, password, role, dialog):
        """Save a new user to the database."""
        # Basic validation
        if not first_name or not last_name or not email or not password:
            CTkMessagebox(
                title="Validation Error",
                message="All fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid email address.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Password strength check
        from custom.auth import is_password_strong
        if not is_password_strong(password):
            CTkMessagebox(
                title="Password Requirements",
                message="Password must be at least 8 characters with 1 uppercase letter and 1 special character.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if email already exists
        check_query = "SELECT UserID FROM User WHERE Email = %s"
        existing_user = execute_query(check_query, (email,), fetch=True)
        
        if existing_user:
            CTkMessagebox(
                title="Registration Error",
                message="A user with this email already exists.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Insert new user
        query = """
            INSERT INTO User (FirstName, LastName, Email, Password, Role)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, hashed_password, role))
            user_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            # If role is 'restaurant', create a restaurant entry for this user
            if role == 'restaurant':
                self.create_restaurant_for_user(user_id, f"{first_name}'s Restaurant")
            
            # Close dialog
            dialog.destroy()
            
            # Refresh users list
            self.refresh_users()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="User created successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to create user: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def create_restaurant_for_user(self, user_id, restaurant_name):
        """Create a restaurant entry for a restaurant owner user."""
        query = """
            INSERT INTO Restaurant (Name, Cuisine, Contact, Location)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (restaurant_name, "Mixed", "Not Set", "Not Set"))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error creating restaurant for user: {e}")
    
    def edit_user(self, user):
        """Open dialog to edit an existing user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit User")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # First Name
        first_name_label = ctk.CTkLabel(dialog, text="First Name", anchor="w")
        first_name_label.pack(padx=20, pady=(20, 5), anchor="w")
        first_name_entry = ctk.CTkEntry(dialog, width=350)
        first_name_entry.insert(0, user['FirstName'])
        first_name_entry.pack(padx=20, pady=5)
        
        # Last Name
        last_name_label = ctk.CTkLabel(dialog, text="Last Name", anchor="w")
        last_name_label.pack(padx=20, pady=(10, 5), anchor="w")
        last_name_entry = ctk.CTkEntry(dialog, width=350)
        last_name_entry.insert(0, user['LastName'])
        last_name_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.insert(0, user['Email'])
        email_entry.pack(padx=20, pady=5)
        
        # Role
        role_label = ctk.CTkLabel(dialog, text="User Role", anchor="w")
        role_label.pack(padx=20, pady=(10, 5), anchor="w")
        role_var = ctk.StringVar(value=user['Role'])
        role_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=["customer", "restaurant", "admin"],
            variable=role_var,
            width=350
        )
        role_dropdown.pack(padx=20, pady=5)
        
        # Password Reset Option
        reset_password_btn = ctk.CTkButton(
            dialog,
            text="Reset Password",
            command=lambda: self.reset_user_password(user['UserID']),
            width=350,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        reset_password_btn.pack(padx=20, pady=(10, 5))
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Update User", 
            command=lambda: self.save_user_changes(
                user['UserID'],
                first_name_entry.get(), 
                last_name_entry.get(), 
                email_entry.get(), 
                role_var.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_user_changes(self, user_id, first_name, last_name, email, role, dialog):
        """Save changes to an existing user."""
        # Basic validation
        if not first_name or not last_name or not email:
            CTkMessagebox(
                title="Validation Error",
                message="All fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid email address.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Get current user data
        query = "SELECT Role FROM User WHERE UserID = %s"
        current_user = execute_query(query, (user_id,), fetch=True)
        
        if not current_user:
            CTkMessagebox(
                title="Error",
                message="User not found.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        current_role = current_user[0]['Role']
        
        # Update user query
        query = """
            UPDATE User 
            SET FirstName = %s, LastName = %s, Email = %s, Role = %s
            WHERE UserID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, role, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # If changing role to 'restaurant' from something else, create a restaurant
            if role == 'restaurant' and current_role != 'restaurant':
                self.create_restaurant_for_user(user_id, f"{first_name}'s Restaurant")
            
            # Close dialog
            dialog.destroy()
            
            # Refresh users list
            self.refresh_users()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="User updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update user: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def reset_user_password(self, user_id):
        """Reset a user's password."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Password")
        dialog.geometry("400x300")
        dialog.grab_set()  # Make dialog modal
        
        # New Password
        new_pass_label = ctk.CTkLabel(dialog, text="New Password", anchor="w")
        new_pass_label.pack(padx=20, pady=(20, 5), anchor="w")
        new_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        new_pass_entry.pack(padx=20, pady=5)
        
        # Confirm New Password
        confirm_pass_label = ctk.CTkLabel(dialog, text="Confirm New Password", anchor="w")
        confirm_pass_label.pack(padx=20, pady=(10, 5), anchor="w")
        confirm_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        confirm_pass_entry.pack(padx=20, pady=5)
        
        # Password requirements hint
        hint_label = ctk.CTkLabel(
            dialog,
            text="Password must be at least 8 characters\nwith 1 uppercase letter and 1 special character",
            font=("Arial", 10),
            text_color="#666666"
        )
        hint_label.pack(pady=(10, 5))
        
        # Reset button
        reset_btn = ctk.CTkButton(
            dialog, 
            text="Reset Password", 
            command=lambda: self.save_reset_password(
                user_id,
                new_pass_entry.get(), 
                confirm_pass_entry.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        reset_btn.pack(padx=20, pady=(20, 10))
    
    def save_reset_password(self, user_id, new_password, confirm_password, dialog):
        """Save the reset password."""
        # Validate passwords match
        if new_password != confirm_password:
            CTkMessagebox(
                title="Validation Error",
                message="Passwords do not match.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Check password strength
        from custom.auth import is_password_strong
        if not is_password_strong(new_password):
            CTkMessagebox(
                title="Password Requirements",
                message="Password must be at least 8 characters with 1 uppercase letter and 1 special character.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password query
        query = "UPDATE User SET Password = %s WHERE UserID = %s"
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (hashed_password, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Password reset successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to reset password: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def delete_user(self, user):
        """Delete a user from the database."""
        # Confirm deletion
        confirm = CTkMessagebox(
            title="Delete User",
            message=f"Are you sure you want to delete user {user['FirstName']} {user['LastName']}?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Delete user query
            query = "DELETE FROM User WHERE UserID = %s"
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(query, (user['UserID'],))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh users list
                self.refresh_users()
                
                # Show success message
                CTkMessagebox(
                    title="Success",
                    message="User deleted successfully!",
                    icon="check",
                    option_1="OK"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Database Error",
                    message=f"Failed to delete user: {e}",
                    icon="cancel",
                    option_1="OK"
                )

class RestaurantsFrame(ctk.CTkFrame):
    """Restaurants management screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Restaurant Management",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Add restaurant button
        self.add_restaurant_button = ctk.CTkButton(
            self,
            text="Add New Restaurant",
            command=self.open_add_restaurant_dialog,
            fg_color="#2196F3",
            hover_color="#1976D2",
            corner_radius=10,
            font=("Arial", 14),
            height=40,
            width=250
        )
        self.add_restaurant_button.pack(pady=(0, 15))
        
        # Restaurants container
        self.restaurants_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.restaurants_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Refresh restaurants
        self.refresh_restaurants()
    
    def refresh_restaurants(self):
        """Refresh and display restaurants."""
        # Clear existing items
        for widget in self.restaurants_container.winfo_children():
            widget.destroy()
        
        # Get restaurants
        restaurants = self.get_restaurants()
        
        if not restaurants:
            # No restaurants
            no_restaurants_label = ctk.CTkLabel(
                self.restaurants_container,
                text="No restaurants found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_restaurants_label.pack(pady=50)
            return
        
        # Display restaurants
        for restaurant in restaurants:
            self.create_restaurant_card(restaurant)
    
    def get_restaurants(self):
        """Get all restaurants from the database with owner information."""
        query = """
            SELECT r.*, u.FirstName, u.LastName, u.Email, u.UserID
            FROM Restaurant r
            LEFT JOIN User u ON u.Role = 'restaurant' AND (
                SELECT COUNT(*) FROM Restaurant r2 
                WHERE r2.RestaurantID < r.RestaurantID AND 
                EXISTS (SELECT 1 FROM User u2 WHERE u2.Role = 'restaurant' AND u2.UserID = u.UserID)
            ) = 0
            ORDER BY r.RestaurantID
        """
        return execute_query(query, fetch=True) or []
    
    def create_restaurant_card(self, restaurant):
        """Create a card for a restaurant."""
        card = ctk.CTkFrame(self.restaurants_container, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=5, ipady=10)
        
        # Restaurant details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Name
        name_label = ctk.CTkLabel(
            details_frame,
            text=restaurant['Name'],
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        name_label.pack(anchor="w")
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(
            details_frame,
            text=f"Cuisine: {restaurant.get('Cuisine', 'Not specified')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        cuisine_label.pack(anchor="w")
        
        # Owner information
        owner_text = "No owner assigned"
        if restaurant.get('FirstName') and restaurant.get('LastName'):
            owner_text = f"Owner: {restaurant['FirstName']} {restaurant['LastName']} ({restaurant['Email']})"
        
        owner_label = ctk.CTkLabel(
            details_frame,
            text=owner_text,
            font=("Arial", 12),
            text_color="#666666"
        )
        owner_label.pack(anchor="w")
        
        # Additional details
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        contact_label = ctk.CTkLabel(
            info_frame,
            text=f"Contact: {restaurant.get('Contact', 'Not provided')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        contact_label.pack(side="left")
        
        location_label = ctk.CTkLabel(
            info_frame,
            text=f"Location: {restaurant.get('Location', 'Not provided')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        location_label.pack(side="right")
        
        # Actions frame
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=100,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda r=restaurant: self.edit_restaurant(r)
        )
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=100,
            fg_color="#F44336",
            hover_color="#D32F2F",
            command=lambda r=restaurant: self.delete_restaurant(r)
        )
        delete_btn.pack(side="right", padx=5)
        
        # Assign owner button (only if no owner is assigned)
        if not restaurant.get('UserID'):
            assign_btn = ctk.CTkButton(
                card,
                text="Assign Restaurant Owner",
                width=card.winfo_width() - 20,
                fg_color="#FF9800",
                hover_color="#F57C00",
                command=lambda r=restaurant: self.assign_restaurant_owner(r)
            )
            assign_btn.pack(fill="x", padx=10, pady=5)
    
    def open_add_restaurant_dialog(self):
        """Open dialog to add a new restaurant."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Restaurant")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # Restaurant Name
        name_label = ctk.CTkLabel(dialog, text="Restaurant Name", anchor="w")
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.pack(padx=20, pady=5)
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(dialog, text="Cuisine", anchor="w")
        cuisine_label.pack(padx=20, pady=(10, 5), anchor="w")
        cuisine_entry = ctk.CTkEntry(dialog, width=350)
        cuisine_entry.pack(padx=20, pady=5)
        
        # Contact
        contact_label = ctk.CTkLabel(dialog, text="Contact", anchor="w")
        contact_label.pack(padx=20, pady=(10, 5), anchor="w")
        contact_entry = ctk.CTkEntry(dialog, width=350)
        contact_entry.pack(padx=20, pady=5)
        
        # Location
        location_label = ctk.CTkLabel(dialog, text="Location", anchor="w")
        location_label.pack(padx=20, pady=(10, 5), anchor="w")
        location_entry = ctk.CTkEntry(dialog, width=350)
        location_entry.pack(padx=20, pady=5)
        
        # Owner selection
        owner_label = ctk.CTkLabel(dialog, text="Restaurant Owner (Optional)", anchor="w")
        owner_label.pack(padx=20, pady=(10, 5), anchor="w")
        
        # Get restaurant owner users
        owners = self.get_restaurant_owner_users()
        owner_options = ["None"] + [f"{owner['FirstName']} {owner['LastName']} ({owner['Email']})" for owner in owners]
        owner_ids = [None] + [owner['UserID'] for owner in owners]
        
        owner_var = ctk.StringVar(value=owner_options[0])
        owner_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=owner_options,
            variable=owner_var,
            width=350
        )
        owner_dropdown.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Create Restaurant", 
            command=lambda: self.save_new_restaurant(
                name_entry.get(), 
                cuisine_entry.get(), 
                contact_entry.get(), 
                location_entry.get(),
                owner_ids[owner_options.index(owner_var.get())],
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def get_restaurant_owner_users(self):
        """Get users with 'restaurant' role that don't have a restaurant assigned."""
        query = """
            SELECT u.*
            FROM User u
            LEFT JOIN Restaurant r ON u.UserID = r.UserID
            WHERE u.Role = 'restaurant'
            ORDER BY u.FirstName, u.LastName
        """
        return execute_query(query, fetch=True) or []
    
    def save_new_restaurant(self, name, cuisine, contact, location, owner_id, dialog):
        """Save a new restaurant to the database."""
        # Basic validation
        if not name:
            CTkMessagebox(
                title="Validation Error",
                message="Restaurant Name is required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Insert new restaurant
        query = """
            INSERT INTO Restaurant (Name, Cuisine, Contact, Location)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (name, cuisine, contact, location))
            restaurant_id = cursor.lastrowid
            conn.commit()
            
            # If owner was selected, update the ownership
            if owner_id:
                assign_query = "UPDATE Restaurant SET UserID = %s WHERE RestaurantID = %s"
                cursor.execute(assign_query, (owner_id, restaurant_id))
                conn.commit()
            
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Refresh restaurants list
            self.refresh_restaurants()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Restaurant created successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to create restaurant: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def edit_restaurant(self, restaurant):
        """Open dialog to edit an existing restaurant."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Restaurant")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # Restaurant Name
        name_label = ctk.CTkLabel(dialog, text="Restaurant Name", anchor="w")
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.insert(0, restaurant['Name'])
        name_entry.pack(padx=20, pady=5)
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(dialog, text="Cuisine", anchor="w")
        cuisine_label.pack(padx=20, pady=(10, 5), anchor="w")
        cuisine_entry = ctk.CTkEntry(dialog, width=350)
        cuisine_entry.insert(0, restaurant.get('Cuisine', ''))
        cuisine_entry.pack(padx=20, pady=5)
        
        # Contact
        contact_label = ctk.CTkLabel(dialog, text="Contact", anchor="w")
        contact_label.pack(padx=20, pady=(10, 5), anchor="w")
        contact_entry = ctk.CTkEntry(dialog, width=350)
        contact_entry.insert(0, restaurant.get('Contact', ''))
        contact_entry.pack(padx=20, pady=5)
        
        # Location
        location_label = ctk.CTkLabel(dialog, text="Location", anchor="w")
        location_label.pack(padx=20, pady=(10, 5), anchor="w")
        location_entry = ctk.CTkEntry(dialog, width=350)
        location_entry.insert(0, restaurant.get('Location', ''))
        location_entry.pack(padx=20, pady=5)
        
        # Owner selection
        owner_label = ctk.CTkLabel(dialog, text="Restaurant Owner", anchor="w")
        owner_label.pack(padx=20, pady=(10, 5), anchor="w")
        
        # Get restaurant owner users
        owners = self.get_restaurant_owner_users()
        
        # Add current owner if exists
        current_owner_text = "None"
        if restaurant.get('FirstName') and restaurant.get('LastName'):
            current_owner_text = f"{restaurant['FirstName']} {restaurant['LastName']} ({restaurant['Email']})"
            # Add to list if not already present
            if not any(owner['UserID'] == restaurant.get('UserID') for owner in owners):
                owners.append({
                    'UserID': restaurant.get('UserID'),
                    'FirstName': restaurant.get('FirstName'),
                    'LastName': restaurant.get('LastName'),
                    'Email': restaurant.get('Email')
                })
        
        owner_options = ["None"] + [f"{owner['FirstName']} {owner['LastName']} ({owner['Email']})" for owner in owners]
        owner_ids = [None] + [owner['UserID'] for owner in owners]
        
        # Set current selection
        owner_var = ctk.StringVar(value=current_owner_text if current_owner_text in owner_options else owner_options[0])
        owner_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=owner_options,
            variable=owner_var,
            width=350
        )
        owner_dropdown.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Update Restaurant", 
            command=lambda: self.save_restaurant_changes(
                restaurant['RestaurantID'],
                name_entry.get(), 
                cuisine_entry.get(), 
                contact_entry.get(), 
                location_entry.get(),
                owner_ids[owner_options.index(owner_var.get())] if owner_var.get() in owner_options else None,
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_restaurant_changes(self, restaurant_id, name, cuisine, contact, location, owner_id, dialog):
        """Save changes to an existing restaurant."""
        # Basic validation
        if not name:
            CTkMessagebox(
                title="Validation Error",
                message="Restaurant Name is required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Update restaurant query
        query = """
            UPDATE Restaurant 
            SET Name = %s, Cuisine = %s, Contact = %s, Location = %s, UserID = %s
            WHERE RestaurantID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (name, cuisine, contact, location, owner_id, restaurant_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Refresh restaurants list
            self.refresh_restaurants()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Restaurant updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update restaurant: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def assign_restaurant_owner(self, restaurant):
        """Open dialog to assign an owner to a restaurant."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Assign Restaurant Owner")
        dialog.geometry("400x300")
        dialog.grab_set()  # Make dialog modal
        
        # Restaurant info
        info_label = ctk.CTkLabel(
            dialog,
            text=f"Assign owner for: {restaurant['Name']}",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        info_label.pack(padx=20, pady=(20, 15))
        
        # Get restaurant owner users
        owners = self.get_restaurant_owner_users()
        
        if not owners:
            # No available restaurant owners
            no_owners = ctk.CTkLabel(
                dialog,
                text="No available restaurant owners.\nCreate a user with the 'restaurant' role first.",
                font=("Arial", 12),
                text_color="#666666"
            )
            no_owners.pack(pady=20)
            
            # Close button
            close_btn = ctk.CTkButton(
                dialog,
                text="Close",
                command=dialog.destroy,
                width=350,
                fg_color="#F44336",
                hover_color="#D32F2F"
            )
            close_btn.pack(padx=20, pady=10)
            return
        
        # Owner selection
        owner_label = ctk.CTkLabel(dialog, text="Select Owner", anchor="w")
        owner_label.pack(padx=20, pady=(10, 5), anchor="w")
        
        owner_options = [f"{owner['FirstName']} {owner['LastName']} ({owner['Email']})" for owner in owners]
        owner_ids = [owner['UserID'] for owner in owners]
        
        owner_var = ctk.StringVar(value=owner_options[0] if owner_options else "")
        owner_dropdown = ctk.CTkOptionMenu(
            dialog, 
            values=owner_options,
            variable=owner_var,
            width=350
        )
        owner_dropdown.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Assign Owner", 
            command=lambda: self.save_owner_assignment(
                restaurant['RestaurantID'],
                owner_ids[owner_options.index(owner_var.get())] if owner_var.get() in owner_options else None,
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_owner_assignment(self, restaurant_id, owner_id, dialog):
        """Save owner assignment to a restaurant."""
        if not owner_id:
            CTkMessagebox(
                title="Selection Error",
                message="Please select an owner.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Update restaurant query
        query = "UPDATE Restaurant SET UserID = %s WHERE RestaurantID = %s"
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (owner_id, restaurant_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Refresh restaurants list
            self.refresh_restaurants()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Restaurant owner assigned successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to assign restaurant owner: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def delete_restaurant(self, restaurant):
        """Delete a restaurant from the database."""
        # Confirm deletion
        confirm = CTkMessagebox(
            title="Delete Restaurant",
            message=f"Are you sure you want to delete restaurant '{restaurant['Name']}'?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Delete restaurant query
            query = "DELETE FROM Restaurant WHERE RestaurantID = %s"
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(query, (restaurant['RestaurantID'],))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh restaurants list
                self.refresh_restaurants()
                
                # Show success message
                CTkMessagebox(
                    title="Success",
                    message="Restaurant deleted successfully!",
                    icon="check",
                    option_1="OK"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Database Error",
                    message=f"Failed to delete restaurant: {e}",
                    icon="cancel",
                    option_1="OK"
                )

class OrdersFrame(ctk.CTkFrame):
    """Orders management screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Order Management",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Search and filter section
        self.filter_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.filter_frame.pack(fill="x", padx=15, pady=10)
        
        # Restaurant filter
        self.filter_restaurant_label = ctk.CTkLabel(
            self.filter_frame,
            text="Filter by Restaurant:",
            font=("Arial", 12),
            text_color="#333333"
        )
        self.filter_restaurant_label.pack(side="left", padx=(10, 5), pady=10)
        
        # Get restaurants for filter
        restaurants = self.get_restaurants_for_filter()
        restaurant_options = ["All Restaurants"] + [r['Name'] for r in restaurants]
        restaurant_ids = [None] + [r['RestaurantID'] for r in restaurants]
        
        self.filter_restaurant_var = ctk.StringVar(value=restaurant_options[0])
        self.filter_restaurant_dropdown = ctk.CTkOptionMenu(
            self.filter_frame,
            values=restaurant_options,
            variable=self.filter_restaurant_var,
            command=lambda _: self.refresh_orders(),
            width=200
        )
        self.filter_restaurant_dropdown.pack(side="left", padx=5, pady=10)
        
        # Status filter
        self.filter_status_label = ctk.CTkLabel(
            self.filter_frame,
            text="Status:",
            font=("Arial", 12),
            text_color="#333333"
        )
        self.filter_status_label.pack(side="left", padx=(20, 5), pady=10)
        
        status_options = ["All", "pending", "preparing", "shipped", "delivered"]
        self.filter_status_var = ctk.StringVar(value=status_options[0])
        self.filter_status_dropdown = ctk.CTkOptionMenu(
            self.filter_frame,
            values=status_options,
            variable=self.filter_status_var,
            command=lambda _: self.refresh_orders(),
            width=150
        )
        self.filter_status_dropdown.pack(side="left", padx=5, pady=10)
        
        # Orders container
        self.orders_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.orders_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Refresh orders
        self.refresh_orders()
    
    def get_restaurants_for_filter(self):
        """Get restaurants for the filter dropdown."""
        query = "SELECT RestaurantID, Name FROM Restaurant ORDER BY Name"
        return execute_query(query, fetch=True) or []
    
    def refresh_orders(self):
        """Refresh and display orders."""
        # Clear existing items
        for widget in self.orders_container.winfo_children():
            widget.destroy()
        
        # Get selected filters
        restaurant_filter = self.filter_restaurant_var.get()
        status_filter = self.filter_status_var.get()
        
        # Get restaurants for mapping
        restaurants = self.get_restaurants_for_filter()
        restaurant_map = {r['Name']: r['RestaurantID'] for r in restaurants}
        
        # Build query with filters
        restaurant_id = restaurant_map.get(restaurant_filter) if restaurant_filter != "All Restaurants" else None
        order_status = status_filter if status_filter != "All" else None
        
        # Get orders
        orders = self.get_orders(restaurant_id, order_status)
        
        if not orders:
            # No orders
            no_orders_label = ctk.CTkLabel(
                self.orders_container,
                text="No orders found.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_orders_label.pack(pady=50)
            return
        
        # Display orders
        for order in orders:
            self.create_order_card(order)
    
    def get_orders(self, restaurant_id=None, status=None):
        """Get orders from the database with optional filters."""
        query_params = []
        
        base_query = """
            SELECT o.*, r.Name as RestaurantName, u.FirstName, u.LastName, u.Email
            FROM `Order` o
            JOIN Restaurant r ON o.RestaurantID = r.RestaurantID
            JOIN User u ON o.UserID = u.UserID
        """
        
        # Add filters
        where_clauses = []
        if restaurant_id:
            where_clauses.append("o.RestaurantID = %s")
            query_params.append(restaurant_id)
        
        if status:
            where_clauses.append("o.OrderStatus = %s")
            query_params.append(status)
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY o.OrderDate DESC"
        
        orders = execute_query(base_query, tuple(query_params), fetch=True) or []
        
        # Get order items for each order
        for order in orders:
            items_query = """
                SELECT oi.*, m.ItemName 
                FROM OrderItem oi
                JOIN Menu m ON oi.MenuID = m.MenuID
                WHERE oi.OrderID = %s
            """
            order['Items'] = execute_query(items_query, (order['OrderID'],), fetch=True) or []
        
        return orders
    
    def create_order_card(self, order):
        """Create a card for an order."""
        card = ctk.CTkFrame(self.orders_container, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=5, ipady=10)
        
        # Order details header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Order ID and Date
        order_id_label = ctk.CTkLabel(
            header_frame,
            text=f"Order #{order['OrderID']}",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        order_id_label.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=str(order['OrderDate']),
            font=("Arial", 12),
            text_color="#666666"
        )
        date_label.pack(side="right")
        
        # Restaurant and customer info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        restaurant_label = ctk.CTkLabel(
            info_frame,
            text=f"Restaurant: {order['RestaurantName']}",
            font=("Arial", 12, "bold"),
            text_color="#333333"
        )
        restaurant_label.pack(side="left")
        
        customer_label = ctk.CTkLabel(
            info_frame,
            text=f"Customer: {order['FirstName']} {order['LastName']}",
            font=("Arial", 12),
            text_color="#666666"
        )
        customer_label.pack(side="right")
        
        # Order items
        items_label = ctk.CTkLabel(
            card,
            text="Items:",
            font=("Arial", 12, "bold"),
            text_color="#333333"
        )
        items_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Create frame for order items
        items_frame = ctk.CTkFrame(card, fg_color="#f9f9f9", corner_radius=5)
        items_frame.pack(fill="x", padx=10, pady=5)
        
        # Display order items
        for item in order['Items']:
            item_frame = ctk.CTkFrame(items_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=2)
            
            item_name = ctk.CTkLabel(
                item_frame,
                text=item['ItemName'],
                font=("Arial", 12),
                text_color="#333333"
            )
            item_name.pack(side="left")
            
            item_details = ctk.CTkLabel(
                item_frame,
                text=f"Qty: {item['Quantity']} - ${item['Subtotal']:.2f}",
                font=("Arial", 12),
                text_color="#666666"
            )
            item_details.pack(side="right")
        
        # Total and status
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=10, pady=5)
        
        total_label = ctk.CTkLabel(
            bottom_frame,
            text=f"Total: ${order['TotalAmount']:.2f}",
            font=("Arial", 14, "bold"),
            text_color="#4CAF50"
        )
        total_label.pack(side="left")
        
        status_label = ctk.CTkLabel(
            bottom_frame,
            text=f"Status: {order['OrderStatus']}",
            font=("Arial", 12),
            text_color={
                'pending': '#FFA000',
                'preparing': '#2196F3',
                'shipped': '#9C27B0',
                'delivered': '#4CAF50'
            }.get(order['OrderStatus'], '#666666')
        )
        status_label.pack(side="right")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # Update status dropdown
        status_options = ["pending", "preparing", "shipped", "delivered"]
        status_var = ctk.StringVar(value=order['OrderStatus'])
        
        status_dropdown = ctk.CTkOptionMenu(
            actions_frame,
            values=status_options,
            variable=status_var,
            width=150
        )
        status_dropdown.pack(side="left")
        
        # Update button
        update_btn = ctk.CTkButton(
            actions_frame,
            text="Update Status",
            command=lambda o_id=order['OrderID'], status_var=status_var: self.update_order_status(o_id, status_var.get()),
            fg_color="#2196F3",
            hover_color="#1976D2",
            width=150
        )
        update_btn.pack(side="left", padx=10)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete Order",
            command=lambda o_id=order['OrderID']: self.delete_order(o_id),
            fg_color="#F44336",
            hover_color="#D32F2F",
            width=150
        )
        delete_btn.pack(side="right")
    
    def update_order_status(self, order_id, new_status):
        """Update the status of an order."""
        query = "UPDATE `Order` SET OrderStatus = %s WHERE OrderID = %s"
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (new_status, order_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Refresh orders
            self.refresh_orders()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message=f"Order status updated to '{new_status}'!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update order status: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def delete_order(self, order_id):
        """Delete an order from the database."""
        # Confirm deletion
        confirm = CTkMessagebox(
            title="Delete Order",
            message=f"Are you sure you want to delete Order #{order_id}?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Delete order
            query = "DELETE FROM `Order` WHERE OrderID = %s"
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(query, (order_id,))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh orders
                self.refresh_orders()
                
                # Show success message
                CTkMessagebox(
                    title="Success",
                    message="Order deleted successfully!",
                    icon="check",
                    option_1="OK"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Database Error",
                    message=f"Failed to delete order: {e}",
                    icon="cancel",
                    option_1="OK"
                )

class SettingsFrame(ctk.CTkFrame):
    """Settings screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Admin Settings",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Profile settings container
        self.profile_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.profile_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Admin info
        admin_data = self.controller.admin_data
        
        # Profile fields
        fields = [
            ("Name", f"{admin_data.get('FirstName', 'Admin')} {admin_data.get('LastName', 'User')}"),
            ("Email", admin_data.get('Email', 'admin@example.com')),
            ("Role", admin_data.get('Role', 'admin')),
        ]
        
        for field, value in fields:
            field_frame = ctk.CTkFrame(self.profile_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=15, pady=10)
            
            field_label = ctk.CTkLabel(
                field_frame,
                text=field,
                font=("Arial", 14),
                text_color="#555555",
                anchor="w"
            )
            field_label.pack(side="left")
            
            value_label = ctk.CTkLabel(
                field_frame,
                text=value,
                font=("Arial", 14),
                text_color="#333333",
                anchor="e"
            )
            value_label.pack(side="right")
        
        # Edit Profile Button
        self.edit_button = ctk.CTkButton(
            self,
            text="Edit Profile",
            command=self.edit_profile,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            corner_radius=5,
            font=("Arial", 16),
            height=40,
            width=350
        )
        self.edit_button.pack(pady=(0, 20))
        
        # System Settings Section
        self.system_label = ctk.CTkLabel(
            self,
            text="System Settings",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.system_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # System settings container
        self.system_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.system_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # System settings options
        settings = [
            ("Database Backup", False),
            ("Email Notifications", True),
            ("Maintenance Mode", False)
        ]
        
        for setting, value in settings:
            setting_frame = ctk.CTkFrame(self.system_container, fg_color="transparent")
            setting_frame.pack(fill="x", padx=15, pady=10)
            
            setting_label = ctk.CTkLabel(
                setting_frame,
                text=setting,
                font=("Arial", 14),
                text_color="#333333",
                anchor="w"
            )
            setting_label.pack(side="left")
            
            switch_var = ctk.BooleanVar(value=value)
            setting_switch = ctk.CTkSwitch(
                setting_frame,
                text="",
                variable=switch_var,
                command=lambda s=setting: self.toggle_setting(s),
                switch_width=46,
                switch_height=24,
                fg_color="#CCCCCC",
                progress_color="#4CAF50",
                button_color="#FFFFFF",
                button_hover_color="#EEEEEE"
            )
            setting_switch.pack(side="right")
        
        # Account Options Section
        self.account_label = ctk.CTkLabel(
            self,
            text="Account Options",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.account_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Account options container
        self.account_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.account_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Account options
        account_options = [
            ("Change Password", self.change_password),
            ("Sign Out", self.sign_out)
        ]
        
        for option_text, command in account_options:
            option_button = ctk.CTkButton(
                self.account_container,
                text=option_text,
                command=command,
                fg_color="transparent",
                hover_color="#f0f0f0",
                text_color="#333333",
                anchor="w",
                font=("Arial", 14),
                height=40
            )
            option_button.pack(fill="x", padx=5, pady=2)
    
    def toggle_setting(self, setting):
        """Handle toggling a system setting."""
        CTkMessagebox(
            title="Setting Changed",
            message=f"The '{setting}' setting will be available in a future update.",
            icon="info",
            option_1="OK"
        )
    
    def edit_profile(self):
        """Open dialog to edit admin profile."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Profile")
        dialog.geometry("400x400")
        dialog.grab_set()  # Make dialog modal
        
        admin_data = self.controller.admin_data
        
        # First Name
        first_name_label = ctk.CTkLabel(dialog, text="First Name", anchor="w")
        first_name_label.pack(padx=20, pady=(20, 5), anchor="w")
        first_name_entry = ctk.CTkEntry(dialog, width=350)
        first_name_entry.insert(0, admin_data.get('FirstName', ''))
        first_name_entry.pack(padx=20, pady=5)
        
        # Last Name
        last_name_label = ctk.CTkLabel(dialog, text="Last Name", anchor="w")
        last_name_label.pack(padx=20, pady=(10, 5), anchor="w")
        last_name_entry = ctk.CTkEntry(dialog, width=350)
        last_name_entry.insert(0, admin_data.get('LastName', ''))
        last_name_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.insert(0, admin_data.get('Email', ''))
        email_entry.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Save Changes", 
            command=lambda: self.save_profile_changes(
                first_name_entry.get(), 
                last_name_entry.get(), 
                email_entry.get(), 
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_profile_changes(self, first_name, last_name, email, dialog):
        """Save changes to admin profile."""
        # Basic validation
        if not first_name or not last_name or not email:
            CTkMessagebox(
                title="Validation Error",
                message="All fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid email address.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Update user query
        query = """
            UPDATE User 
            SET FirstName = %s, LastName = %s, Email = %s
            WHERE UserID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, self.controller.user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update local admin data
            self.controller.admin_data.update({
                'FirstName': first_name,
                'LastName': last_name,
                'Email': email
            })
            
            # Close dialog
            dialog.destroy()
            
            # Refresh the view
            self.pack_forget()
            self.pack(fill="both", expand=True)
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Profile updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update profile: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def change_password(self):
        """Open change password dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x400")
        dialog.grab_set()  # Make dialog modal
        
        # Current Password
        current_pass_label = ctk.CTkLabel(dialog, text="Current Password", anchor="w")
        current_pass_label.pack(padx=20, pady=(20, 5), anchor="w")
        current_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        current_pass_entry.pack(padx=20, pady=5)
        
        # New Password
        new_pass_label = ctk.CTkLabel(dialog, text="New Password", anchor="w")
        new_pass_label.pack(padx=20, pady=(10, 5), anchor="w")
        new_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        new_pass_entry.pack(padx=20, pady=5)
        
        # Confirm New Password
        confirm_pass_label = ctk.CTkLabel(dialog, text="Confirm New Password", anchor="w")
        confirm_pass_label.pack(padx=20, pady=(10, 5), anchor="w")
        confirm_pass_entry = ctk.CTkEntry(dialog, width=350, show="*")
        confirm_pass_entry.pack(padx=20, pady=5)
        
        # Password requirements hint
        hint_label = ctk.CTkLabel(
            dialog,
            text="Password must be at least 8 characters\nwith 1 uppercase letter and 1 special character",
            font=("Arial", 10),
            text_color="#666666"
        )
        hint_label.pack(pady=(10, 5))
        
        # Change Password Button
        change_btn = ctk.CTkButton(
            dialog, 
            text="Change Password", 
            command=lambda: self.update_password(
                current_pass_entry.get(), 
                new_pass_entry.get(), 
                confirm_pass_entry.get(),
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        change_btn.pack(padx=20, pady=(20, 10))
    
    def update_password(self, current_password, new_password, confirm_password, dialog):
        """Update admin password."""
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            CTkMessagebox(
                title="Validation Error",
                message="All password fields are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Check if new passwords match
        if new_password != confirm_password:
            CTkMessagebox(
                title="Validation Error",
                message="New passwords do not match.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Validate password strength
        from custom.auth import is_password_strong
        if not is_password_strong(new_password):
            CTkMessagebox(
                title="Password Requirements",
                message="Password must be at least 8 characters with 1 uppercase letter and 1 special character.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Verify current password
        import bcrypt
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get user's current password
            query = "SELECT Password FROM User WHERE UserID = %s"
            cursor.execute(query, (self.controller.user_id,))
            user = cursor.fetchone()
            
            if not user or not bcrypt.checkpw(current_password.encode('utf-8'), user['Password'].encode('utf-8')):
                cursor.close()
                conn.close()
                CTkMessagebox(
                    title="Authentication Error",
                    message="Current password is incorrect.",
                    icon="cancel",
                    option_1="OK"
                )
                return
            
            # Hash new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update password
            update_query = "UPDATE User SET Password = %s WHERE UserID = %s"
            cursor.execute(update_query, (hashed_password, self.controller.user_id))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Password changed successfully!",
                icon="check",
                option_1="OK"
            )
        
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to change password: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def sign_out(self):
        """Sign out the admin user."""
        self.controller.sign_out()

class ReportsFrame(ctk.CTkFrame):
    """Reports and analytics screen for administrators."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Reports & Analytics",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Create tab view for different reports
        self.tab_view = ctk.CTkTabview(self, width=800, height=600)
        self.tab_view.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create tabs
        self.tab_view.add("Revenue")
        self.tab_view.add("Orders")
        self.tab_view.add("Restaurants")
        self.tab_view.add("Users")
        
        # Initialize tab contents
        self.initialize_revenue_tab()
        self.initialize_orders_tab()
        self.initialize_restaurants_tab()
        self.initialize_users_tab()
        
        # Export reports button
        self.export_button = ctk.CTkButton(
            self,
            text="Export Reports",
            command=self.export_reports,
            fg_color="#2196F3",
            hover_color="#1976D2",
            corner_radius=5,
            font=("Arial", 14),
            height=40,
            width=200
        )
        self.export_button.pack(pady=(0, 15))
    
    def initialize_revenue_tab(self):
        """Initialize the revenue tab content."""
        tab = self.tab_view.tab("Revenue")
        
        # Date range selector
        range_frame = ctk.CTkFrame(tab, fg_color="transparent")
        range_frame.pack(fill="x", pady=10)
        
        range_label = ctk.CTkLabel(
            range_frame,
            text="Select Date Range:",
            font=("Arial", 14),
            text_color="#333333"
        )
        range_label.pack(side="left", padx=(0, 10))
        
        # Date range options
        range_options = ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last Year", "All Time"]
        self.revenue_range_var = ctk.StringVar(value=range_options[1])
        
        range_dropdown = ctk.CTkOptionMenu(
            range_frame,
            values=range_options,
            variable=self.revenue_range_var,
            command=lambda _: self.refresh_data(),
            width=150
        )
        range_dropdown.pack(side="left")
        
        # Summary stats container
        self.revenue_stats_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10)
        self.revenue_stats_frame.pack(fill="x", pady=10)
        
        # Chart frame
        self.revenue_chart_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=300)
        self.revenue_chart_frame.pack(fill="both", expand=True, pady=10)
    
    def initialize_orders_tab(self):
        """Initialize the orders tab content."""
        tab = self.tab_view.tab("Orders")
        
        # Date range selector
        range_frame = ctk.CTkFrame(tab, fg_color="transparent")
        range_frame.pack(fill="x", pady=10)
        
        range_label = ctk.CTkLabel(
            range_frame,
            text="Select Date Range:",
            font=("Arial", 14),
            text_color="#333333"
        )
        range_label.pack(side="left", padx=(0, 10))
        
        # Date range options
        range_options = ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last Year", "All Time"]
        self.orders_range_var = ctk.StringVar(value=range_options[1])
        
        range_dropdown = ctk.CTkOptionMenu(
            range_frame,
            values=range_options,
            variable=self.orders_range_var,
            command=lambda _: self.refresh_data(),
            width=150
        )
        range_dropdown.pack(side="left")
        
        # Status distribution chart
        self.orders_stats_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=150)
        self.orders_stats_frame.pack(fill="x", pady=10)
        
        # Orders over time chart
        self.orders_chart_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=300)
        self.orders_chart_frame.pack(fill="both", expand=True, pady=10)
    
    def initialize_restaurants_tab(self):
        """Initialize the restaurants tab content."""
        tab = self.tab_view.tab("Restaurants")
        
        # Top restaurants frame
        self.top_restaurants_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=200)
        self.top_restaurants_frame.pack(fill="x", pady=10)
        
        # Restaurant statistics
        self.restaurant_stats_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=300)
        self.restaurant_stats_frame.pack(fill="both", expand=True, pady=10)
    
    def initialize_users_tab(self):
        """Initialize the users tab content."""
        tab = self.tab_view.tab("Users")
        
        # User growth chart
        self.user_growth_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=200)
        self.user_growth_frame.pack(fill="x", pady=10)
        
        # User statistics
        self.user_stats_frame = ctk.CTkFrame(tab, fg_color="white", corner_radius=10, height=300)
        self.user_stats_frame.pack(fill="both", expand=True, pady=10)
    
    def refresh_data(self):
        """Refresh all report data."""
        self.refresh_revenue_data()
        self.refresh_orders_data()
        self.refresh_restaurants_data()
        self.refresh_users_data()
    
    def refresh_revenue_data(self):
        """Refresh revenue report data."""
        # Clear existing widgets
        for widget in self.revenue_stats_frame.winfo_children():
            widget.destroy()
        
        for widget in self.revenue_chart_frame.winfo_children():
            widget.destroy()
        
        # Get date range
        date_range = self.revenue_range_var.get()
        start_date = self.get_start_date_from_range(date_range)
        
        # Get revenue stats
        total_revenue = self.get_total_revenue(start_date)
        avg_order_value = self.get_avg_order_value(start_date)
        revenue_growth = self.get_revenue_growth(start_date)
        
        # Display stats
        stats = [
            ("Total Revenue", f"${total_revenue:.2f}"),
            ("Average Order Value", f"${avg_order_value:.2f}"),
            ("Revenue Growth", f"{revenue_growth:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(self.revenue_stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10, pady=15)
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Arial", 18, "bold"),
                text_color="#333333"
            )
            value_label.pack()
            
            label_widget = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 12),
                text_color="#666666"
            )
            label_widget.pack()
        
        # Create revenue chart
        fig = Figure(figsize=(12, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get revenue data for chart
        revenue_data = self.get_revenue_chart_data(start_date)
        
        # Plot data
        if revenue_data:
            dates = [item['date'] for item in revenue_data]
            revenues = [item['revenue'] for item in revenue_data]
            
            ax.plot(dates, revenues, marker='o', linewidth=2, color='#2196F3')
            ax.set_title('Revenue Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Revenue ($)')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Format y-axis as currency
            import matplotlib.ticker as ticker
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.2f}'))
            
            # Rotate date labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            fig.tight_layout()
            
            # Add figure to chart frame
            canvas = FigureCanvasTkAgg(fig, master=self.revenue_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                self.revenue_chart_frame,
                text="No revenue data available for the selected period.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def refresh_orders_data(self):
        """Refresh orders report data."""
        # Clear existing widgets
        for widget in self.orders_stats_frame.winfo_children():
            widget.destroy()
        
        for widget in self.orders_chart_frame.winfo_children():
            widget.destroy()
        
        # Get date range
        date_range = self.orders_range_var.get()
        start_date = self.get_start_date_from_range(date_range)
        
        # Get order stats
        total_orders = self.get_total_orders(start_date)
        orders_growth = self.get_orders_growth(start_date)
        avg_delivery_time = self.get_avg_delivery_time(start_date)
        
        # Display stats
        stats = [
            ("Total Orders", str(total_orders)),
            ("Order Growth", f"{orders_growth:.1f}%"),
            ("Avg. Delivery Time", f"{avg_delivery_time:.1f} hours")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(self.orders_stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10, pady=15)
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Arial", 18, "bold"),
                text_color="#333333"
            )
            value_label.pack()
            
            label_widget = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 12),
                text_color="#666666"
            )
            label_widget.pack()
        
        # Create orders chart
        fig = Figure(figsize=(12, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get orders data for chart
        orders_data = self.get_orders_chart_data(start_date)
        
        # Plot data
        if orders_data:
            dates = [item['date'] for item in orders_data]
            orders_count = [item['count'] for item in orders_data]
            
            ax.bar(dates, orders_count, color='#4CAF50', alpha=0.7)
            ax.set_title('Orders Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Orders')
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # Rotate date labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            fig.tight_layout()
            
            # Add figure to chart frame
            canvas = FigureCanvasTkAgg(fig, master=self.orders_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                self.orders_chart_frame,
                text="No order data available for the selected period.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def refresh_restaurants_data(self):
        """Refresh restaurants report data."""
        # Clear existing widgets
        for widget in self.top_restaurants_frame.winfo_children():
            widget.destroy()
        
        for widget in self.restaurant_stats_frame.winfo_children():
            widget.destroy()
        
        # Top restaurants label
        top_label = ctk.CTkLabel(
            self.top_restaurants_frame,
            text="Top Performing Restaurants",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        top_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Get top restaurants
        top_restaurants = self.get_top_restaurants()
        
        if top_restaurants:
            # Create scrollable frame for restaurant listings
            restaurants_list = ctk.CTkScrollableFrame(
                self.top_restaurants_frame,
                fg_color="transparent",
                width=750,
                height=150
            )
            restaurants_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            # Create restaurant cards
            for restaurant in top_restaurants:
                self.create_restaurant_report_card(restaurants_list, restaurant)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                self.top_restaurants_frame,
                text="No restaurant data available.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_data_label.pack(pady=30)
        
        # Restaurant statistics
        self.create_restaurant_statistics()
    
    def refresh_users_data(self):
        """Refresh users report data."""
        # Clear existing widgets
        for widget in self.user_growth_frame.winfo_children():
            widget.destroy()
        
        for widget in self.user_stats_frame.winfo_children():
            widget.destroy()
        
        # User growth label
        growth_label = ctk.CTkLabel(
            self.user_growth_frame,
            text="User Growth",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        growth_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Get user statistics
        total_users = self.get_total_users()
        active_users = self.get_active_users()
        user_growth = self.get_user_growth()
        
        # Display stats
        stats_frame = ctk.CTkFrame(self.user_growth_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=10)
        
        stats = [
            ("Total Users", str(total_users)),
            ("Active Users", str(active_users)),
            ("Monthly Growth", f"{user_growth:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", expand=True, padx=10, pady=5)
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Arial", 18, "bold"),
                text_color="#333333"
            )
            value_label.pack()
            
            label_widget = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 12),
                text_color="#666666"
            )
            label_widget.pack()
        
        # User role distribution
        self.create_user_role_chart()
    
    def get_start_date_from_range(self, date_range):
        """Convert date range string to an actual date."""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        if date_range == "Last 7 Days":
            return today - timedelta(days=7)
        elif date_range == "Last 30 Days":
            return today - timedelta(days=30)
        elif date_range == "Last 3 Months":
            return today - timedelta(days=90)
        elif date_range == "Last Year":
            return today - timedelta(days=365)
        else:  # All Time
            return datetime(2020, 1, 1)  # Set a far back date
    
    def get_total_revenue(self, start_date=None):
        """Get total revenue from orders."""
        query = "SELECT SUM(TotalAmount) as total FROM `Order`"
        params = ()
        
        if start_date:
            query += " WHERE OrderDate >= %s"
            params = (start_date,)
        
        result = execute_query(query, params, fetch=True)
        return result[0]['total'] if result and result[0]['total'] else 0.0
    
    def get_avg_order_value(self, start_date=None):
        """Get average order value."""
        query = "SELECT AVG(TotalAmount) as avg FROM `Order`"
        params = ()
        
        if start_date:
            query += " WHERE OrderDate >= %s"
            params = (start_date,)
        
        result = execute_query(query, params, fetch=True)
        return result[0]['avg'] if result and result[0]['avg'] else 0.0
    
    def get_revenue_growth(self, start_date=None):
        """Calculate revenue growth percentage."""
        # For demo purposes, return a random value between 5 and 15
        import random
        return random.uniform(5.0, 15.0)
    
    def get_revenue_chart_data(self, start_date=None):
        """Get revenue data for chart display."""
        query = """
            SELECT DATE(OrderDate) as date, SUM(TotalAmount) as revenue
            FROM `Order`
            WHERE OrderDate >= %s
            GROUP BY DATE(OrderDate)
            ORDER BY date
        """
        
        result = execute_query(query, (start_date,), fetch=True)
        return result or []
    
    def get_total_orders(self, start_date=None):
        """Get total number of orders."""
        query = "SELECT COUNT(*) as total FROM `Order`"
        params = ()
        
        if start_date:
            query += " WHERE OrderDate >= %s"
            params = (start_date,)
        
        result = execute_query(query, params, fetch=True)
        return result[0]['total'] if result else 0
    
    def get_orders_growth(self, start_date=None):
        """Calculate order growth percentage."""
        # For demo purposes, return a random value between 3 and 12
        import random
        return random.uniform(3.0, 12.0)
    
    def get_avg_delivery_time(self, start_date=None):
        """Get average delivery time in hours."""
        # For demo purposes, return a random value between 0.5 and 2.0
        import random
        return random.uniform(0.5, 2.0)
    
    def get_orders_chart_data(self, start_date=None):
        """Get orders data for chart display."""
        query = """
            SELECT DATE(OrderDate) as date, COUNT(*) as count
            FROM `Order`
            WHERE OrderDate >= %s
            GROUP BY DATE(OrderDate)
            ORDER BY date
        """
        
        result = execute_query(query, (start_date,), fetch=True)
        return result or []
    
    def get_top_restaurants(self):
        """Get top performing restaurants based on order count and revenue."""
        query = """
            SELECT r.RestaurantID, r.Name, r.Cuisine, 
                   COUNT(o.OrderID) as order_count, 
                   SUM(o.TotalAmount) as total_revenue
            FROM Restaurant r
            JOIN `Order` o ON r.RestaurantID = o.RestaurantID
            GROUP BY r.RestaurantID, r.Name, r.Cuisine
            ORDER BY total_revenue DESC
            LIMIT 5
        """
        
        return execute_query(query, fetch=True) or []
    
    def create_restaurant_report_card(self, parent, restaurant):
        """Create a card displaying restaurant performance information."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, border_width=1, border_color="#e0e0e0")
        card.pack(fill="x", pady=5, ipady=5, padx=10)
        
        # Restaurant name
        name_label = ctk.CTkLabel(
            card,
            text=restaurant['Name'],
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        name_label.pack(anchor="w", padx=15, pady=(10, 0))
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(
            card,
            text=f"Cuisine: {restaurant.get('Cuisine', 'Not specified')}",
            font=("Arial", 12),
            text_color="#666666"
        )
        cuisine_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Performance metrics
        metrics_frame = ctk.CTkFrame(card, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Order count
        order_count_label = ctk.CTkLabel(
            metrics_frame,
            text=f"Orders: {restaurant.get('order_count', 0)}",
            font=("Arial", 12),
            text_color="#2196F3"
        )
        order_count_label.pack(side="left", padx=(0, 20))
        
        # Revenue
        revenue = restaurant.get('total_revenue', 0)
        revenue_label = ctk.CTkLabel(
            metrics_frame,
            text=f"Revenue: ${revenue:.2f}",
            font=("Arial", 12, "bold"),
            text_color="#4CAF50"
        )
        revenue_label.pack(side="left")
    
    def create_restaurant_statistics(self):
        """Create restaurant statistics charts."""
        # Create a frame for the charts
        charts_frame = ctk.CTkFrame(self.restaurant_stats_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Use grid layout for two charts side by side
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Cuisine distribution chart
        cuisine_frame = ctk.CTkFrame(charts_frame, fg_color="white", corner_radius=10)
        cuisine_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        cuisine_label = ctk.CTkLabel(
            cuisine_frame,
            text="Restaurants by Cuisine",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        cuisine_label.pack(pady=(10, 0))
        
        # Get cuisine distribution data
        cuisine_data = self.get_cuisine_distribution()
        
        if cuisine_data:
            # Create pie chart
            fig1 = Figure(figsize=(5, 4), dpi=100)
            ax1 = fig1.add_subplot(111)
            
            labels = [item['cuisine'] for item in cuisine_data]
            sizes = [item['count'] for item in cuisine_data]
            colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#607D8B']
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            fig1.tight_layout()
            
            # Add figure to frame
            canvas1 = FigureCanvasTkAgg(fig1, master=cuisine_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                cuisine_frame,
                text="No cuisine data available.",
                font=("Arial", 12),
                text_color="#999999"
            )
            no_data_label.pack(pady=50)
        
        # Orders by restaurant chart
        orders_frame = ctk.CTkFrame(charts_frame, fg_color="white", corner_radius=10)
        orders_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        orders_label = ctk.CTkLabel(
            orders_frame,
            text="Top Restaurants by Orders",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        orders_label.pack(pady=(10, 0))
        
        # Get restaurant orders data
        restaurant_orders = self.get_restaurant_orders()
        
        if restaurant_orders:
            # Create bar chart
            fig2 = Figure(figsize=(5, 4), dpi=100)
            ax2 = fig2.add_subplot(111)
            
            restaurants = [item['name'] for item in restaurant_orders]
            order_counts = [item['order_count'] for item in restaurant_orders]
            
            # Horizontal bar chart
            bars = ax2.barh(restaurants, order_counts, color='#2196F3', alpha=0.7)
            ax2.set_xlabel('Number of Orders')
            ax2.grid(True, linestyle='--', alpha=0.7, axis='x')
            
            # Add the number at the end of each bar
            for i, (restaurant, count) in enumerate(zip(restaurants, order_counts)):
                ax2.text(count + 0.1, i, str(count), va='center')
            
            fig2.tight_layout()
            
            # Add figure to frame
            canvas2 = FigureCanvasTkAgg(fig2, master=orders_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                orders_frame,
                text="No restaurant orders data available.",
                font=("Arial", 12),
                text_color="#999999"
            )
            no_data_label.pack(pady=50)
    
    def get_cuisine_distribution(self):
        """Get distribution of restaurants by cuisine."""
        query = """
            SELECT Cuisine as cuisine, COUNT(*) as count
            FROM Restaurant
            WHERE Cuisine IS NOT NULL AND Cuisine != ''
            GROUP BY Cuisine
            ORDER BY count DESC
        """
        
        return execute_query(query, fetch=True) or []
    
    def get_restaurant_orders(self):
        """Get top restaurants by order count."""
        query = """
            SELECT r.Name as name, COUNT(o.OrderID) as order_count
            FROM Restaurant r
            JOIN `Order` o ON r.RestaurantID = o.RestaurantID
            GROUP BY r.Name
            ORDER BY order_count DESC
            LIMIT 5
        """
        
        return execute_query(query, fetch=True) or []
    
    def create_user_role_chart(self):
        """Create user role distribution chart."""
        # User role distribution label
        role_label = ctk.CTkLabel(
            self.user_stats_frame,
            text="User Role Distribution",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        role_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Get user role distribution
        role_data = self.get_user_role_distribution()
        
        if role_data:
            # Create pie chart
            fig = Figure(figsize=(6, 5), dpi=100)
            ax = fig.add_subplot(111)
            
            labels = [item['role'] for item in role_data]
            sizes = [item['count'] for item in role_data]
            colors = ['#FF9800', '#2196F3', '#4CAF50']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            fig.tight_layout()
            
            # Add figure to frame
            canvas = FigureCanvasTkAgg(fig, master=self.user_stats_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=10)
        else:
            # No data
            no_data_label = ctk.CTkLabel(
                self.user_stats_frame,
                text="No user role data available.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_data_label.pack(pady=50)
    
    def get_total_users(self):
        """Get total number of users."""
        query = "SELECT COUNT(*) as total FROM User"
        result = execute_query(query, fetch=True)
        return result[0]['total'] if result else 0
    
    def get_active_users(self):
        """Get number of active users (users who placed orders in the last 30 days)."""
        query = """
            SELECT COUNT(DISTINCT UserID) as active
            FROM `Order`
            WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        result = execute_query(query, fetch=True)
        return result[0]['active'] if result else 0
    
    def get_user_growth(self):
        """Calculate user growth percentage."""
        # For demo purposes, return a random value between 2 and 8
        import random
        return random.uniform(2.0, 8.0)
    
    def get_user_role_distribution(self):
        """Get distribution of users by role."""
        query = """
            SELECT Role as role, COUNT(*) as count
            FROM User
            GROUP BY Role
            ORDER BY count DESC
        """
        
        return execute_query(query, fetch=True) or []
    
    def export_reports(self):
        """Export reports to CSV files."""
        try:
            import os
            import csv
            from datetime import datetime
            
            # Create exports directory if it doesn't exist
            export_dir = "reports_exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export revenue data
            revenue_data = self.get_revenue_chart_data(self.get_start_date_from_range("All Time"))
            if revenue_data:
                revenue_file = os.path.join(export_dir, f"revenue_report_{timestamp}.csv")
                with open(revenue_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Revenue'])
                    for item in revenue_data:
                        writer.writerow([item['date'], item['revenue']])
            
            # Export restaurant data
            restaurant_data = self.get_top_restaurants()
            if restaurant_data:
                restaurant_file = os.path.join(export_dir, f"restaurant_report_{timestamp}.csv")
                with open(restaurant_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Restaurant ID', 'Name', 'Cuisine', 'Order Count', 'Total Revenue'])
                    for item in restaurant_data:
                        writer.writerow([
                            item['RestaurantID'], 
                            item['Name'], 
                            item['Cuisine'], 
                            item['order_count'], 
                            item['total_revenue']
                        ])
            
            # Export user role data
            user_data = self.get_user_role_distribution()
            if user_data:
                user_file = os.path.join(export_dir, f"user_report_{timestamp}.csv")
                with open(user_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Role', 'Count'])
                    for item in user_data:
                        writer.writerow([item['role'], item['count']])
                        
            # Export orders data
            orders_data = self.get_orders_chart_data(self.get_start_date_from_range("All Time"))
            if orders_data:
                orders_file = os.path.join(export_dir, f"orders_report_{timestamp}.csv")
                with open(orders_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Order Count'])
                    for item in orders_data:
                        writer.writerow([item['date'], item['count']])
            
            # Show success message
            CTkMessagebox(
                title="Export Success",
                message=f"Reports successfully exported to '{export_dir}' directory!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            # Show error message
            CTkMessagebox(
                title="Export Error",
                message=f"Error exporting reports: {e}",
                icon="cancel",
                option_1="OK"
            )
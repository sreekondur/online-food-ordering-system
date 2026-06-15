import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime
from custom.navigation_frame_restaurant import NavigationFrameRestaurant
from utils import connect_to_database, execute_query
from CTkMessagebox import CTkMessagebox

class RestaurantDashboard(ctk.CTkFrame):
    """Dashboard for restaurant owners to manage their restaurant."""
    def __init__(self, master, user_id=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store user information
        self.master = master
        self.user_id = user_id
        self.restaurant_data = self.get_restaurant_data()
        
        # Configure this frame
        self.configure(fg_color="#f5f5f5")
        
        # Create main content container (all screens will be placed here)
        self.content_container = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)
        
        # Create and place navigation at bottom
        self.navigation_frame = NavigationFrameRestaurant(self, user_id=self.user_id)
        self.navigation_frame.pack(side="bottom", fill="x")
        
        # Initialize frames for different screens
        self.home_frame = HomeFrame(self.content_container, self)
        self.menu_frame = MenuFrame(self.content_container, self)
        self.orders_frame = OrdersFrame(self.content_container, self)
        self.analytics_frame = AnalyticsFrame(self.content_container, self)
        self.settings_frame = SettingsFrame(self.content_container, self)
        
        # Show default frame (home)
        self.show_frame("home")
        
    def get_restaurant_data(self):
        """Fetch restaurant data from database for the current user using RestaurantOwner table."""
        if not self.user_id:
            return {"Name": "Restaurant", "RestaurantID": None}
        
        # Updated query to use the RestaurantOwner table
        query = """
            SELECT r.* 
            FROM Restaurant r
            JOIN RestaurantOwner ro ON r.RestaurantID = ro.RestaurantID
            WHERE ro.UserID = %s
        """
        result = execute_query(query, (self.user_id,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]
        else:
            return {"Name": "Restaurant", "RestaurantID": None}
    
    def show_frame(self, frame_name, **kwargs):
        """Show selected frame and hide others."""
        # Hide all frames
        for frame in [self.home_frame, self.menu_frame, self.orders_frame, 
                     self.analytics_frame, self.settings_frame]:
            frame.pack_forget()
        
        # Show selected frame
        if frame_name == "home":
            self.home_frame.pack(fill="both", expand=True)
        elif frame_name == "menu":
            self.menu_frame.refresh_menu()
            self.menu_frame.pack(fill="both", expand=True)
        elif frame_name == "orders":
            self.orders_frame.refresh_orders()
            self.orders_frame.pack(fill="both", expand=True)
        elif frame_name == "analytics":
            self.analytics_frame.pack(fill="both", expand=True)
        elif frame_name == "settings":
            self.settings_frame.pack(fill="both", expand=True)
    
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
    """Home screen for restaurant dashboard with overview and quick actions."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title section
        restaurant_name = controller.restaurant_data.get("Name", "My Restaurant")
        self.title_label = ctk.CTkLabel(
            self, 
            text=f"Welcome, {restaurant_name}",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Quick stats frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.stats_frame.pack(fill="x", padx=15, pady=10)
        
        # Define stats
        stats = [
            ("Total Orders", self.get_total_orders()),
            ("Total Revenue", f"${self.get_total_revenue():.2f}"),
            ("Pending Orders", self.get_pending_orders())
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
            ("Add Menu Item", self.add_menu_item),
            ("View Orders", lambda: self.controller.show_frame("orders")),
            ("Update Profile", self.update_profile)
        ]
        
        # Create action buttons
        for action_text, command in actions:
            action_button = ctk.CTkButton(
                self.actions_frame,
                text=action_text,
                command=command,
                fg_color="#FF9800",
                hover_color="#F57C00",
                corner_radius=10,
                font=("Arial", 14),
                height=40
            )
            action_button.pack(fill="x", padx=10, pady=10)
    
    def get_total_orders(self):
        """Get total number of orders."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            return 0
        
        query = "SELECT COUNT(*) as total FROM `Order` WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]["total"] if result else 0
    
    def get_total_revenue(self):
        """Get total revenue."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            return 0.0
        
        query = "SELECT SUM(TotalAmount) as revenue FROM `Order` WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]["revenue"] if result and result[0]["revenue"] else 0.0
    
    def get_pending_orders(self):
        """Get number of pending orders."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            return 0
        
        query = "SELECT COUNT(*) as total FROM `Order` WHERE RestaurantID = %s AND OrderStatus = 'pending'"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]["total"] if result else 0
    
    def add_menu_item(self):
        """Open add menu item dialog."""
        self.controller.show_frame("menu")
    
    def update_profile(self):
        """Open profile update dialog."""
        self.controller.show_frame("settings")

class MenuFrame(ctk.CTkFrame):
    """Screen for managing restaurant menu items."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Manage Menu",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Add menu item button
        self.add_item_button = ctk.CTkButton(
            self,
            text="Add New Menu Item",
            command=self.open_add_item_dialog,
            fg_color="#FF9800",
            hover_color="#F57C00",
            corner_radius=10,
            font=("Arial", 14),
            height=40,
            width=250
        )
        self.add_item_button.pack(pady=(0, 15))
        
        # Menu items container
        self.menu_items_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.menu_items_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Refresh menu items
        self.refresh_menu()
    
    def refresh_menu(self):
        """Refresh and display menu items."""
        # Clear existing items
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        # Get menu items
        menu_items = self.get_menu_items()
        
        if not menu_items:
            # No menu items
            no_items_label = ctk.CTkLabel(
                self.menu_items_frame,
                text="No menu items. Add some!",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_items_label.pack(pady=50)
            return
        
        # Display menu items
        for item in menu_items:
            self.create_menu_item_card(item)
    
    def get_menu_items(self):
        """Get menu items for the restaurant."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            return []
        
        query = "SELECT * FROM Menu WHERE RestaurantID = %s"
        return execute_query(query, (restaurant_id,), fetch=True) or []
    
    def create_menu_item_card(self, item):
        """Create a card for a menu item."""
        # Card frame
        card = ctk.CTkFrame(self.menu_items_frame, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=5, ipady=10)
        
        # Left side - food image
        image_frame = ctk.CTkFrame(card, width=80, height=80, fg_color="#e0e0e0")
        image_frame.pack(side="left", padx=10, pady=10)
        
        # Try to load menu item image
        try:
            image_filename = f"menu_item_{item['MenuID']}.png"
            image_path = self.get_image_path(image_filename)
            
            if image_path:
                image = ctk.CTkImage(
                    light_image=Image.open(image_path),
                    size=(80, 80)
                )
                image_label = ctk.CTkLabel(
                    image_frame, 
                    image=image, 
                    text=""
                )
                image_label.pack(expand=True, fill="both")
            else:
                raise FileNotFoundError("Menu item image not found")
        except Exception:
            # Fallback to text placeholder if image loading fails
            placeholder_label = ctk.CTkLabel(
                image_frame,
                text="Food",
                font=("Arial", 12),
                text_color="#888888"
            )
            placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Middle - item details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        # Item name
        name_label = ctk.CTkLabel(
            details_frame,
            text=item["ItemName"],
            font=("Arial", 14, "bold"),
            text_color="#333333",
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Item description
        desc_label = ctk.CTkLabel(
            details_frame,
            text=item.get("Description", "No description"),
            font=("Arial", 12),
            text_color="#666666",
            anchor="w",
            wraplength=200
        )
        desc_label.pack(anchor="w")
        
        # Item price
        price_label = ctk.CTkLabel(
            details_frame,
            text=f"${item['Price']:.2f}",
            font=("Arial", 14),
            text_color="#4CAF50",
            anchor="w"
        )
        price_label.pack(anchor="w")
        
        # Right side - action buttons
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            width=70,
            height=30,
            fg_color="#2196F3",
            hover_color="#1976D2",
            corner_radius=5,
            command=lambda i=item: self.edit_menu_item(i)
        )
        edit_btn.pack(pady=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=70,
            height=30,
            fg_color="#F44336",
            hover_color="#D32F2F",
            corner_radius=5,
            command=lambda i=item: self.delete_menu_item(i)
        )
        delete_btn.pack(pady=5)
    
    def get_image_path(self, filename):
        """Get the full path to an image file."""
        base_path = os.path.join('static', 'images', 'menu')
        full_path = os.path.join(base_path, filename)
        
        # Fallback image if specific image not found
        if not os.path.exists(full_path):
            fallback_path = os.path.join(base_path, 'default.png')
            if os.path.exists(fallback_path):
                return fallback_path
            return None
        
        return full_path
    
    def open_add_item_dialog(self):
        """Open dialog to add a new menu item."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Menu Item")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make the dialog modal
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Item Name", anchor="w")
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.pack(padx=20, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(dialog, text="Description", anchor="w")
        desc_label.pack(padx=20, pady=(10, 5), anchor="w")
        desc_entry = ctk.CTkTextbox(dialog, width=350, height=100)
        desc_entry.pack(padx=20, pady=5)
        
        # Price
        price_label = ctk.CTkLabel(dialog, text="Price", anchor="w")
        price_label.pack(padx=20, pady=(10, 5), anchor="w")
        price_entry = ctk.CTkEntry(dialog, width=350)
        price_entry.pack(padx=20, pady=5)
        
        # Image upload (placeholder)
        image_label = ctk.CTkLabel(dialog, text="Upload Image (Optional)", anchor="w")
        image_label.pack(padx=20, pady=(10, 5), anchor="w")
        upload_btn = ctk.CTkButton(
            dialog, 
            text="Choose Image", 
            command=self.upload_menu_item_image,
            width=350
        )
        upload_btn.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Save Menu Item", 
            command=lambda: self.save_menu_item(
                name_entry.get(), 
                desc_entry.get("1.0", "end-1c"), 
                price_entry.get(), 
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def upload_menu_item_image(self):
        """Placeholder for image upload functionality."""
        CTkMessagebox(
            title="Image Upload",
            message="Image upload will be available in a future update.",
            icon="info",
            option_1="OK"
        )
    
    def save_menu_item(self, name, description, price, dialog):
        """Save a new menu item to the database."""
        # Validate inputs
        if not name or not price:
            CTkMessagebox(
                title="Validation Error",
                message="Item Name and Price are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Validate price
        try:
            price = float(price)
        except ValueError:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid price. Use a numeric value.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Get restaurant ID
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            CTkMessagebox(
                title="Error",
                message="Restaurant not found.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Insert menu item
        query = """
            INSERT INTO Menu (RestaurantID, ItemName, Description, Price)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (restaurant_id, name, description, price))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Refresh menu
            self.refresh_menu()
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Menu item added successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to add menu item: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def edit_menu_item(self, item):
        """Open dialog to edit an existing menu item."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Menu Item")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make the dialog modal
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Item Name", anchor="w")
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.insert(0, item["ItemName"])
        name_entry.pack(padx=20, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(dialog, text="Description", anchor="w")
        desc_label.pack(padx=20, pady=(10, 5), anchor="w")
        desc_entry = ctk.CTkTextbox(dialog, width=350, height=100)
        desc_entry.insert("1.0", item.get("Description", ""))
        desc_entry.pack(padx=20, pady=5)
        
        # Price
        price_label = ctk.CTkLabel(dialog, text="Price", anchor="w")
        price_label.pack(padx=20, pady=(10, 5), anchor="w")
        price_entry = ctk.CTkEntry(dialog, width=350)
        price_entry.insert(0, f"{item['Price']:.2f}")
        price_entry.pack(padx=20, pady=5)
        
        # Image upload (placeholder)
        image_label = ctk.CTkLabel(dialog, text="Update Image (Optional)", anchor="w")
        image_label.pack(padx=20, pady=(10, 5), anchor="w")
        upload_btn = ctk.CTkButton(
            dialog, 
            text="Choose Image", 
            command=self.upload_menu_item_image,
            width=350
        )
        upload_btn.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Update Menu Item", 
            command=lambda: self.update_menu_item(
                item['MenuID'],
                name_entry.get(), 
                desc_entry.get("1.0", "end-1c"), 
                price_entry.get(), 
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def update_menu_item(self, menu_id, name, description, price, dialog):
        """Update an existing menu item in the database."""
        # Validate inputs
        if not name or not price:
            CTkMessagebox(
                title="Validation Error",
                message="Item Name and Price are required.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Validate price
        try:
            price = float(price)
        except ValueError:
            CTkMessagebox(
                title="Validation Error",
                message="Invalid price. Use a numeric value.",
                icon="warning",
                option_1="OK"
            )
            return
        
        # Update menu item
        query = """
            UPDATE Menu 
            SET ItemName = %s, Description = %s, Price = %s
            WHERE MenuID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (name, description, price, menu_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Refresh menu
            self.refresh_menu()
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Menu item updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update menu item: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def delete_menu_item(self, item):
        """Delete a menu item from the database."""
        # Confirm deletion
        confirm = CTkMessagebox(
            title="Delete Menu Item",
            message=f"Are you sure you want to delete '{item['ItemName']}'?",
            icon="question",
            option_1="Yes",
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Delete menu item
            query = "DELETE FROM Menu WHERE MenuID = %s"
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(query, (item['MenuID'],))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Refresh menu
                self.refresh_menu()
                
                # Show success message
                CTkMessagebox(
                    title="Success",
                    message="Menu item deleted successfully!",
                    icon="check",
                    option_1="OK"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Database Error",
                    message=f"Failed to delete menu item: {e}",
                    icon="cancel",
                    option_1="OK"
                )

class OrdersFrame(ctk.CTkFrame):
    """Orders screen for restaurant to manage and track orders."""
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
    
    def refresh_orders(self):
        """Refresh and display orders."""
        # Clear existing items
        for widget in self.orders_container.winfo_children():
            widget.destroy()
        
        # Get orders
        orders = self.get_orders()
        
        if not orders:
            # No orders
            no_orders_label = ctk.CTkLabel(
                self.orders_container,
                text="No orders yet.",
                font=("Arial", 14),
                text_color="#999999"
            )
            no_orders_label.pack(pady=50)
            return
        
        # Display orders
        for order in orders:
            self.create_order_card(order)
    
    def get_orders(self):
        """Get orders for the restaurant."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            return []
        
        query = """
            SELECT o.*, u.FirstName, u.LastName 
            FROM `Order` o
            JOIN User u ON o.UserID = u.UserID
            WHERE o.RestaurantID = %s
            ORDER BY o.OrderDate DESC
        """
        orders = execute_query(query, (restaurant_id,), fetch=True)
        
        # Fetch order items for each order
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
        
        # Customer name
        customer_label = ctk.CTkLabel(
            card,
            text=f"Customer: {order['FirstName']} {order['LastName']}",
            font=("Arial", 12),
            text_color="#333333"
        )
        customer_label.pack(anchor="w", padx=10, pady=5)
        
        # Order items
        for item in order['Items']:
            item_frame = ctk.CTkFrame(card, fg_color="transparent")
            item_frame.pack(fill="x", padx=10, pady=2)
            
            item_name_label = ctk.CTkLabel(
                item_frame,
                text=item['ItemName'],
                font=("Arial", 12),
                text_color="#666666"
            )
            item_name_label.pack(side="left")
            
            quantity_label = ctk.CTkLabel(
                item_frame,
                text=f"Qty: {item['Quantity']}",
                font=("Arial", 12),
                text_color="#666666"
            )
            quantity_label.pack(side="right")
        
        # Total amount
        total_label = ctk.CTkLabel(
            card,
            text=f"Total: ${order['TotalAmount']:.2f}",
            font=("Arial", 14, "bold"),
            text_color="#4CAF50"
        )
        total_label.pack(anchor="w", padx=10, pady=5)
        
        # Status and Actions
        status_frame = ctk.CTkFrame(card, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Current status
        status_label = ctk.CTkLabel(
            status_frame,
            text=f"Status: {order['OrderStatus']}",
            font=("Arial", 12),
            text_color="#FF9800"
        )
        status_label.pack(side="left")
        
        # Update status dropdown
        status_options = ["pending", "preparing", "shipped", "delivered"]
        current_status = order['OrderStatus']
        status_var = ctk.StringVar(value=current_status)
        
        status_dropdown = ctk.CTkOptionMenu(
            status_frame,
            values=status_options,
            variable=status_var,
            command=lambda value, o_id=order['OrderID']: self.update_order_status(o_id, value)
        )
        status_dropdown.pack(side="right")
    
    def update_order_status(self, order_id, new_status):
        """Update order status in the database."""
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
                message="Order status updated successfully!",
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

class AnalyticsFrame(ctk.CTkFrame):
    """Analytics screen for restaurant performance insights."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Restaurant Analytics",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 15))
        
        # Create scrollable frame for analytics
        self.analytics_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#f5f5f5",
            width=350,
            height=450
        )
        self.analytics_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Load and display analytics
        self.load_analytics()
    
    def load_analytics(self):
        """Load and display various analytics metrics."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            self.show_no_data()
            return
        
        # Prepare analytics sections
        analytics_sections = [
            ("Total Revenue", self.get_total_revenue(restaurant_id)),
            ("Total Orders", self.get_total_orders(restaurant_id)),
            ("Average Order Value", self.get_average_order_value(restaurant_id)),
            ("Top-Selling Items", self.get_top_selling_items(restaurant_id)),
            ("Order Status Distribution", self.get_order_status_distribution(restaurant_id))
        ]
        
        # Display each analytics section
        for title, data in analytics_sections:
            section_frame = ctk.CTkFrame(self.analytics_container, fg_color="white", corner_radius=10)
            section_frame.pack(fill="x", pady=5, ipady=10)
            
            # Section title
            title_label = ctk.CTkLabel(
                section_frame,
                text=title,
                font=("Arial", 16, "bold"),
                text_color="#333333"
            )
            title_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Section content
            if isinstance(data, (int, float)):
                # Simple numeric value
                value_label = ctk.CTkLabel(
                    section_frame,
                    text=f"{data}" if isinstance(data, int) else f"${data:.2f}",
                    font=("Arial", 18),
                    text_color="#4CAF50"
                )
                value_label.pack(padx=10, pady=5)
            elif isinstance(data, list):
                # List of items or key-value pairs
                for item in data[:5]:  # Limit to top 5
                    item_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
                    item_frame.pack(fill="x", padx=10, pady=2)
                    
                    if isinstance(item, dict):
                        # For top-selling items or status distribution
                        name_label = ctk.CTkLabel(
                            item_frame,
                            text=str(item.get('name', 'Unknown')),
                            font=("Arial", 12),
                            text_color="#666666"
                        )
                        name_label.pack(side="left")
                        
                        value_label = ctk.CTkLabel(
                            item_frame,
                            text=str(item.get('value', 0)),
                            font=("Arial", 12),
                            text_color="#4CAF50"
                        )
                        value_label.pack(side="right")
    
    def show_no_data(self):
        """Display message when no restaurant data is available."""
        no_data_label = ctk.CTkLabel(
            self.analytics_container,
            text="No analytics data available.",
            font=("Arial", 14),
            text_color="#999999"
        )
        no_data_label.pack(pady=50)
    
    def get_total_revenue(self, restaurant_id):
        """Calculate total revenue for the restaurant."""
        query = "SELECT SUM(TotalAmount) as total_revenue FROM `Order` WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]['total_revenue'] if result and result[0]['total_revenue'] else 0.0
    
    def get_total_orders(self, restaurant_id):
        """Get total number of orders for the restaurant."""
        query = "SELECT COUNT(*) as total_orders FROM `Order` WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]['total_orders'] if result else 0
    
    def get_average_order_value(self, restaurant_id):
        """Calculate average order value."""
        query = "SELECT AVG(TotalAmount) as avg_order_value FROM `Order` WHERE RestaurantID = %s"
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result[0]['avg_order_value'] if result and result[0]['avg_order_value'] else 0.0
    
    def get_top_selling_items(self, restaurant_id):
        """Get top-selling menu items."""
        query = """
            SELECT m.ItemName as name, SUM(oi.Quantity) as value
            FROM OrderItem oi
            JOIN Menu m ON oi.MenuID = m.MenuID
            JOIN `Order` o ON oi.OrderID = o.OrderID
            WHERE o.RestaurantID = %s
            GROUP BY m.ItemName
            ORDER BY value DESC
            LIMIT 5
        """
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result if result else []
    
    def get_order_status_distribution(self, restaurant_id):
        """Get distribution of order statuses."""
        query = """
            SELECT OrderStatus as name, COUNT(*) as value
            FROM `Order`
            WHERE RestaurantID = %s
            GROUP BY OrderStatus
        """
        result = execute_query(query, (restaurant_id,), fetch=True)
        return result if result else []

class SettingsFrame(ctk.CTkFrame):
    """Settings screen for restaurant profile and account management."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f5f5", corner_radius=0)
        self.controller = controller
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Restaurant Settings",
            font=("Arial", 24, "bold"),
            text_color="#333333"
        )
        self.title_label.pack(pady=(20, 20))
        
        # Profile settings container
        self.profile_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.profile_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Load restaurant data
        restaurant_data = self.controller.restaurant_data
        
        # Profile fields
        fields = [
            ("Restaurant Name", restaurant_data.get('Name', 'Restaurant')),
            ("Cuisine", restaurant_data.get('Cuisine', 'Not Specified')),
            ("Contact", restaurant_data.get('Contact', 'N/A')),
            ("Location", restaurant_data.get('Location', 'Not Set'))
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
            text="Edit Restaurant Profile",
            command=self.edit_profile,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            corner_radius=5,
            font=("Arial", 16),
            height=40,
            width=350
        )
        self.edit_button.pack(pady=(0, 20))
        
        # Account Settings Section
        self.account_label = ctk.CTkLabel(
            self,
            text="Account Settings",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.account_label.pack(anchor="w", padx=15, pady=(20, 10))
        
        # Account settings container
        self.account_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.account_container.pack(fill="x", padx=15, pady=(0, 20))
        
        # Account options
        account_options = [
            ("Change Password", self.change_password),
            ("Update Contact Info", self.update_contact),
            ("Manage Restaurant Hours", self.manage_hours),
            ("Logout", self.logout)
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
    
    def edit_profile(self):
        """Open dialog to edit restaurant profile."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Restaurant Profile")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Restaurant Name", anchor="w")
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.insert(0, self.controller.restaurant_data.get('Name', ''))
        name_entry.pack(padx=20, pady=5)
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(dialog, text="Cuisine", anchor="w")
        cuisine_label.pack(padx=20, pady=(10, 5), anchor="w")
        cuisine_entry = ctk.CTkEntry(dialog, width=350)
        cuisine_entry.insert(0, self.controller.restaurant_data.get('Cuisine', ''))
        cuisine_entry.pack(padx=20, pady=5)
        
        # Contact
        contact_label = ctk.CTkLabel(dialog, text="Contact Number", anchor="w")
        contact_label.pack(padx=20, pady=(10, 5), anchor="w")
        contact_entry = ctk.CTkEntry(dialog, width=350)
        contact_entry.insert(0, self.controller.restaurant_data.get('Contact', ''))
        contact_entry.pack(padx=20, pady=5)
        
        # Location
        location_label = ctk.CTkLabel(dialog, text="Location", anchor="w")
        location_label.pack(padx=20, pady=(10, 5), anchor="w")
        location_entry = ctk.CTkEntry(dialog, width=350)
        location_entry.insert(0, self.controller.restaurant_data.get('Location', ''))
        location_entry.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Save Changes", 
            command=lambda: self.save_profile_changes(
                name_entry.get(), 
                cuisine_entry.get(), 
                contact_entry.get(), 
                location_entry.get(), 
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_profile_changes(self, name, cuisine, contact, location, dialog):
        """Save restaurant profile changes to database."""
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            CTkMessagebox(
                title="Error",
                message="Restaurant not found.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        query = """
            UPDATE Restaurant 
            SET Name = %s, Cuisine = %s, Contact = %s, Location = %s
            WHERE RestaurantID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (name, cuisine, contact, location, restaurant_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update local restaurant data
            self.controller.restaurant_data.update({
                'Name': name,
                'Cuisine': cuisine,
                'Contact': contact,
                'Location': location
            })
            
            # Refresh the view
            self.pack_forget()
            self.pack(fill="both", expand=True)
            
            # Close dialog
            dialog.destroy()
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Restaurant profile updated successfully!",
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
        """Update user password."""
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
    
    def update_contact(self):
        """Open dialog to update contact information."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Contact Information")
        dialog.geometry("400x300")
        dialog.grab_set()  # Make dialog modal
        
        # Phone Number
        phone_label = ctk.CTkLabel(dialog, text="Phone Number", anchor="w")
        phone_label.pack(padx=20, pady=(20, 5), anchor="w")
        phone_entry = ctk.CTkEntry(dialog, width=350)
        phone_entry.insert(0, self.controller.restaurant_data.get('Contact', ''))
        phone_entry.pack(padx=20, pady=5)
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Contact Email", anchor="w")
        email_label.pack(padx=20, pady=(10, 5), anchor="w")
        email_entry = ctk.CTkEntry(dialog, width=350)
        email_entry.pack(padx=20, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Save Contact Info", 
            command=lambda: self.save_contact_info(
                phone_entry.get(), 
                email_entry.get(), 
                dialog
            ),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def save_contact_info(self, phone, email, dialog):
        """Save contact information to database."""
        # Validate inputs (basic validation)
        if not phone and not email:
            CTkMessagebox(
                title="Validation Error",
                message="Please provide at least one contact method.",
                icon="warning",
                option_1="OK"
            )
            return
        
        restaurant_id = self.controller.restaurant_data.get("RestaurantID")
        if not restaurant_id:
            CTkMessagebox(
                title="Error",
                message="Restaurant not found.",
                icon="cancel",
                option_1="OK"
            )
            return
        
        # Update contact info in restaurant table
        query = """
            UPDATE Restaurant 
            SET Contact = %s
            WHERE RestaurantID = %s
        """
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, (phone, restaurant_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update local restaurant data
            self.controller.restaurant_data['Contact'] = phone
            
            # Close dialog
            dialog.destroy()
            
            # Refresh the view
            self.pack_forget()
            self.pack(fill="both", expand=True)
            
            # Show success message
            CTkMessagebox(
                title="Success",
                message="Contact information updated successfully!",
                icon="check",
                option_1="OK"
            )
        except Exception as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to update contact info: {e}",
                icon="cancel",
                option_1="OK"
            )
    
    def manage_hours(self):
        """Open dialog to manage restaurant hours."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manage Restaurant Hours")
        dialog.geometry("400x500")
        dialog.grab_set()  # Make dialog modal
        
        # Days of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Create frames for each day
        for day in days:
            day_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            day_frame.pack(fill="x", padx=20, pady=5)
            
            # Day label
            day_label = ctk.CTkLabel(day_frame, text=day, width=100)
            day_label.pack(side="left", padx=(0, 10))
            
            # Enabled checkbox
            enabled_var = ctk.BooleanVar(value=True)
            enabled_check = ctk.CTkCheckBox(
                day_frame, 
                text="Open", 
                variable=enabled_var,
                command=lambda d=day, var=enabled_var: self.toggle_day_hours(d, var)
            )
            enabled_check.pack(side="left", padx=(0, 10))
            
            # Open time
            open_label = ctk.CTkLabel(day_frame, text="Open:")
            open_label.pack(side="left", padx=(0, 5))
            open_time = ctk.CTkEntry(day_frame, width=70, placeholder_text="09:00")
            open_time.pack(side="left", padx=(0, 10))
            
            # Close time
            close_label = ctk.CTkLabel(day_frame, text="Close:")
            close_label.pack(side="left", padx=(0, 5))
            close_time = ctk.CTkEntry(day_frame, width=70, placeholder_text="21:00")
            close_time.pack(side="left")
        
        # Save button
        save_btn = ctk.CTkButton(
            dialog, 
            text="Save Restaurant Hours", 
            command=lambda: self.save_restaurant_hours(dialog),
            width=350,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_btn.pack(padx=20, pady=(20, 10))
    
    def toggle_day_hours(self, day, enabled_var):
        """Enable/disable hours for a specific day."""
        # This is a placeholder for more complex hour management
        CTkMessagebox(
            title="Feature Unavailable",
            message="Detailed hour management will be available in a future update.",
            icon="info",
            option_1="OK"
        )
    
    def save_restaurant_hours(self, dialog):
        """Save restaurant hours (placeholder)."""
        CTkMessagebox(
            title="Feature Unavailable",
            message="Hour management will be available in a future update.",
            icon="info",
            option_1="OK"
        )
        dialog.destroy()
    
    def logout(self):
        """Logout the restaurant user."""
        self.controller.sign_out()
import customtkinter as ctk

class NavigationFrameAdmin(ctk.CTkFrame):
    def __init__(self, master=None, user_id=None):
        super().__init__(master, corner_radius=0)
        self.master = master
        self.user_id = user_id
        
        # Configure frame appearance - change to white background with shadow
        self.configure(fg_color="white", height=70)
        
        # Add a subtle top border for shadow effect
        self.border_frame = ctk.CTkFrame(self, height=1, fg_color="#e0e0e0")
        self.border_frame.place(relx=0, rely=0, relwidth=1)
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        for i in range(5):
            self.grid_columnconfigure(i, weight=1)

        # Create the navigation buttons with text icons
        self.create_navigation_button("home", "Dashboard", "🏠", 0)
        self.create_navigation_button("users", "Users", "👥", 1)
        self.create_navigation_button("restaurants", "Restaurants", "🍽️", 2)
        self.create_navigation_button("orders", "Orders", "🛒", 3)
        self.create_navigation_button("settings", "Settings", "⚙️", 4)
        
        # Set initial selected button
        self.set_selected_button("home")

    def create_navigation_button(self, frame_name, text, icon, col_index):
        """Create a navigation button with an icon and text."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=col_index, sticky="nsew", padx=2)
        frame.grid_rowconfigure((0, 1), weight=0)
        frame.grid_columnconfigure(0, weight=1)
        
        # Create the button with icon text
        button = ctk.CTkButton(
            frame,
            text=icon,
            command=lambda name=frame_name: self.navigate_to(name),
            fg_color="transparent",
            hover_color="#f5f5f5",
            corner_radius=10,
            width=40,
            height=30,
            font=("Arial", 18)
        )
        button.grid(row=0, column=0, padx=5, pady=(5, 2))
        
        # Create the text label
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 11),
            text_color="#808080",
            width=8,
            height=8
        )
        label.grid(row=1, column=0, padx=5, pady=(0, 2))
        
        # Store the button and label as attributes
        setattr(self, f"{frame_name}_button", button)
        setattr(self, f"{frame_name}_label", label)

    def navigate_to(self, frame_name):
        """Navigate to a specific frame and update the button appearance."""
        # First, reset all buttons to default state
        self.reset_button_styles()
        
        # Handle special case for logout
        if frame_name == "logout":
            self.master.sign_out()
            return
            
        # Set the selected button style
        self.set_selected_button(frame_name)
        
        # Tell the master frame to show the selected frame
        self.master.show_frame(frame_name)

    def reset_button_styles(self):
        """Reset all button styles to default."""
        for name in ["home", "users", "restaurants", "orders", "settings"]:
            button = getattr(self, f"{name}_button", None)
            label = getattr(self, f"{name}_label", None)
            if button:
                button.configure(fg_color="transparent", text_color="#808080")
            if label:
                label.configure(text_color="#808080")

    def set_selected_button(self, selected_name):
        """Set the style of the selected button."""
        button = getattr(self, f"{selected_name}_button", None)
        label = getattr(self, f"{selected_name}_label", None)
        if button:
            # Change to transparent with green text, matching the design
            button.configure(fg_color="transparent", text_color="#22C55E")
        if label:
            label.configure(text_color="#22C55E")  # Green color for selected item
            
    def add_logout_option(self):
        """Add logout option to the settings menu."""
        # Create a logout button at the bottom of the screen
        logout_frame = ctk.CTkFrame(self.master, fg_color="#f9f9f9", height=40)
        logout_frame.pack(side="bottom", fill="x", before=self)
        
        logout_button = ctk.CTkButton(
            logout_frame,
            text="Logout",
            command=self.master.sign_out,
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=5,
            font=("Arial", 12),
            height=30,
            width=100
        )
        logout_button.pack(pady=5)
# 🍕 Online Food Ordering System

A desktop-based food ordering application built with Python and CustomTkinter, developed as an academic group project. The system supports multiple user roles — customers, restaurant owners, and admins — each with their own dedicated dashboard.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Team](#team)

---

## Overview

The Online Food Ordering System is a GUI desktop application that simulates a food delivery platform. Users can browse restaurants, place orders, and track deliveries. Restaurant owners can manage their menus, and admins have full control over the platform.

---

## Features

### Customer
- Register and log in securely (bcrypt password hashing)
- Browse restaurants by cuisine
- Place and track orders
- View order history

### Restaurant Owner
- Manage restaurant profile
- Add, edit, and remove menu items
- View incoming orders

### Admin
- Manage all users, restaurants, and orders
- View platform-wide statistics

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.x |
| GUI Framework | CustomTkinter |
| Database | MySQL |
| DB Connector | mysql-connector-python |
| Auth | bcrypt |
| Image Handling | Pillow (PIL) |

---

## Database Schema

The application uses the following MySQL tables:

- **User** — stores all users (customers, restaurant owners, admins)
- **Restaurant** — restaurant profiles
- **RestaurantOwner** — links users to their restaurants
- **Menu** — menu items per restaurant
- **Order** — customer orders
- **OrderItem** — line items within each order
- **Delivery** — delivery assignments and status

Tables are auto-created on first run via `main.py`.

---

## Project Structure

```
online-food-ordering-system/
│
├── main.py               # App entry point; creates DB tables and launches GUI
├── config.py             # App configuration (DB credentials, theme settings)
├── utils.py              # DB connection and query helpers
│
├── custom/               # UI modules per role
│   ├── auth.py           # Login & registration windows
│   ├── admin_dashboard.py
│   ├── restaurant_dashboard.py
│   └── user_dashboard.py
│
└── static/
    └── images/           # App icons and background images
```

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL Server

### 1. Clone the repository
```bash
git clone https://github.com/your-username/online-food-ordering-system.git
cd online-food-ordering-system
```

### 2. Install dependencies
```bash
pip install customtkinter mysql-connector-python bcrypt Pillow
```

### 3. Configure the database
Copy `.env.example` to `.env` and fill in your MySQL credentials (see [Configuration](#configuration)).

### 4. Run the app
```bash
python main.py
```

The app will auto-create all required tables and seed sample data on first launch.

---

## Configuration

Create a `.env` file in the root directory (never commit this file):

```
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=food_ordering_db
```

Then update `config.py` to read from environment variables:

```python
import os

class Config:
    db_host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "food_ordering_db")
```

> ⚠️ **Never hardcode credentials.** Add `.env` to your `.gitignore`.

---

## Usage

### Default Sample Accounts (seeded on first run)

| Role | Email | Password |
|------|-------|----------|
| Customer | john@example.com | Password123! |
| Admin | admin@example.com | Password123! |
| Restaurant Owner | restaurant@example.com | Password123! |

---

## Team

Developed by **Group 6** as part of BIS 698W coursework.

---

## License

This project is for academic purposes only.

# Faculty Leave Management System

## Setup Instructions

1. Install PostgreSQL if not already installed:
   - Download from: https://www.postgresql.org/download/
   - During installation, set a password for the 'postgres' user

2. Create the database:
   - Open PostgreSQL command prompt or pgAdmin
   - Create a new database named 'faculty_leave_db':
   ```sql
   CREATE DATABASE faculty_leave_db;
   ```

3. Update database connection:
   - Open `app.py`
   - Modify the `SQLALCHEMY_DATABASE_URI` with your PostgreSQL password:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:your_password@localhost/faculty_leave_db'
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application:
   - Open browser and go to: http://localhost:5000

## Features

- User Registration and Login
- Leave Application Submission
- Leave Status Tracking
- Admin Dashboard for Leave Management

## Color Scheme

- Primary: #2b6777
- Secondary: #52ab98
- Light Background: #c8d8e4
- White: #ffffff
- Light Gray: #f2f2f2
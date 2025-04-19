from app import app, db, User, Task, assign_tasks_rl
from datetime import datetime, timedelta
import random
import string
import json
import os

def load_passwords():
    if os.path.exists('passwords.json'):
        with open('passwords.json', 'r') as f:
            return json.load(f)
    return {}

def save_passwords(passwords):
    with open('passwords.json', 'w') as f:
        json.dump(passwords, f)

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def reset_database():
    with app.app_context():
        # Load existing passwords
        passwords = load_passwords()
        
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin_password = passwords.get('admin', 'admin123')
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin',
            experience=20,
            area_of_interest='Administration'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        print(f"Created admin user with password: {admin_password}")
        
        # Create faculty users
        faculty_data = [
            {"name": "Dr. M. Kaliappan", "email": "kaliappan@example.com", "experience": 25, "area_of_interest": "Machine Learning"},
            {"name": "Dr. P. Elamparithi", "email": "elamparithi@example.com", "experience": 15, "area_of_interest": "Data Science"},
            {"name": "Dr. S. Selva Birundha", "email": "selva@example.com", "experience": 12, "area_of_interest": "Computer Vision"},
            {"name": "Dr. R. M. Rajeswari", "email": "rajeswari@example.com", "experience": 10, "area_of_interest": "Natural Language Processing"},
            {"name": "Mrs. R. Angel Hephzibah", "email": "angel@example.com", "experience": 19, "area_of_interest": "Devops"},
            {"name": "Mrs. B. Revathi", "email": "revathi@example.com", "experience": 8, "area_of_interest": "Cybersecurity"},
            {"name": "Mrs. C. Karpagavalli", "email": "karpagavalli@example.com", "experience": 12, "area_of_interest": "Cloud Computing"},
            {"name": "Mrs. C. Usharani", "email": "usharani@example.com", "experience": 6, "area_of_interest": "Big Data Analytics"},
            {"name": "Mr. M. Ramanath", "email": "ramanath@example.com", "experience": 14, "area_of_interest": "Data Mining"},
            {"name": "Mrs. S. Jothi Lakshmi", "email": "jothi@example.com", "experience": 3, "area_of_interest": "Computer Science"},
            {"name": "Mrs. B. Sankara Lakshmi", "email": "sankara@example.com", "experience": 5, "area_of_interest": "Software Engineering"},
            {"name": "Mrs. R. Ramana", "email": "ramana@example.com", "experience": 1, "area_of_interest": "Blockchain"},
            {"name": "Mrs. M. Pradeepa", "email": "pradeepa@example.com", "experience": 1, "area_of_interest": "Computer Science"},
            {"name": "Mrs. M. Santhikala", "email": "santhikala@example.com", "experience": 5, "area_of_interest": "Data Science"},
            {"name": "Mrs. G. Kavitha", "email": "kavitha@example.com", "experience": 7, "area_of_interest": "Healthcare in AI"},
            {"name": "Mr. P. Vetrivel", "email": "vetrivel@example.com", "experience": 5, "area_of_interest": "Business Analytics"},
            {"name": "Ms. V. Logapriya", "email": "logapriya@example.com", "experience": 3, "area_of_interest": "Computer Networks"},
            {"name": "Mr. R. Muthu Eshwaran", "email": "muthu@example.com", "experience": 1, "area_of_interest": "AI Ethics"}
        ]
        
        print("\nCreating faculty users:")
        faculty_users = []
        for faculty in faculty_data:
            # Use existing password or generate new one
            faculty_password = passwords.get(faculty["email"], generate_random_password())
            passwords[faculty["email"]] = faculty_password
            
            user = User(
                email=faculty["email"],
                name=faculty["name"],
                role='faculty',
                experience=faculty["experience"],
                area_of_interest=faculty["area_of_interest"]
            )
            user.set_password(faculty_password)
            db.session.add(user)
            faculty_users.append(user)
            print(f"{faculty['name']}: {faculty_password}")
        
        # Save passwords for future use
        save_passwords(passwords)
        
        db.session.commit()
        print("\nRunning Q-learning task allocation...")
        
        # Run Q-learning for multiple episodes
        for _ in range(100):
            assign_tasks_rl()
        
        # Get final allocation
        allocation = assign_tasks_rl()
        
        # Save tasks to database
        for task_info in allocation:
            faculty = User.query.filter_by(name=task_info["Faculty"]).first()
            if faculty:
                # Set due date to 1 month from now
                due_date = datetime.utcnow() + timedelta(days=30)
                task = Task(
                    user_id=faculty.id,
                    task_name=task_info["Assigned Task"],
                    status='pending',
                    due_date=due_date,
                    priority='medium'  # Default priority
                )
                db.session.add(task)
                print(f"Assigned {task_info['Assigned Task']} to {faculty.name}")
        
        db.session.commit()
        print("\nDatabase reset successfully!")

if __name__ == '__main__':
    reset_database()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import random
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/leave_mgmt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Faculty Data
faculty_data = [
    {"Name": "Dr. M. Kaliappan", "Area of Interest": "Machine Learning", "Experience": 25},
    {"Name": "Dr. P. Elamparithi", "Area of Interest": "Data Science", "Experience": 15},
    {"Name": "Dr. S. Selva Birundha", "Area of Interest": "Computer Vision", "Experience": 12},
    {"Name": "Dr. R. M. Rajeswari", "Area of Interest": "Natural Language Processing", "Experience": 10},
    {"Name": "Mrs. R. Angel Hephzibah", "Area of Interest": "Devops", "Experience": 19},
    {"Name": "Mrs. B. Revathi", "Area of Interest": "Cybersecurity", "Experience": 8},
    {"Name": "Mrs. C. Karpagavalli", "Area of Interest": "Cloud Computing", "Experience": 12},
    {"Name": "Mrs. C. Usharani", "Area of Interest": "Big Data Analytics", "Experience": 6},
    {"Name": "Mr. M. Ramanath", "Area of Interest": "Data Mining", "Experience": 14},
    {"Name": "Mrs. S. Jothi Lakshmi", "Area of Interest": "Computer Science", "Experience": 3},
    {"Name": "Mrs. B. Sankara Lakshmi", "Area of Interest": "Software Engineering", "Experience": 5},
    {"Name": "Mrs. R. Ramana", "Area of Interest": "Blockchain", "Experience": 1},
    {"Name": "Mrs. M. Pradeepa", "Area of Interest": "Computer Science", "Experience": 1},
    {"Name": "Mrs. M. Santhikala", "Area of Interest": "Data Science", "Experience": 5},
    {"Name": "Mrs. G. Kavitha", "Area of Interest": "Healthcare in AI", "Experience": 7},
    {"Name": "Mr. P. Vetrivel", "Area of Interest": "Business Analytics", "Experience": 5},
    {"Name": "Ms. V. Logapriya", "Area of Interest": "Computer Networks", "Experience": 3},
    {"Name": "Mr. R. Muthu Eshwaran", "Area of Interest": "AI Ethics", "Experience": 1}
]

# Task List
tasks = [
    "Research Paper Review", "Mentoring Students", "Conducting Workshops",
    "AI Model Deployment", "Curriculum Development", "Data Annotation",
    "Lab In-charge", "Class Advisor", "Placement Coordinator", "Event Coordinator",
    "Exam Coordinator", "Project Guide", "Research Coordinator", "Industry Liaison",
    "Faculty Development Coordinator", "Student Activity Coordinator"
]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'faculty' or 'admin'
    experience = db.Column(db.Integer, nullable=True)  # Made nullable
    area_of_interest = db.Column(db.String(100), nullable=True)  # Made nullable
    leaves = db.relationship('Leave', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high

# Q-learning Parameters
alpha = 0.5  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.2  # Exploration rate

# Initialize Q-table
Q_table = {faculty["Name"]: {task: 0 for task in tasks} for faculty in faculty_data}

# Reward Function
def get_reward(faculty, task):
    if faculty["Experience"] < 5 and task == "Research Paper Review":
        return -10  # Strong negative for junior faculty doing research paper review
    elif faculty["Experience"] < 5:
        return 10 if task in ["Mentoring Students", "Lab In-charge", "Student Activity Coordinator","Class Advisor"] else -5
    elif 6 <= faculty["Experience"] <= 10 and task in ["Exam Coordinator", "Placement Coordinator","Event Coordinator"]:
        return 10  # Mid-level faculty should take leadership roles
    elif faculty["Experience"] > 15 and task in ["Research Paper Review", "AI Model Deployment", "Industry Liaison","Faculty Development Coordinator"]:
        return 10  # Senior faculty prefer research-based and leadership tasks
    else:
        return -5  # Not ideal

# Q-learning Task Allocation
def assign_tasks_rl():
    task_allocation = []
    for faculty in faculty_data:
        if random.uniform(0, 1) < epsilon:
            assigned_task = random.choice(tasks)  # Exploration
        else:
            assigned_task = max(Q_table[faculty["Name"]], key=Q_table[faculty["Name"]].get)  # Exploitation
        
        reward = get_reward(faculty, assigned_task)
        Q_table[faculty["Name"]][assigned_task] += alpha * (reward + gamma * max(Q_table[faculty["Name"]].values()) - Q_table[faculty["Name"]][assigned_task])
        
        task_allocation.append({
            "Faculty": faculty["Name"],
            "Area of Interest": faculty["Area of Interest"],
            "Assigned Task": assigned_task
        })
    return task_allocation

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Debug print
        print(f"Attempting login for email: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"User found: {user.name}")
            if user.check_password(password):
                print("Password correct, logging in...")
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('dashboard')
                return redirect(next_page)
            else:
                print("Invalid password")
        else:
            print("User not found")
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = 'faculty'  # Default role
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(email=email, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        leaves = Leave.query.all()
    else:
        leaves = Leave.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', leaves=leaves)

@app.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        leave_type = request.form.get('leave_type')
        reason = request.form.get('reason')
        
        leave = Leave(user_id=current_user.id, start_date=start_date,
                     end_date=end_date, leave_type=leave_type, reason=reason)
        db.session.add(leave)
        db.session.commit()
        
        flash('Leave application submitted successfully')
        return redirect(url_for('dashboard'))
    return render_template('apply_leave.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/task_allocation', methods=['GET', 'POST'])
@login_required
def task_allocation():
    if current_user.role == 'admin':
        if request.method == 'POST':
            # Run Q-learning for multiple episodes
            for _ in range(100):
                assign_tasks_rl()
            
            # Get final allocation
            allocation = assign_tasks_rl()
            
            # Clear existing tasks
            Task.query.delete()
            
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
            
            # Create additional tasks for each faculty member
            additional_tasks = [
                "Research Paper Writing",
                "Conference Paper Review",
                "Student Project Guidance",
                "Department Meeting",
                "Faculty Development Program",
                "Industry Collaboration",
                "Research Proposal Writing",
                "Academic Committee Work",
                "Student Evaluation",
                "Course Material Preparation"
            ]
            
            for faculty in User.query.filter_by(role='faculty').all():
                # Assign 2-3 additional tasks to each faculty
                num_tasks = random.randint(2, 3)
                selected_tasks = random.sample(additional_tasks, num_tasks)
                
                for task_name in selected_tasks:
                    # Set due date between 2 weeks to 2 months from now
                    days = random.randint(14, 60)
                    due_date = datetime.utcnow() + timedelta(days=days)
                    
                    # Random priority
                    priority = random.choice(['low', 'medium', 'high'])
                    
                    task = Task(
                        user_id=faculty.id,
                        task_name=task_name,
                        status='pending',
                        due_date=due_date,
                        priority=priority
                    )
                    db.session.add(task)
            
            db.session.commit()
            flash('Tasks have been allocated successfully')
            return redirect(url_for('task_allocation'))
        
        # Get all tasks
        tasks = Task.query.all()
        return render_template('task_allocation.html', tasks=tasks)
    else:
        # Faculty view - show only their tasks
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template('task_allocation.html', tasks=tasks)

@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.role != 'admin':
        flash('Only admin can create tasks')
        return redirect(url_for('task_allocation'))
    
    if request.method == 'POST':
        task_name = request.form.get('task_name')
        faculty_id = request.form.get('faculty_id')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        priority = request.form.get('priority')
        
        task = Task(
            user_id=faculty_id,
            task_name=task_name,
            status='pending',
            due_date=due_date,
            priority=priority
        )
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully')
        return redirect(url_for('task_allocation'))
    
    faculty = User.query.filter_by(role='faculty').all()
    return render_template('create_task.html', faculty=faculty)

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('You are not authorized to update this task')
        return redirect(url_for('task_allocation'))
    
    task.status = request.form.get('status')
    db.session.commit()
    flash('Task status updated successfully')
    return redirect(url_for('task_allocation'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
import sqlite3
from flask import Flask, abort, jsonify, render_template, request
import os
from sqlalchemy import case
from flask_login import current_user
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from enum import Enum
from datetime import date, datetime


app = Flask(__name__)
app.secret_key = "s3cr3t_k3y!@#"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Create instance folder if it doesn't exist
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
    print(f"✅ Created missing folder: {instance_path}")
else:
    print(f"✅ Folder exists: {instance_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'tasks.db')

db = SQLAlchemy(app)
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# class User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(10), default='Medium')  # High, Medium, Low
    due_date = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='To Do') # To Do, In Progress, Done
    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan')
    
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    
@app.route('/task/<int:task_id>/subtask', methods=['POST'])
@login_required
def add_subtask(task_id):
    content = request.form['content']
    conn = sqlite3.connect('instance/tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subtask (content, is_done, task_id) VALUES (?, ?, ?)", (content, 0, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Routes
@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form.get("task")
    priority = request.form.get('priority', 'Medium')
    due_date_str = request.form.get('due_date')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
    

    if task_content:
        new_task = Task(content=task_content, priority=priority, due_date=due_date, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!")
    
    return redirect(url_for("index"))

@app.route('/subtask/<int:subtask_id>/toggle', methods=['POST'])
@login_required
def toggle_subtask(subtask_id):
    conn = sqlite3.connect('instance/tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_done FROM subtask WHERE id = ?", (subtask_id,))
    current = cursor.fetchone()
    if current:
        new_value = 0 if current[0] else 1
        cursor.execute("UPDATE subtask SET is_done = ? WHERE id = ?", (new_value, subtask_id))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    date_str = request.args.get('date')
    filter_status = request.args.get('status')
    #tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    #today = datetime.utcnow().date()
    today = date.today()
    selected_date = date_str if date_str else ''
    base_query = Task.query.filter_by(user_id=current_user.id)
    if date_str:
        try:
            selected = datetime.strptime(date_str,'%Y-%m-%d').date()
            base_query = base_query.filter(Task.due_date == selected)
        except ValueError:
            pass
    if filter_status:
        query = query.filter(Task.status == filter_status)
# Ordiring Logic
    priority_order = case(
        (Task.priority == 'High', 1),
        (Task.priority == 'Medium', 2),
        (Task.priority == 'Low', 3),
        else_=4
    )
    # Fetch tasks grouped by status
    tasks_to_do = base_query.filter(Task.status == 'To Do').order_by(priority_order)
    tasks_in_progress = base_query.filter(Task.status == 'In Progress').order_by(priority_order)
    tasks_done = base_query.filter(Task.status == 'Done').order_by(priority_order)
    #tasks = query.order_by(priority_order, Task.due_date).all()   

    
    return render_template('index.html', tasks_to_do=tasks_to_do,tasks_in_progress= tasks_in_progress,tasks_done= tasks_done, today=today, selected_date=selected_date)

@app.route('/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_status(task_id):
    new_status = request.form.get('status')
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    task.status = new_status
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    # 🛡️ Only allow if the task belongs to the current user
    if task.user_id != current_user.id:
        flash("You are not authorized to edit this task.", "danger")
        return redirect(url_for('index'))
    
    if request.method == "POST":
        new_content = request.form.get("content")
        if not new_content:
            return abort(400, description="Task content cannot be empty")
        
        task.content = new_content
        task.status = request.form['status']
        task.priority = request.form['priority']
        db.session.commit()
        return redirect(url_for("index"))
    
    return render_template("edit.html", task=task)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database and tables created!")
    app.run(debug=True)
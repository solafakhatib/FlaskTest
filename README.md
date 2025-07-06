# 📝 Flask Task Manager

A simple and clean task manager built with **Python**, **Flask**, **Bootstrap**, and **SQLite**.  
Create, edit, and delete personal tasks — with user authentication.

---

## 🚀 Features

- 🧑‍💼 User registration and login (Flask-Login)
- ✅ Add / update / delete your own tasks
- 📦 SQLite database with SQLAlchemy ORM
- 🎨 Responsive UI with Bootstrap 5
- 🔒 Password hashing with Werkzeug
- 🌐 Session management
- 💡 Flash messages for actions
- 🖼️ Icon support using Bootstrap Icons

---

## 🖼️ Screenshot

![Task Manager UI](static/demo.png) <!-- Optional: Replace with your own screenshot -->

---

## 📁 Folder Structure
flask-m/
│
├── static/
│ └── style.css
│
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ └── edit.html
│
├── instance
│ ├── tasks.db # SQLite database
├── app.py # Main application
├── README.md
└── requirements.txt # still want to do it 
## 🧰 Technologies Used

- Python 3.11+
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5
- Bootstrap Icons

---

## ⚙️ Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/flask-task-manager.git
cd flask-task-manager
# Employee Leave Management System

A complete full-stack **Employee Leave Management** web application built with **Python (Flask)** and **MySQL**.

Track leave requests, manage leave balances, view holiday calendar, and get a beautiful dashboard overview.

---

## Features

- User Registration & Login
- Dashboard with leave stats, apply form, calendar & recent requests
- Apply for Leave (with balance validation)
- My Leave Requests (filter by status)
- Leave Balance tracking per leave type
- Holiday Calendar
- Settings page
- Clean modern UI matching professional design
- Demo account pre-seeded

---

## Tech Stack

| Layer     | Technology          |
|-----------|---------------------|
| Backend   | Python 3 + Flask    |
| Database  | MySQL               |
| Frontend  | Bootstrap 5 + Custom CSS |
| Auth      | Flask-Login         |
| Forms     | Flask-WTF           |

---

## Demo Login

| Field    | Value         |
|----------|---------------|
| Username | `ishaan`      |
| Password | `password123` |

---

## Setup Instructions

### 1. Clone & enter project

```bash
git clone <your-repo-url>
cd employee-leave-management
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create MySQL database

```sql
CREATE DATABASE leave_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'leave_user'@'localhost' IDENTIFIED BY 'leave_pass';
GRANT ALL PRIVILEGES ON leave_management.* TO 'leave_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure environment

```bash
cp .env.example .env
# Edit if needed
```

### 6. Run the app

```bash
python run.py
```

Open **http://127.0.0.1:5000**

---

## Project Structure

```
employee-leave-management/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── routes.py
│   ├── seed.py
│   ├── templates/
│   └── static/css/
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Learn Full Stack Development

Want to build projects like this?

- [Full Stack Development Training Course in Noida](https://uncodemy.com/course/full-stack-development-training-course-in-noida)
- [Full Stack Development Training Course in Delhi](https://uncodemy.com/course/full-stack-development-training-course-in-delhi)

---

## License

MIT License

from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='employee')  # employee / admin
    department = db.Column(db.String(80), default='General')
    join_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    leave_balances = db.relationship('LeaveBalance', backref='employee', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.full_name}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LeaveType(db.Model):
    __tablename__ = 'leave_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    max_days = db.Column(db.Integer, default=0)
    color = db.Column(db.String(20), default='#0d6efd')
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

    requests = db.relationship('LeaveRequest', backref='leave_type', lazy='dynamic')
    balances = db.relationship('LeaveBalance', backref='leave_type', lazy='dynamic')

    def __repr__(self):
        return f'<LeaveType {self.name}>'


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_on = db.Column(db.DateTime)
    reviewer_note = db.Column(db.Text)

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def __repr__(self):
        return f'<LeaveRequest {self.id} - {self.status}>'


class LeaveBalance(db.Model):
    __tablename__ = 'leave_balances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    total_days = db.Column(db.Integer, default=0)
    used_days = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'leave_type_id', 'year', name='unique_balance'),
    )

    @property
    def remaining(self):
        return max(0, self.total_days - self.used_days)

    def __repr__(self):
        return f'<LeaveBalance {self.user_id}-{self.leave_type_id}>'


class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.String(200))
    is_optional = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Holiday {self.name} on {self.date}>'

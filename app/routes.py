from datetime import datetime, date, timedelta
from calendar import monthcalendar, month_name
from collections import defaultdict

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import extract, or_

from app import db
from app.models import User, LeaveType, LeaveRequest, LeaveBalance, Holiday
from app.forms import RegistrationForm, LoginForm, LeaveRequestForm

main = Blueprint('main', __name__)


def get_user_stats(user):
    year = date.today().year
    balances = LeaveBalance.query.filter_by(user_id=user.id, year=year).all()
    total = sum(b.total_days for b in balances)
    used = sum(b.used_days for b in balances)
    remaining = total - used

    # Upcoming holidays next 30 days
    today = date.today()
    upcoming = Holiday.query.filter(
        Holiday.date >= today,
        Holiday.date <= today + timedelta(days=30)
    ).count()

    return {
        'total': total,
        'used': used,
        'remaining': remaining,
        'upcoming_holidays': upcoming
    }


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role='employee'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Create leave balances
        year = date.today().year
        for lt in LeaveType.query.all():
            db.session.add(LeaveBalance(
                user_id=user.id,
                leave_type_id=lt.id,
                total_days=lt.max_days,
                used_days=0,
                year=year
            ))
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    stats = get_user_stats(current_user)
    form = LeaveRequestForm()
    form.leave_type_id.choices = [
        (lt.id, lt.name) for lt in LeaveType.query.filter_by(is_active=True).all()
    ]

    # Recent leave requests
    recent = LeaveRequest.query.filter_by(user_id=current_user.id)\
        .order_by(LeaveRequest.applied_on.desc()).limit(5).all()

    # Leave balances
    year = date.today().year
    balances = LeaveBalance.query.filter_by(user_id=current_user.id, year=year).all()

    # Calendar data for current month
    today = date.today()
    year_cal, month_cal = today.year, today.month
    if request.args.get('month') and request.args.get('year'):
        try:
            month_cal = int(request.args.get('month'))
            year_cal = int(request.args.get('year'))
        except:
            pass

    cal = monthcalendar(year_cal, month_cal)
    month_name_str = month_name[month_cal]

    # Get leave requests for this month for coloring
    month_requests = LeaveRequest.query.filter(
        LeaveRequest.user_id == current_user.id,
        extract('year', LeaveRequest.start_date) == year_cal,
        extract('month', LeaveRequest.start_date) == month_cal
    ).all()

    # Holidays this month
    holidays = Holiday.query.filter(
        extract('year', Holiday.date) == year_cal,
        extract('month', Holiday.date) == month_cal
    ).all()

    # Build day status map
    day_status = {}  # day -> list of statuses
    for req in month_requests:
        d = req.start_date
        while d <= req.end_date:
            if d.month == month_cal and d.year == year_cal:
                day_status.setdefault(d.day, []).append(req.status)
            d += timedelta(days=1)
    for h in holidays:
        day_status.setdefault(h.date.day, []).append('Holiday')

    return render_template(
        'dashboard.html',
        stats=stats,
        form=form,
        recent=recent,
        balances=balances,
        cal=cal,
        month_name=month_name_str,
        year=year_cal,
        month=month_cal,
        day_status=day_status,
        today=today
    )


@main.route('/apply-leave', methods=['POST'])
@login_required
def apply_leave():
    form = LeaveRequestForm()
    form.leave_type_id.choices = [
        (lt.id, lt.name) for lt in LeaveType.query.filter_by(is_active=True).all()
    ]
    if form.validate_on_submit():
        # Check balance
        year = date.today().year
        balance = LeaveBalance.query.filter_by(
            user_id=current_user.id,
            leave_type_id=form.leave_type_id.data,
            year=year
        ).first()

        days = (form.end_date.data - form.start_date.data).days + 1
        if balance and balance.remaining < days:
            flash(f'Insufficient leave balance. You have only {balance.remaining} days remaining.', 'danger')
            return redirect(url_for('main.dashboard'))

        req = LeaveRequest(
            user_id=current_user.id,
            leave_type_id=form.leave_type_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            status='Pending'
        )
        db.session.add(req)
        db.session.commit()
        flash('Leave request submitted successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f'{field}: {e}', 'danger')
    return redirect(url_for('main.dashboard'))


@main.route('/my-requests')
@login_required
def my_requests():
    status_filter = request.args.get('status', '')
    query = LeaveRequest.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests = query.order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('my_requests.html', requests=requests, status_filter=status_filter)


@main.route('/leave-balance')
@login_required
def leave_balance():
    year = date.today().year
    balances = LeaveBalance.query.filter_by(user_id=current_user.id, year=year).all()
    stats = get_user_stats(current_user)
    return render_template('leave_balance.html', balances=balances, stats=stats, year=year)


@main.route('/holiday-calendar')
@login_required
def holiday_calendar():
    year = request.args.get('year', date.today().year, type=int)
    holidays = Holiday.query.filter(
        extract('year', Holiday.date) == year
    ).order_by(Holiday.date).all()
    return render_template('holiday_calendar.html', holidays=holidays, year=year)


@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

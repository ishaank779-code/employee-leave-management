from datetime import date
from app import db
from app.models import User, LeaveType, LeaveBalance, Holiday


def seed_data():
    # Leave Types
    if LeaveType.query.count() == 0:
        types = [
            {'name': 'Casual Leave', 'max_days': 8, 'color': '#0d6efd', 'description': 'For personal work'},
            {'name': 'Sick Leave', 'max_days': 6, 'color': '#198754', 'description': 'For medical reasons'},
            {'name': 'Earned Leave', 'max_days': 10, 'color': '#6f42c1', 'description': 'Accumulated leave'},
            {'name': 'Maternity Leave', 'max_days': 3, 'color': '#d63384', 'description': 'Maternity related'},
        ]
        for t in types:
            db.session.add(LeaveType(**t))
        db.session.commit()

    # Demo user - Ishaan Khan
    if not User.query.filter_by(username='ishaan').first():
        user = User(
            username='ishaan',
            email='ishaankhan@example.com',
            full_name='Ishaan Khan',
            role='employee',
            department='Engineering'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Assign leave balances for current year
        year = date.today().year
        for lt in LeaveType.query.all():
            balance = LeaveBalance(
                user_id=user.id,
                leave_type_id=lt.id,
                total_days=lt.max_days,
                used_days=0,
                year=year
            )
            # Pre-fill some used days to match screenshot style
            if lt.name == 'Casual Leave':
                balance.used_days = 2
            elif lt.name == 'Sick Leave':
                balance.used_days = 2
            elif lt.name == 'Earned Leave':
                balance.used_days = 4
            db.session.add(balance)
        db.session.commit()

    # Sample Holidays for 2026
    if Holiday.query.count() == 0:
        holidays = [
            {'name': 'Republic Day', 'date': date(2026, 1, 26)},
            {'name': 'Holi', 'date': date(2026, 3, 14)},
            {'name': 'Good Friday', 'date': date(2026, 4, 3)},
            {'name': 'Independence Day', 'date': date(2026, 8, 15)},
            {'name': 'Gandhi Jayanti', 'date': date(2026, 10, 2)},
            {'name': 'Diwali', 'date': date(2026, 11, 8)},
            {'name': 'Christmas', 'date': date(2026, 12, 25)},
            {'name': 'New Year', 'date': date(2026, 1, 1)},
            # October 2026 sample holidays matching calendar
            {'name': 'Dussehra', 'date': date(2026, 10, 20)},
            {'name': 'Diwali Eve', 'date': date(2026, 10, 27)},
        ]
        for h in holidays:
            db.session.add(Holiday(**h))
        db.session.commit()

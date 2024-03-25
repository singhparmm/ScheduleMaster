from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json


from datetime import datetime, timedelta
import calendar
from calendar import monthrange, day_name
from flask import request
from dateutil.relativedelta import relativedelta




views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

# New view routes


@views.route('/day-detail')
@login_required
def day_detail():
    date_str = request.args.get('date')
    # Use date_str directly since it's already in the correct format
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    notes = Note.query.filter_by(date=date, user_id=current_user.id).all()
    return render_template("day_detail.html", date=date_str, notes=notes)


@views.route('/weekly')
@login_required
def weekly_view():
    today = datetime.now()
    offset = request.args.get('offset', default=0, type=int)
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    
    dates_with_days = [
    ((start_of_week + timedelta(days=i)).strftime("%A"),
     (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
    for i in range(7)
    ]    

    next_week_offset = offset + 1
    prev_week_offset = offset - 1
    
    return render_template("week_view.html", user=current_user, dates_with_days=dates_with_days, next_week_offset=next_week_offset, prev_week_offset=prev_week_offset)


@views.route('/monthly')
@login_required
def monthly_view():
    offset = request.args.get('offset', default=0, type=int)
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    target_month = first_day_of_current_month + relativedelta(months=offset)
    days_in_month = monthrange(target_month.year, target_month.month)[1]

    # Calculate placeholders for the beginning of the month
    placeholders_before = (target_month.weekday() + 1) % 7
    days = [''] * placeholders_before

    # Add actual days of the month with full date strings
    for day in range(1, days_in_month + 1):
        full_date = datetime(target_month.year, target_month.month, day).strftime('%Y-%m-%d')
        days.append(full_date)  # Append the full date string instead of just the day

    # Add placeholders to the end if necessary to complete the grid
    placeholders_after = 7 - ((len(days) % 7) or 7)
    days.extend([''] * placeholders_after)

    return render_template("month_view.html", days=days, current_month=target_month.strftime("%B"), current_year=target_month.year, next_month_offset=offset + 1, prev_month_offset=offset - 1)



@views.route('/yearly')
@login_required
def yearly_view():
    today = datetime.now()
    current_year = today.year
    # Generate a list of months with their relative offsets from the current month
    months_with_offsets = []
    for i in range(1, 13):
        month_date = datetime(current_year, i, 1)
        offset = (month_date.year - today.year) * 12 + month_date.month - today.month
        months_with_offsets.append((month_date.strftime("%B"), offset))
    
    return render_template("year_view.html", user=current_user, year=current_year, months_with_offsets=months_with_offsets)



@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})